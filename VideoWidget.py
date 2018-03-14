import sys
import os
import math
import cv2
from PyQt5.Qt import *
import numpy as np


__location__ = os.path.dirname(__file__)


class Picker(QLabel):
    """contains circle radius information"""

    center = .5, .5
    radius = .2

    def changeResolution(self, resolution=0):
        resolution += 1
        self.setFixedSize(640 * resolution, 360 * resolution)

    def createCircle(self):
        pixmap = QPixmap(self.width(), self.height())
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor(255, 0, 0, 255)))
        center = QPoint(self.center[0] * self.width(), self.center[1] * self.height())
        painter.drawPoint(center)
        radius = self.radius * self.width()
        painter.drawEllipse(center, radius, radius)
        painter.end()
        self.setPixmap(pixmap)

    def mousePressEvent(self, event):
        if event.button() == 1:
            self.center = event.pos().x() / self.width(), event.pos().y() / self.height()
        else:
            r_x = abs(event.pos().x() / self.width() - self.center[0])
            r_y = abs(event.pos().y() / self.height() - self.center[1]) * (self.height() / self.width())
            self.radius = math.sqrt(r_x ** 2 + r_y ** 2)
        self.createCircle()

    def mouseMoveEvent(self, event):
        r_x = abs(event.pos().x() / self.width() - self.center[0])
        r_y = abs(event.pos().y() / self.height() - self.center[1]) * (self.height() / self.width())
        self.radius = math.sqrt(r_x ** 2 + r_y ** 2)
        self.createCircle()

    def __init__(self):
        QLabel.__init__(self)
        self.setStyleSheet("background-color: transparent;color: red")
        self.setWindowOpacity(.1)
        self.changeResolution()
        self.createCircle()


class ProceedImage(QThread):
    """get images from rendering threads via queue and updates viewport"""
    update_viewport = pyqtSignal(np.ndarray)
    update_slider = pyqtSignal(int)

    def __init__(self, image_queue):
        QThread.__init__(self)
        self.queue = image_queue

    def run(self):
        """get images and emit qsignal"""
        while True:
            time_seconds, frame_array = self.queue.get()
            self.update_slider.emit(int(time_seconds))
            self.update_viewport.emit(frame_array)


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
        self.changeResolution()

    def changeResolution(self, resolution=0):
        """select between resolution with aspect ratio"""
        resolution += 1
        self.setFixedSize(640 * resolution, 360 * resolution)

    def setMatrixImage(self, array):
        """set background image from numpy array"""
        array = cv2.resize(array, (self.width(), self.height()))
        array = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)      # reverse BGR to RGB
        image = QImage(array.data, array.shape[1], array.shape[0], QImage.Format_RGB888)
        self.image_player.setPixmap(QPixmap(image))
        self.setCurrentWidget(self.image_player)

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
            self.current_frame_changed.emit(value)  # if it runs signal to time to update time


if __name__ == "__main__":
    app = QApplication([])
    a = VideoWidget()
    a.show()
    a.openVideo(__location__ + "/10.mp14")
    sys.exit(app.exec())
