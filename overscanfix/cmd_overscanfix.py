import signal

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QFont, QKeySequence, QPolygon, \
    QResizeEvent, QPaintEvent, QKeyEvent, QAction
from PyQt6.QtCore import Qt, QSize, QRect, QMargins, QPoint, QPointF


def print_xrandr_cmd(screen_size: QSize, safezone: QRect, output: str) -> None:
    sx = screen_size.width() / safezone.width()
    sy = screen_size.height() / safezone.height()

    left = safezone.left()
    top = safezone.top()

    # FIXME: Get the correct output and mode names
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

        def close_cb() -> None:
            self.close()

        quit_action = QAction('Quit', self)
        quit_action.setShortcut(QKeySequence('Esc'))
        quit_action.triggered.connect(close_cb)
        self.addAction(quit_action)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self._safezone = QRect(0, 0, self.width(), self.height())

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(Qt.GlobalColor.black)

        painter.drawRect(self._safezone)

        left = self._safezone.left()
        top = self._safezone.top()
        right = self._safezone.right()
        bottom = self._safezone.bottom()

        tdist = 200

        w = self._safezone.width()
        h = self._safezone.height()

        painter.setPen(Qt.GlobalColor.gray)

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

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(Qt.GlobalColor.red)
        for triangle in triangles:
            painter.drawPolygon(triangle)

        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(QFont("Arial", 20))
        text_x = self.width() / 2 - 200
        painter.drawText(QPointF(text_x, self.height() / 2 + 32),
                         f"size: {w}x{h}")
        painter.drawText(QPointF(text_x, self.height() / 2 + 64),
                         f"pos: {left}, {top}")

        painter.drawText(QPointF(text_x, self.height() / 2 + 96),
                         f"border left: {left} right: {self.width() - right - 1} "
                         f"top: {top} bottom: {self.height() - bottom - 1}")

        painter.setPen(Qt.GlobalColor.gray)
        painter.setFont(QFont("Arial", 20))
        painter.drawText(QPointF(text_x, self.height() / 2 - 32),
                         "Use cursor keys and shift to adjust borders, Esc to quit")
        painter.drawText(QPointF(text_x, self.height() / 2 - 64),
                         "Adjust until only a thin white line is visible at the edge")

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            if event.key() == Qt.Key.Key_Left:
                self._safezone = self._safezone.marginsAdded(QMargins(1, 0, 0, 0))
            elif event.key() == Qt.Key.Key_Right:
                self._safezone = self._safezone.marginsAdded(QMargins(0, 0, 1, 0))
            elif event.key() == Qt.Key.Key_Up:
                self._safezone = self._safezone.marginsAdded(QMargins(0, 1, 0, 0))
            elif event.key() == Qt.Key.Key_Down:
                self._safezone = self._safezone.marginsAdded(QMargins(0, 0, 0, 1))
        else:
            if event.key() == Qt.Key.Key_Left:
                self._safezone = self._safezone.marginsRemoved(QMargins(1, 0, 0, 0))
            elif event.key() == Qt.Key.Key_Right:
                self._safezone = self._safezone.marginsRemoved(QMargins(0, 0, 1, 0))
            elif event.key() == Qt.Key.Key_Up:
                self._safezone = self._safezone.marginsRemoved(QMargins(0, 1, 0, 0))
            elif event.key() == Qt.Key.Key_Down:
                self._safezone = self._safezone.marginsRemoved(QMargins(0, 0, 0, 1))

        self.update()

        print_xrandr_cmd(self.screen().size(), self._safezone, self.screen().name())


def main_entrypoint() -> None:
    # Allow Ctrl-C killing of the Qt app, see:
    # http://stackoverflow.com/questions/4938723/
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication([])
    window = MainWindow()

    window.setWindowState(window.windowState() | Qt.WindowState.WindowFullScreen)
    # self.setWindowState(self.windowState() & ~Qt.WindowState.WindowFullScreen)
    window.show()

    app.exec()


# EOF #
