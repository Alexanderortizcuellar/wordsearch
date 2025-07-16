import sys
import sqlite3
import base64
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLineEdit,
    QLabel,
    QFileDialog,
    QMessageBox,
    QInputDialog,
    QTextEdit,
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, Qt, QBuffer, QByteArray, QUrl, pyqtSignal, QObject
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
import json
import dotenv

DB_FILE = "wordsearch.db"
MAX_ICON_SIZE = 64  # pixels
TOKEN: str = dotenv.get_key(".env", "AI_TOKEN")


class DatabaseManager:
    def __init__(self, db_file=DB_FILE):
        self.conn = sqlite3.connect(db_file)
        self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                image_base64 TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                word TEXT NOT NULL,
                FOREIGN KEY(topic_id) REFERENCES topics(id)
            )
        """)
        self.conn.commit()

    def get_topics(self):
        c = self.conn.cursor()
        c.execute("SELECT id, name, image_base64 FROM topics ORDER BY name")
        return c.fetchall()

    def add_topic(self, name, image_b64):
        try:
            c = self.conn.cursor()
            c.execute(
                "INSERT INTO topics (name, image_base64) VALUES (?, ?)",
                (name, image_b64),
            )
            self.conn.commit()
            return c.lastrowid
        except sqlite3.IntegrityError:
            return None

    def update_topic(self, topic_id, name, image_b64):
        c = self.conn.cursor()
        c.execute(
            "UPDATE topics SET name=?, image_base64=? WHERE id=?",
            (name, image_b64, topic_id),
        )
        self.conn.commit()

    def delete_topic(self, topic_id):
        c = self.conn.cursor()
        c.execute("DELETE FROM words WHERE topic_id=?", (topic_id,))
        c.execute("DELETE FROM topics WHERE id=?", (topic_id,))
        self.conn.commit()

    def get_words(self, topic_id):
        c = self.conn.cursor()
        c.execute(
            "SELECT id, word FROM words WHERE topic_id=? ORDER BY word", (topic_id,)
        )
        return c.fetchall()

    def add_word(self, topic_id, word):
        c = self.conn.cursor()
        c.execute("INSERT INTO words (topic_id, word) VALUES (?, ?)", (topic_id, word))
        self.conn.commit()
        return c.lastrowid

    def update_word(self, word_id, word):
        c = self.conn.cursor()
        c.execute("UPDATE words SET word=? WHERE id=?", (word, word_id))
        self.conn.commit()

    def delete_word(self, word_id):
        c = self.conn.cursor()
        c.execute("DELETE FROM words WHERE id=?", (word_id,))
        self.conn.commit()


# Helper to load and resize image, return base64 string
def encode_image_to_base64(path: str) -> str:
    pix = QPixmap(path)
    if pix.isNull():
        return ""
    # scale keeping aspect ratio
    pix = pix.scaled(
        MAX_ICON_SIZE, MAX_ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation
    )
    buffer = QBuffer()
    buffer.open(QBuffer.WriteOnly)
    pix.save(buffer, "PNG")
    b = bytes(buffer.data())
    return base64.b64encode(b).decode("ascii")


# Helper to decode base64 string to QIcon
def icon_from_base64(b64: str) -> QIcon:
    if not b64:
        return QIcon()
    b = base64.b64decode(b64)
    pix = QPixmap()
    pix.loadFromData(QByteArray(b))
    return QIcon(pix)


class AIRequester(QObject):
    """
    Handles communication with AI service via HTTP POST.
    Emits aiResponse with raw response text.
    """

    aiResponse = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self._on_reply)

    def request(self, prompt: str):
        url = QUrl(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        )  # replace with real endpoint
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": TOKEN,
        }
        req = QNetworkRequest(url)
        for k, v in headers.items():
            req.setRawHeader(k.encode("utf-8"), v.encode("utf-8"))
        body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
        self.network_manager.post(req, QByteArray(body))

    def _on_reply(self, reply: QNetworkReply):
        if reply.error():
            # propagate error message
            self.aiResponse.emit(json.dumps({"error": reply.errorString()}))
            return
        data = bytes(reply.readAll()).decode("utf-8")
        self.aiResponse.emit(data)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.ai = AIRequester(self)
        self.ai.aiResponse.connect(self.on_ai_response)
        self.setWindowTitle("Topic & Word Manager")
        self.setMinimumSize(600, 400)

        cent = QWidget()
        self.setCentralWidget(cent)
        layout = QHBoxLayout(cent)

        # Topics list
        left = QVBoxLayout()
        layout.addLayout(left, 1)
        left.addWidget(QLabel("Topics"))
        self.topic_list = QListWidget()
        self.topic_list.setIconSize(QSize(MAX_ICON_SIZE, MAX_ICON_SIZE))
        self.topic_list.currentItemChanged.connect(self.on_topic_selected)
        left.addWidget(self.topic_list)
        btns_t = QHBoxLayout()
        for lbl, slot in [
            ("Add", self.add_topic),
            ("Edit", self.edit_topic),
            ("Delete", self.delete_topic),
        ]:
            b = QPushButton(lbl)
            b.clicked.connect(slot)
            btns_t.addWidget(b)
        left.addLayout(btns_t)

        # Words panel
        right = QVBoxLayout()
        layout.addLayout(right, 2)
        right.addWidget(QLabel("Words"))
        self.word_list = QListWidget()
        self.word_list.currentItemChanged.connect(self.on_word_selected)
        right.addWidget(self.word_list)
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Enter word")
        right.addWidget(self.word_input)
        btns_w = QHBoxLayout()
        for lbl, slot in [
            ("Add", self.add_word),
            ("Edit", self.edit_word),
            ("Delete", self.delete_word),
        ]:
            b = QPushButton(lbl)
            b.clicked.connect(slot)
            btns_w.addWidget(b)
        right.addLayout(btns_w)
        # Right panel: AI Generator
        right.addWidget(QLabel("Generate Words (AI)"))
        self.ai_text = QTextEdit()
        self.ai_text.setPlaceholderText("AI-generated words will appear here...")
        right.addWidget(self.ai_text)
        self.ai_button = QPushButton("Request Words from AI")
        # Connect this to your AI call handler
        self.ai_button.clicked.connect(self.request_ai_words)
        right.addWidget(self.ai_button)

        self.load_topics()

    def load_topics(self):
        self.topic_list.clear()
        for tid, name, img_b64 in self.db.get_topics():
            item = QListWidgetItem(name)
            icon = icon_from_base64(img_b64)
            item.setIcon(icon)
            item.setData(Qt.UserRole, (tid, name, img_b64))
            self.topic_list.addItem(item)
        self.word_list.clear()
        self.word_input.clear()

    def on_ai_response(self, response):
        try:
            response = json.loads(response)
            response.get("candidates", [])
            text = response["candidates"][0]["content"].get("parts", [])[0]["text"]
        except json.JSONDecodeError:
            response = {"error": response}
        except Exception as e:
            response = {"error": str(e)}
        if response.get("error"):
            text = response["error"]

        self.ai_text.setText(str(text))

    def request_ai_words(self):
        topic = self.topic_list.currentItem()
        if not topic:
            QMessageBox.warning(self, "Error", "Select topic")
            return

        prompt = f"I am creaing a wordsearch can you give me 15 words on topic {topic.text()} separated by commas"
        self.ai.request(prompt)

    def on_topic_selected(self, cur, prev):
        self.word_list.clear()
        self.word_input.clear()
        if cur:
            tid, name, _ = cur.data(Qt.UserRole)
            for wid, w in self.db.get_words(tid):
                it = QListWidgetItem(w)
                it.setData(Qt.UserRole, wid)
                self.word_list.addItem(it)

    def add_topic(self):
        name, ok = QInputDialog.getText(self, "New Topic", "Name:")
        if not ok or not name.strip():
            return
        path, ok2 = QFileDialog.getOpenFileName(
            self, "Select Icon", "", "Images (*.png *.jpg *.bmp)"
        )
        b64 = encode_image_to_base64(path) if ok2 else ""
        if self.db.add_topic(name.strip(), b64) is None:
            QMessageBox.warning(self, "Error", "Topic exists")
        self.load_topics()

    def edit_topic(self):
        cur = self.topic_list.currentItem()
        if not cur:
            return QMessageBox.warning(self, "Error", "Select topic")
        tid, old_name, old_b64 = cur.data(Qt.UserRole)
        name, ok = QInputDialog.getText(self, "Edit Topic", "Name:", text=old_name)
        if not ok or not name.strip():
            return
        path, ok2 = QFileDialog.getOpenFileName(
            self, "Select Icon", "", "Images (*.png *.jpg *.bmp)"
        )
        b64 = encode_image_to_base64(path) if ok2 else old_b64
        self.db.update_topic(tid, name.strip(), b64)
        self.load_topics()

    def delete_topic(self):
        cur = self.topic_list.currentItem()
        if not cur:
            return QMessageBox.warning(self, "Error", "Select topic")
        tid, name, _ = cur.data(Qt.UserRole)
        if (
            QMessageBox.question(self, "Delete", 'Delete topic "' + name + '"?')
            == QMessageBox.Yes
        ):
            self.db.delete_topic(tid)
            self.load_topics()

    def on_word_selected(self, cur, prev):
        if cur:
            self.word_input.setText(cur.text())
        else:
            self.word_input.clear()

    def add_word(self):
        cur = self.topic_list.currentItem()
        if not cur:
            return QMessageBox.warning(self, "Error", "Select topic")
        tid = cur.data(Qt.UserRole)[0]
        w = self.word_input.text().strip()
        if "," in w:
            w = [x.strip() for x in w.split(",")]
            w = [w for w in w if w]
            self.add_words(w, tid)
            self.word_input.clear()
            self.on_topic_selected(cur, None)
            return
        if not w:
            return
        self.db.add_word(tid, w)
        self.on_topic_selected(cur, None)
        self.word_input.clear()

    def add_words(self, words, tid):
        for w in words:
            self.db.add_word(tid, w)

    def edit_word(self):
        cur = self.word_list.currentItem()
        if not cur:
            return QMessageBox.warning(self, "Error", "Select word")
        wid = cur.data(Qt.UserRole)
        nw, ok = QInputDialog.getText(self, "Edit Word", "Word:", text=cur.text())
        if not ok or not nw.strip():
            return
        self.db.update_word(wid, nw.strip())
        self.on_topic_selected(self.topic_list.currentItem(), None)

    def delete_word(self):
        cur = self.word_list.currentItem()
        if not cur:
            return QMessageBox.warning(self, "Error", "Select word")
        wid = cur.data(Qt.UserRole)
        if (
            QMessageBox.question(self, "Delete", 'Delete "' + cur.text() + '"?')
            == QMessageBox.Yes
        ):
            self.db.delete_word(wid)
            self.on_topic_selected(self.topic_list.currentItem(), None)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(open("managerstyle.qss", "r").read())
    Win = MainWindow()
    Win.show()
    sys.exit(app.exec_())
