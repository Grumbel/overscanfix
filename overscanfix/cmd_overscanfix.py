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
        self.setWindowTitle("Overscan Fix")
        self._safezone: QRect = QRect(0, 0, 1, 1)

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

        triangles = [
            # left
            QPolygon([QPoint(left + tdist, top + h//2),
                      QPoint(left, top + h//2 - tdist),
                      QPoint(left, top + h//2 + tdist)
                      ]),

            # right
            QPolygon([QPoint(right - tdist + 1, top + h//2),
                      QPoint(right + 1, top + h//2 - tdist),
                      QPoint(right + 1, top + h//2 + tdist)
                      ]),

            # top
            QPolygon([QPoint(left + w//2, top + tdist),
                      QPoint(left + w//2 - tdist, top),
                      QPoint(left + w//2 + tdist, top)
                      ]),

            # bottom
            QPolygon([QPoint(left + w//2, bottom - tdist + 1),
                      QPoint(left + w//2 + tdist, bottom + 1),
                      QPoint(left + w//2 - tdist, bottom + 1)
                      ]),
            ]

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.red)
        for triangle in triangles:
            painter.drawPolygon(triangle)

        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 20))
        text_x = self.width() / 2 - 200
        painter.drawText(text_x, self.height() / 2 + 32,
                         f"size: {w}x{h}")
        painter.drawText(text_x, self.height() / 2 + 64,
                         f"pos: {left}, {top}")

        painter.drawText(text_x, self.height() / 2 + 96,
                         f"border left: {left} right: {self.width() - right - 1} top: {top} bottom: {self.height() - bottom - 1}")

        painter.setPen(Qt.gray)
        painter.setFont(QFont("Arial", 14))
        painter.drawText(text_x, self.height() / 2 - 32,
                         f"Use cursor keys and shift to adjust borders, Esc to quit")
        painter.drawText(text_x, self.height() / 2 - 64,
                         "Adjust until only a thin white line is visible at the edge")

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
