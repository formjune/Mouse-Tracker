from PyQt5.Qt import *
import ButtonWidget
import VideoWidget
import SliderWidget


class MainWindow(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.left_grid = QGridLayout(self)
        self.setLayout(self.left_grid)

        # file field
        self.file_text = QLineEdit()
        self.file_text.setFixedHeight(20)
        self.file_text.setReadOnly(True)
        self.file_button = ButtonWidget.OpenButton()
        self.left_grid.addWidget(self.file_text, 0, 0, 1, 2)
        self.left_grid.addWidget(self.file_button, 0, 2, 1, 1)

        # player
        self.player = VideoWidget.VideoWidget()
        self.left_grid.addWidget(self.player, 1, 0, 1, 3)

        # slider
        self.range_slider = SliderWidget.RangeSlider()
        self.frame_slider = SliderWidget.FrameSlider()
        self.time_left = SliderWidget.TimeEdit()
        self.time_right = SliderWidget.TimeEdit(1)
        self.time_current = SliderWidget.TimeEdit()
        self.play_button = ButtonWidget.PlayPauseButton()
        self.left_grid.addWidget(self.time_left, 2, 0, 1, 1)
        self.left_grid.addWidget(self.range_slider, 2, 1, 1, 1)
        self.left_grid.addWidget(self.time_right, 2, 2, 1, 1)
        self.left_grid.addWidget(self.play_button, 3, 0, 1, 1)
        self.left_grid.addWidget(self.frame_slider, 3, 1, 1, 1)
        self.left_grid.addWidget(self.time_current, 3, 2, 1, 1)

        # signals
        self.file_button.file_selected.connect(self.file_text.setText)
        self.file_button.file_selected.connect(self.player.openVideo)
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
        self.play_button.pause_player.connect(self.player.media_player.pause)
