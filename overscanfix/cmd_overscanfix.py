import signal

from PyQt5.QtWidgets import QApplication, QWidget, QAction
from PyQt5.QtGui import QPainter, QBrush, QFont, QKeySequence
from PyQt5.QtCore import Qt, QRect, QMargins


class MainWindow(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Rectangle")
        # self.setGeometry(100, 100, 300, 300)
        self._rect: QRect = QRect(100, 100, 50, 50)

        quit_action = QAction('Quit', self)
        quit_action.setShortcut(QKeySequence('Esc'))
        quit_action.triggered.connect(self.close)
        self.addAction(quit_action)

    def resizeEvent(self, event) -> None:
        self._rect = QRect(0, 0, self.width(), self.height())
        print(f"show--- {self._rect}")

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setBrush(QBrush(Qt.red))
        painter.setFont(QFont("Arial", 20))
        painter.drawRect(self._rect)

        painter.drawText(self.width() / 2, self.height() / 2,
                         f"{self._rect.width()}x{self._rect.height()}\n"
                         f"{self._rect.x(), self._rect.y()}")

    def keyPressEvent(self, event) -> None:
        if event.modifiers() & Qt.ShiftModifier:
            if event.key() == Qt.Key_Left:
                self._rect += QMargins(1, 0, 0, 0)
            elif event.key() == Qt.Key_Right:
                self._rect += QMargins(0, 0, 1, 0)
            elif event.key() == Qt.Key_Up:
                self._rect += QMargins(0, 1, 0, 0)
            elif event.key() == Qt.Key_Down:
                self._rect += QMargins(0, 0, 0, 1)
        else:
            if event.key() == Qt.Key_Left:
                self._rect -= QMargins(1, 0, 0, 0)
            elif event.key() == Qt.Key_Right:
                self._rect -= QMargins(0, 0, 1, 0)
            elif event.key() == Qt.Key_Up:
                self._rect -= QMargins(0, 1, 0, 0)
            elif event.key() == Qt.Key_Down:
                self._rect -= QMargins(0, 0, 0, 1)

        self.update()

        screen_size = self.screen().size()
        x = self._rect.x()
        y = self._rect.y()

        print("xrandr --output HDMI-1 " +
              f"--mode {screen_size.width()}x{screen_size.height()} " +
              f"--fb {self._rect.width()}x{self._rect.height()} " +
              f"--transform 1,0,{x},0,1,{y},0,0,1")


def main_entrypoint():
    # Allow Ctrl-C killing of the Qt app, see:
    # http://stackoverflow.com/questions/4938723/
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication([])
    window = MainWindow()

    window.setWindowState(window.windowState() | Qt.WindowFullScreen)
    # self.setWindowState(self.windowState() & ~Qt.WindowFullScreen)
    window.show()

    app.exec_()


# EOF #
