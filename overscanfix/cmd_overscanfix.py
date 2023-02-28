import signal

from PyQt5.QtWidgets import QApplication, QWidget, QAction
from PyQt5.QtGui import QPainter, QBrush, QFont, QKeySequence, QPolygon
from PyQt5.QtCore import Qt, QRect, QMargins, QPoint


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

    def paintEvent(self, event) -> None:
        painter = QPainter(self)

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.black)

        painter.drawRect(self._rect)

        left = self._rect.left()
        top = self._rect.top()
        right = self._rect.right()
        bottom = self._rect.bottom()

        tdist = 200

        w = self._rect.width()
        h = self._rect.height()

        painter.setPen(Qt.gray)

        painter.drawEllipse(left + tdist, top + tdist, w - tdist * 2, h - tdist * 2)

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.red)

        triangles = [
            # left
            QPolygon([QPoint(left + tdist, top + h/2),
                      QPoint(left, top + h/2 - tdist),
                      QPoint(left, top + h/2 + tdist)
                      ]),

            # right
            QPolygon([QPoint(right - tdist, top + h/2),
                      QPoint(right, top + h/2 - tdist),
                      QPoint(right, top + h/2 + tdist)
                      ]),

            # top
            QPolygon([QPoint(left + w/2, top + tdist),
                      QPoint(left + w/2 - tdist, top),
                      QPoint(left + w/2 + tdist, top)
                      ]),

            # bottom
            QPolygon([QPoint(left + w/2, bottom - tdist),
                      QPoint(left + w/2 + tdist, bottom),
                      QPoint(left + w/2 - tdist, bottom)
                      ]),
            ]

        for triangle in triangles:
            painter.drawPolygon(triangle)

        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 20))
        painter.drawText(self.width() / 2 - 100, self.height() / 2,
                         f"size: {w}x{h}")
        painter.drawText(self.width() / 2 - 100, self.height() / 2 + 32,
                         f"pos: {left}, {top}")

        painter.setPen(Qt.gray)
        painter.setFont(QFont("Arial", 14))
        painter.drawText(self.width() / 2 - 100, self.height() / 2 - 32,
                         f"Use cursor keys and shift to move borders, Esc to quit")

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
