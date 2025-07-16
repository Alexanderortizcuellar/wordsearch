from PyQt5 import QtWidgets, QtGui, QtCore
import base64


class TopicCard(QtWidgets.QFrame):
    clicked = QtCore.pyqtSignal(int)

    def __init__(self, title: str, image_base64: str, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.setObjectName(f"TopicCard_{index}")
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setStyleSheet(self._default_style())
        self._setup_ui(title, image_base64)
        self._setup_animation()

    def _setup_ui(self, title, image_base64):
        # Decode base64 image
        image_data = base64.b64decode(image_base64)
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(image_data)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                64, 64, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            )
        print(f"{title}:", pixmap.size())

        # Widgets
        self.image_label = QtWidgets.QLabel()
        self.image_label.setPixmap(pixmap)
        self.image_label.setFixedSize(64, 64)

        self.title_label = QtWidgets.QLabel(title)
        font = self.title_label.font()
        font.setPointSize(12)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)

        # Layout
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(10, 10, 10, 10)
        vbox.setSpacing(8)
        vbox.addWidget(self.image_label, alignment=QtCore.Qt.AlignCenter)
        vbox.addWidget(self.title_label)

    def _setup_animation(self):
        # Shadow effect
        self.shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(0)
        self.shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.shadow)

        # Animation for shadow blur radius
        self.anim = QtCore.QPropertyAnimation(self.shadow, b"blurRadius", self)
        self.anim.setDuration(200)
        self.anim.setStartValue(0)
        self.anim.setEndValue(20)

    def enterEvent(self, event):
        # On hover, animate shadow in
        self.anim.setDirection(QtCore.QPropertyAnimation.Forward)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        # On leave, reverse animation
        self.anim.setDirection(QtCore.QPropertyAnimation.Backward)
        self.anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit(self.index)

    def _default_style(self):
        return """
        QFrame {
            background-color: #ffffff;
            border-radius: 8px;
            border: 1px solid #dddddd;
        }

        QLabel {
            color: #333333;
            border: none;
        }
        """


class TopicsScrollArea(QtWidgets.QScrollArea):
    card_clicked = QtCore.pyqtSignal(int)

    def __init__(self, topics: list, parent=None):
        super().__init__(parent)
        self.topics = topics
        self._init_ui()

    def _init_ui(self):
        self.container = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout(self.container)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.grid.setSpacing(15)
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.update_topics(self.topics)

    def update_topics(self, topics: list):
        # Clear existing widgets
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Re-populate with new topics
        for i, topic in enumerate(topics):
            card = TopicCard(topic["name"], topic["image_base64"], index=topic["id"])
            card.clicked.connect(self.card_clicked.emit)
            self.grid.addWidget(card, i // 4, i % 4)

        self.topics = topics


# Example usage:
# topics = [{'title': 'Animals', 'image': '<base64>'}, ...]
# scroll_area = TopicsScrollArea(topics)
# main_layout.addWidget(scroll_area)
# Later, to refresh:
# scroll_area.update_topics(new_topics)
