import sys
import os
from PyQt5.Qt import *


__location__ = os.path.dirname(__file__)


class PlayPauseButton(QPushButton):
    """play pause player button"""
    play_player = pyqtSignal()
    pause_player = pyqtSignal()

    def __init__(self):
        QPushButton.__init__(self)
        self.setIconSize(QSize(44, 20))
        self.setFixedSize(QSize(44, 20))
        self.setFlat(True)
        self.setIcon(QIcon(__location__ + "/icons/play.png"))
        self.state = 2  # paused

    def getPlayerState(self, state):
        """receive player state. either playing or stopped"""
        if state != self.state:
            self.setIcon(QIcon(__location__ + ("/icons/pause.png" if state == 1 else "/icons/play.png")))
        self.state = state

    def mousePressEvent(self, event):
        """play/pause video"""
        if self.state == 1:
            self.pause_player.emit()
        else:
            self.play_player.emit()


class OpenButton(QPushButton):
    """open new video button"""

    file_selected = pyqtSignal(str)     # send video file to play

    def __init__(self):
        QPushButton.__init__(self)
        self.setText("input")
        self.setFixedSize(44, 20)

    def mousePressEvent(self, event):
        file_names = QFileDialog().getOpenFileName()
        if not file_names:
            return
        self.file_selected.emit(file_names[0])


class SaveButton(QPushButton):
    """open new video button"""

    file_selected = pyqtSignal(str)  # send video file to play

    def __init__(self):
        QPushButton.__init__(self)
        self.setText("output")
        self.setFixedSize(44, 20)

    def mousePressEvent(self, event):
        file_names = QFileDialog().getSaveFileName()[0]
        if not file_names:
            return
        self.file_selected.emit(file_names)


class SaveField(QLineEdit):
    """field for saving files"""

    def setFromOutput(self, file_name):
        """automatically replace name from input"""
        self.setText(os.path.splitext(file_name)[0] + "_output.avi")


if __name__ == "__main__":
    app = QApplication([])
    slider = PlayPauseButton()
    slider.show()
    sys.exit(app.exec())