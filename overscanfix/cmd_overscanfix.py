import signal

from PyQt5.QtWidgets import QApplication, QWidget, QAction
from PyQt5.QtGui import QPainter, QBrush, QFont, QKeySequence, QPolygon
from PyQt5.QtCore import Qt, QRect, QMargins, QPoint


def print_xrandr_cmd(screen_size: QRect, safezone: QRect) -> None:
    sx = screen_size.width() / safezone.width()
    sy = screen_size.height() / safezone.height()

    left = safezone.left()
    top = safezone.top()

    # FIXME: Get the correct output and mode names
    output = "HDMI-1"
    mode = f"{screen_size.width()}x{screen_size.height()}"
    fb = f"{screen_size.width()}x{screen_size.height()}"
    print("xrandr " +
          f"--output {output} " +
          f"--mode {mode} " +
          f"--fb {fb} " +
          f"--transform {sx},0,{-left},0,{sy},{-top},0,0,1"
          )


class MainWindow(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Rectangle")
        # self.setGeometry(100, 100, 300, 300)
        self._safezone: QRect = QRect(100, 100, 50, 50)

        quit_action = QAction('Quit', self)
        quit_action.setShortcut(QKeySequence('Esc'))
        quit_action.triggered.connect(self.close)
        self.addAction(quit_action)

    def resizeEvent(self, event) -> None:
        self._safezone = QRect(0, 0, self.width(), self.height())

    def paintEvent(self, event) -> None:
        painter = QPainter(self)

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.black)

        painter.drawRect(self._safezone)

        left = self._safezone.left()
        top = self._safezone.top()
        right = self._safezone.right()
        bottom = self._safezone.bottom()

        tdist = 200

        w = self._safezone.width()
        h = self._safezone.height()

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
                self._safezone += QMargins(1, 0, 0, 0)
            elif event.key() == Qt.Key_Right:
                self._safezone += QMargins(0, 0, 1, 0)
            elif event.key() == Qt.Key_Up:
                self._safezone += QMargins(0, 1, 0, 0)
            elif event.key() == Qt.Key_Down:
                self._safezone += QMargins(0, 0, 0, 1)
        else:
            if event.key() == Qt.Key_Left:
                self._safezone -= QMargins(1, 0, 0, 0)
            elif event.key() == Qt.Key_Right:
                self._safezone -= QMargins(0, 0, 1, 0)
            elif event.key() == Qt.Key_Up:
                self._safezone -= QMargins(0, 1, 0, 0)
            elif event.key() == Qt.Key_Down:
                self._safezone -= QMargins(0, 0, 0, 1)

        self.update()

        print_xrandr_cmd(self.screen().size(), self._safezone)


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
