import sys
import os
import math
import cv2
from PyQt5.Qt import *


__location__ = os.path.dirname(__file__)


class VideoWidget(QStackedWidget):
    """video and image player widget"""
    duration_changed = pyqtSignal(int)  # set new length of video
    current_frame_changed = pyqtSignal(int)     # set current time in slider

    def __init__(self):
        QWidget.__init__(self)
        self.image_player = QLabel()
        self.image_player.setAlignment(Qt.AlignCenter)
        self.video_player = QVideoWidget()
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_player)
        self.addWidget(self.image_player)
        self.addWidget(self.video_player)
        self.media_player.durationChanged.connect(self.durationChanged)     # sends information in ms
        self.media_player.positionChanged.connect(self.currentFrameChanged)  # sends information in ms
        self.setDefaultImage()

    def setMatrixImage(self, array):
        """set background image from numpy array"""
        array = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)      # reverse BGR to RGB
        image = QImage(array.data, array.shape[1], array.shape[0], QImage.Format_RGB888)
        self.image_player.setPixmap(QPixmap(image))

    def setDefaultImage(self):
        """set default background image"""
        self.setCurrentWidget(self.image_player)
        self.image_player.setPixmap(QPixmap(__location__ + "/icons/background.png"))

    def setVideoPlayer(self):
        """set video player"""
        self.setCurrentWidget(self.video_player)

    def setCurrentSecond(self, second):
        """set current time in seconds"""
        self.media_player.setPosition(second * 1e3)

    def openVideo(self, video_file):
        """open video player"""
        if QFileInfo(video_file).exists():
            self.setCurrentWidget(self.video_player)
            url = QUrl.fromLocalFile(video_file)
            self.media_player.setMedia(QMediaContent(url))
        else:
            self.setDefaultImage()

    def durationChanged(self, value):
        """signal for duration changed"""
        self.duration_changed.emit(math.ceil(value / 1e3))

    def currentFrameChanged(self, value):
        """signal for current moment changed"""
        if self.media_player.state() == 1:  # check if player running
            value = round(value / 1e3)
            self.current_frame_changed.emit(value)


if __name__ == "__main__":
    app = QApplication([])
    a = VideoWidget()
    a.show()
    a.openVideo(__location__ + "/10.mp14")
    sys.exit(app.exec())
