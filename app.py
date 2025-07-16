from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QApplication,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QPushButton,
    QListWidget,
    QSpacerItem,
    QSizePolicy,
    QStackedWidget,
    QHBoxLayout,
    QFrame,
)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QObject
from PyQt5.QtGui import (
    QPainter,
    QColor,
    QPen,
    QPainterPath,
    QPaintEvent,
    QMouseEvent,
    QResizeEvent,
    QCursor,
    QFont,
)
from topic_card import TopicsScrollArea
import sys
import random
from generator import WordSearchGenerator
import sqlite3


class DbManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.con = sqlite3.connect("wordsearch.db")
        self.con.row_factory = sqlite3.Row

    def get_topics(self):
        c = self.con.cursor()
        c.execute("SELECT * FROM topics")
        return c.fetchall()

    def get_words(self, topic_id):
        c = self.con.cursor()
        c.execute("SELECT * FROM words WHERE topic_id=?", (topic_id,))
        words = [row["word"] for row in c.fetchall()]
        return words

    def close(self):
        self.con.close()


class LetterTile(QLabel):
    def __init__(self, letter, row, col, parent=None):
        super().__init__(letter, parent)
        self.row = row
        self.col = col
        self.letter = letter
        self.setFixedSize(60, 60)
        self.setAlignment(Qt.AlignCenter)
        self.locked_highlight = False
        self.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid lightgray;
                font: 800 24px 'Arial';
            }
        """)

        self.setCursor(QCursor(Qt.PointingHandCursor))

    def redraw_text(self):
        self.locked_highlight = True
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.locked_highlight:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(Qt.NoPen)
            # Redraw the letter clearly on top
            painter.setPen(Qt.black)
            font = QFont("Arial", 15, QFont.Bold)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, self.letter)


class PathOverlay(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.active_path = []
        self.active_color = QColor(100, 150, 255, 180)
        self.locked_paths = []  # List of (points, color)
        self.setMouseTracking(True)

    def updatePath(self, points, color: QColor = None):
        self.active_path = points
        if color:
            self.active_color = color
        self.update()

    def cleanPath(self):
        self.active_path = []
        self.locked_paths = []
        self.update()

    def lockCurrentPath(self, color=None):
        if len(self.active_path) < 2:
            return
        if self.checkPaths(self.active_path):
            return
        path_color = color or self.active_color
        self.locked_paths.append((list(self.active_path), path_color))
        self.active_path = []
        self.update()

    def checkPaths(self, path_to_check):
        check_coords = tuple((pt.x(), pt.y()) for pt in path_to_check)
        for path_points, _ in self.locked_paths:
            locked_coords = tuple((pt.x(), pt.y()) for pt in path_points)
            if locked_coords == check_coords:
                return True
        return False

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw locked paths with their own color
        for path_points, path_color in self.locked_paths:
            if len(path_points) >= 2:
                pen = QPen(path_color, 35, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painter.setPen(pen)
                path = QPainterPath()
                path.moveTo(path_points[0])
                for pt in path_points[1:]:
                    path.lineTo(pt)
                painter.drawPath(path)

        # Draw active path
        if len(self.active_path) >= 2:
            if self.checkPaths(self.active_path):
                return
            pen = QPen(self.active_color, 35, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            path = QPainterPath()
            path.moveTo(self.active_path[0])
            for pt in self.active_path[1:]:
                path.lineTo(pt)
            painter.drawPath(path)


class WordSearchWidget(QWidget):
    wordFound = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid = []
        self.rows = 0
        self.cols = 0
        self.tiles: list[list[LetterTile]] = []
        self.selection = []
        self.start_tile = None
        self.dragging = False
        self.word_list = []
        self.highlight_colors = [
            QColor(244, 67, 54, 70),  # Red
            QColor(255, 152, 0, 70),  # Orange
            QColor(255, 235, 59, 70),  # Yellow
            QColor(76, 175, 80, 70),  # Green
            QColor(0, 188, 212, 70),  # Cyan
            QColor(33, 150, 243, 70),  # Blue
            QColor(156, 39, 176, 70),  # Purple
            QColor(255, 87, 34, 70),  # Deep Orange
            QColor(121, 85, 72, 70),  # Brown
            QColor(96, 125, 139, 70),  # Blue Gray
        ]
        self.main_layout = QGridLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.main_layout)

        self.overlay = PathOverlay(self)
        self.overlay.raise_()

    def update_wordsearch(self, data: dict):
        self.clear_tiles()
        self.tiles.clear()
        # 2) Clear any active selection/path
        self.clearSelection()
        self.overlay.cleanPath()
        self.grid = data.get("grid", [])
        self.word_list = data.get("words", [])
        self.rows = len(self.grid)
        self.cols = len(self.grid[0]) if self.rows > 0 else 0
        self.setFixedSize(self.cols * 60, self.rows * 60)
        for r in range(self.rows):
            row_tiles = []
            for c in range(self.cols):
                tile = LetterTile(self.grid[r][c], r, c)
                self.main_layout.addWidget(tile, r, c)
                row_tiles.append(tile)
            self.tiles.append(row_tiles)

        self.overlay.resize(self.size())
        self.overlay.raise_()

        # 7) Trigger a repaint (so the overlay and tiles draw immediately)
        self.update()

    def clear_tiles(self):
        for row in self.tiles:
            for tile in row:
                self.main_layout.removeWidget(tile)
                tile.deleteLater()

    def resizeEvent(self, event: QResizeEvent):
        self.overlay.resize(self.size())

    def mousePressEvent(self, event: QMouseEvent):
        tile = self.tileAt(event.pos())
        if tile:
            self.clearSelection()
            self.start_tile = tile
            self.dragging = True
            self.updateSelectionPathTo(tile)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging and self.start_tile:
            tile = self.tileAt(event.pos())
            if tile:
                self.updateSelectionPathTo(tile)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False
        word = "".join(tile.text() for tile in self.selection)
        if word in self.word_list:
            color = random.choice(self.highlight_colors)
            self.overlay.lockCurrentPath(color)  # <-- LOCK IT IN
            # self.draw_texts()
            self.wordFound.emit(word)
        else:
            self.overlay.updatePath([])  # clear selection path

    def draw_texts(self):
        for tile in self.selection:
            tile.redraw_text()

    def tileAt(self, pos: QPoint):
        for row in self.tiles:
            for tile in row:
                local_pos = tile.mapFromParent(pos)
                if tile.rect().contains(local_pos):
                    return tile
        return None

    def clearSelection(self):
        self.selection.clear()
        self.overlay.updatePath([])

    def updateSelectionPathTo(self, end_tile: LetterTile):
        if not self.start_tile:
            return

        r1, c1 = self.start_tile.row, self.start_tile.col
        r2, c2 = end_tile.row, end_tile.col
        dr = r2 - r1
        dc = c2 - c1

        # Determine if direction is valid (horizontal, vertical, diagonal)
        if dr == 0 and dc == 0:
            path = [self.start_tile]
        elif dr == 0:  # Horizontal
            step = 1 if dc > 0 else -1
            path = [self.tiles[r1][c] for c in range(c1, c2 + step, step)]
        elif dc == 0:  # Vertical
            step = 1 if dr > 0 else -1
            path = [self.tiles[r][c1] for r in range(r1, r2 + step, step)]
        elif abs(dr) == abs(dc):  # Diagonal
            step_r = 1 if dr > 0 else -1
            step_c = 1 if dc > 0 else -1
            path = [
                self.tiles[r1 + i * step_r][c1 + i * step_c] for i in range(abs(dr) + 1)
            ]
        else:
            return  # Invalid direction

        self.selection = path
        self.updateOverlay()

    def updateOverlay(self):
        path_points = [
            tile.mapTo(self, tile.rect().center()) for tile in self.selection
        ]
        self.overlay.updatePath(path_points)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DbManager(self)
        self.setWindowTitle("Word Search Game")
        self.setMinimumSize(800, 600)

        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        self.menu_screen = self.create_menu_screen()
        self.game_screen = self.create_game_screen()

        self.stacked.addWidget(self.menu_screen)
        self.stacked.addWidget(self.game_screen)
        self.wordsearch_generator = WordSearchGenerator()
        self.state = {}

    def create_menu_screen(self):
        topics = self.db_manager.get_topics()
        container = TopicsScrollArea(topics, self)
        container.card_clicked.connect(self.start_game)
        layout = QVBoxLayout()
        layout.addStretch()
        container.setLayout(layout)
        return container

    def create_game_screen(self):
        widget = QWidget()
        main_layout = QVBoxLayout()

        # Top bar
        top_bar = QHBoxLayout()
        self.back_button = QPushButton("Back to Menu")
        self.back_button.clicked.connect(self.go_to_menu)
        self.topic_label = QLabel("Topic: Sports")
        self.topic_label.setAlignment(Qt.AlignCenter)

        top_bar.addWidget(self.back_button)
        top_bar.addStretch()
        top_bar.addWidget(self.topic_label)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        # Center area
        center_layout = QHBoxLayout()
        center_layout.setStretch(1, 0)
        wordsearch_frame = QFrame()
        wordsearch_frame.setMinimumWidth(600)
        wordsearch_layout = QVBoxLayout(wordsearch_frame)

        self.word_search_widget = WordSearchWidget()
        wordsearch_layout.addWidget(self.word_search_widget, alignment=Qt.AlignCenter)
        self.word_search_widget.wordFound.connect(self.on_word_found)

        # Word list and side panel
        side_panel = QVBoxLayout()
        side_panel.addWidget(QLabel("Words to Find:"))
        self.word_list_widget = QListWidget()
        self.word_list_widget.setMaximumWidth(200)
        side_panel.addWidget(self.word_list_widget)
        side_panel.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding)
        )

        self.progress_label = QLabel("Words Found: 0 / 10")
        self.give_up_button = QPushButton("Give Up")

        side_panel.addWidget(self.progress_label)
        side_panel.addWidget(self.give_up_button)

        center_layout.addWidget(wordsearch_frame)
        center_layout.addLayout(side_panel)
        center_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        main_layout.addLayout(center_layout)
        widget.setLayout(main_layout)

        return widget

    def start_game(self, topic):
        self.topic_label.setText(f"Topic: {topic}")
        self.word_list_widget.clear()
        # Example: simulate loading words
        words = self.db_manager.get_words(topic)
        words = self.wordsearch_generator.clean_words(words)
        for word in words:
            self.word_list_widget.addItem(word)
            self.state[word] = False
        wordsearch_data = self.wordsearch_generator.generate(
            words=words, auto_dimensions=True, directions=["down", "diagonal_up_left"]
        )
        self.word_search_widget.update_wordsearch(wordsearch_data)
        self.progress_label.setText(f"Words Found: 0 / {len(words)}")
        self.stacked.setCurrentWidget(self.game_screen)

    def on_word_found(self, word):
        self.state[word] = True
        self.progress_label.setText(
            f"Words Found: {len([word for word in self.state if self.state[word]])} / {len(self.word_list_widget)}"
        )
        items = self.word_list_widget.findItems(word, Qt.MatchExactly)
        if not items:
            return
        item = items[0]
        font = item.font()
        font.setBold(True)
        font.setStrikeOut(True)
        item.setFont(font)

    def go_to_menu(self):
        self.stacked.setCurrentWidget(self.menu_screen)

    def closeEvent(self, a0):
        self.db_manager.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(open("style.qss", "r").read())
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
