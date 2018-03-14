import queue
import threading
import cv2
from PyQt5.Qt import *
import ButtonWidget
import VideoWidget
import SliderWidget
import MouseTracker


class MainWindow(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Big Brother watches you")
        self.video_reader = None
        self.left_grid = QGridLayout(self)
        self.setLayout(self.left_grid)

        # file field
        self.file_text = QLineEdit()
        self.file_text.setFixedHeight(20)
        self.file_text.setReadOnly(True)
        self.file_button = ButtonWidget.OpenButton()
        self.left_grid.addWidget(self.file_text, 0, 0, 1, 2)
        self.left_grid.addWidget(self.file_button, 0, 2, 1, 1)

        self.file_text_out = ButtonWidget.SaveField()
        self.file_text_out.setFixedHeight(20)
        self.file_text_out.setReadOnly(True)
        self.file_button_out = ButtonWidget.SaveButton()
        self.left_grid.addWidget(self.file_text_out, 1, 0, 1, 2)
        self.left_grid.addWidget(self.file_button_out, 1, 2, 1, 1)

        # player
        self.player = VideoWidget.VideoWidget()
        self.left_grid.addWidget(self.player, 2, 0, 1, 3)

        self.picker = VideoWidget.Picker()
        self.picker.hide()
        self.left_grid.addWidget(self.picker, 2, 0, 1, 3)

        # slider
        self.range_slider = SliderWidget.RangeSlider()
        self.frame_slider = SliderWidget.FrameSlider()
        self.time_left = SliderWidget.TimeEdit()
        self.time_right = SliderWidget.TimeEdit(1)
        self.time_current = SliderWidget.TimeEdit()
        self.play_button = ButtonWidget.PlayPauseButton()
        self.left_grid.addWidget(self.time_left, 3, 0, 1, 1)
        self.left_grid.addWidget(self.range_slider, 3, 1, 1, 1)
        self.left_grid.addWidget(self.time_right, 3, 2, 1, 1)
        self.left_grid.addWidget(self.play_button, 4, 0, 1, 1)
        self.left_grid.addWidget(self.frame_slider, 4, 1, 1, 1)
        self.left_grid.addWidget(self.time_current, 4, 2, 1, 1)

        # queue
        self.queue = queue.Queue()  # sync
        self.render_log = VideoWidget.ProceedImage(self.queue)
        self.render_log.start()

        # signals
        self.file_button.file_selected.connect(self.file_text.setText)
        self.file_button.file_selected.connect(self.player.openVideo)
        self.file_button.file_selected.connect(self.file_text_out.setFromOutput)
        self.file_button_out.file_selected.connect(self.file_text_out.setText)
        self.range_slider.left_slider_changed.connect(self.frame_slider.setMinValue)
        self.range_slider.left_slider_changed.connect(self.time_left.setValue)
        self.time_left.time_changed.connect(self.range_slider.setLeftValue)
        self.range_slider.right_slider_changed.connect(self.frame_slider.setMaxValue)
        self.range_slider.right_slider_changed.connect(self.time_right.setValue)
        self.time_right.time_changed.connect(self.range_slider.setRightValue)
        self.frame_slider.slider_changed.connect(self.time_current.setValue)
        self.frame_slider.player_update.connect(self.player.setCurrentSecond)
        self.frame_slider.player_stop.connect(self.player.media_player.pause)
        self.time_current.time_changed.connect(self.frame_slider.setValue)
        self.player.duration_changed.connect(self.range_slider.setMaxValue)
        self.player.current_frame_changed.connect(self.frame_slider.setValuePlayer)
        self.player.media_player.stateChanged.connect(self.play_button.getPlayerState)
        self.play_button.play_player.connect(self.player.media_player.play)
        self.play_button.play_player.connect(self.player.setVideoPlayer)
        self.play_button.play_player.connect(self.picker.hide)
        self.play_button.pause_player.connect(self.player.media_player.pause)

        self.render_log.update_viewport.connect(self.player.setMatrixImage)
        self.render_log.update_slider.connect(self.frame_slider.setValue)

        # add render button
        self.btn_start = QPushButton()
        self.btn_start.setFlat(True)
        self.btn_start.setIconSize(QSize(32, 32))
        self.btn_start.setFixedSize(32, 32)
        self.btn_start.setIcon(QIcon("icons/start_render.png"))
        self.left_grid.addWidget(self.btn_start, 0, 4, 2, 1)
        self.btn_start.released.connect(self.startRender)
        
        self.btn_stop = QPushButton()
        self.btn_stop.setFlat(True)
        self.btn_stop.setIconSize(QSize(32, 32))
        self.btn_stop.setFixedSize(32, 32)
        self.btn_stop.setIcon(QIcon("icons/stop_render.png"))
        self.left_grid.addWidget(self.btn_stop, 0, 5, 2, 1)
        self.btn_stop.released.connect(self.stopRender)

        self.btn_radius = QPushButton()
        self.btn_radius.setFlat(True)
        self.btn_radius.setIconSize(QSize(32, 32))
        self.btn_radius.setFixedSize(32, 32)
        self.btn_radius.setIcon(QIcon("icons/circle.png"))
        self.left_grid.addWidget(self.btn_radius, 0, 6, 2, 1)
        self.btn_radius.released.connect(self.circleMode)

        self.cmb_res = QComboBox()
        self.cmb_res.addItems(["UI size: 640x360", "UI size: 1280x720"])
        self.cmb_res.currentIndexChanged.connect(self.picker.changeResolution)
        self.cmb_res.currentIndexChanged.connect(self.player.changeResolution)
        self.cmb_res.currentIndexChanged.connect(self.changeResolution)
        self.left_grid.addWidget(self.cmb_res, 4, 4, 1, 3)

        self.text_out = QTextEdit()
        self.left_grid.addWidget(self.text_out, 2, 4, 1, 4)

        self.changeResolution()

    def startRender(self):
        """execute rendering"""
        if self.video_reader:
            self.video_reader.stop()

        self.picker.hide()
        self.video_reader = MouseTracker.VideoReader(self.file_text.text(),
                                                     self.file_text_out.text(),
                                                     start=self.range_slider.left_value,
                                                     end=self.range_slider.right_value,
                                                     frame_queue=self.queue,
                                                     size=(1280, 720))
        args = (self.video_reader, self.picker.center, self.picker.radius)
        threading.Thread(target=MouseTracker.startTracking, args=args).start()

    def stopRender(self):
        """stop render"""
        if self.video_reader:
            self.video_reader.stop()

    def circleMode(self):
        """turn on circle point mode"""
        video_reader = cv2.VideoCapture(self.file_text.text())
        is_frame, frame = video_reader.read()
        if is_frame:
            self.player.setMatrixImage(frame)
            self.picker.show()

    def changeResolution(self, resolution=0):
        if resolution == 0:
            self.setFixedSize(900, 490)
        else:
            self.setFixedSize(1570, 850)
