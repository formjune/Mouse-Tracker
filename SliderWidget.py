import sys
from PyQt5.Qt import *


def findMiddle(left_value, middle_value, right_value):
    """find value in given range"""
    return max(left_value, min(right_value, middle_value))


class RangeSlider(QWidget):
    """two sliders for setting up the range"""
    MOVE_NONE = 0
    MOVE_LEFT = 1
    MOVE_RIGHT = 2

    left_slider_changed = pyqtSignal(int)   # tell frame slider about changing left limit
    right_slider_changed = pyqtSignal(int)   # tell frame slider about changing right limit
    action = MOVE_NONE

    def __init__(self, max_value=1):
        QWidget.__init__(self)
        self.setFixedHeight(20)
        self.setMinimumWidth(100)
        self.left_value = 0
        self.right_value = self.max_value = max(1, max_value)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def mousePressEvent(self, event):
        """select controller for move"""
        left_pixel = (self.width() - 20) * self.left_value / self.max_value
        right_pixel = (self.width() - 20) * self.right_value / self.max_value
        cursor = event.pos().x()
        if left_pixel <= cursor <= left_pixel + 10:
            self.action = self.MOVE_LEFT
        elif right_pixel + 20 >= cursor >= right_pixel + 10:
            self.action = self.MOVE_RIGHT
        else:
            self.action = self.MOVE_NONE
            return
        self.update()

    def mouseMoveEvent(self, event):
        """calculate left and right values"""
        if self.action == self.MOVE_NONE:
            return
        value = round((event.pos().x() - 10) / ((self.width() - 20) / self.max_value))
        if self.action == self.MOVE_LEFT and value != self.left_value:
            self.left_value = findMiddle(0, value, self.right_value - 1)
            self.left_slider_changed.emit(self.left_value)
        elif self.action == self.MOVE_RIGHT and value != self.right_value:
            self.right_value = findMiddle(self.left_value + 1, value, self.max_value)
            self.right_slider_changed.emit(self.right_value)
        self.update()

    def paintEvent(self, event):
        """update ui"""
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(231, 234, 234)))
        painter.setPen(QPen(QColor(214, 214, 214)))
        painter.drawRect(0, 8, self.width() - 1, 4)
        left_value = (self.width() - 20) * self.left_value / self.max_value
        rigth_value = (self.width() - 20) * self.right_value / self.max_value + 10
        painter.setBrush(QBrush(QColor(0, 122, 217)))
        painter.drawRect(left_value, 8, rigth_value - left_value + 1, 4)
        painter.setBrush(QBrush(QColor(0, 122, 217)))
        painter.setPen(QPen(QColor(0, 122, 217)))
        painter.drawRect(left_value, 0, 10, 20)
        painter.drawRect(rigth_value, 0, 10, 20)

    def setMaxValue(self, max_value=1):
        """set new values. left value is locked for 0"""
        self.max_value = max(1, int(max_value))
        self.setLeftValue(0)
        self.setRightValue(self.max_value)

    def setLeftValue(self, value):
        """set left value"""
        value = findMiddle(0, value, self.right_value - 1)
        if value != self.left_value:
            self.left_value = value
            self.left_slider_changed.emit(self.left_value)  # return corrected value into time widget
            self.update()

    def setRightValue(self, value):
        """set right value"""
        value = findMiddle(self.left_value + 1, value, self.max_value)
        if value != self.right_value:
            self.right_value = value
            self.right_slider_changed.emit(self.right_value)  # return corrected value into time widget
            self.update()


class FrameSlider(QWidget):
    """slider for current time frame"""
    action = True
    slider_changed = pyqtSignal(int)    # update time line frame
    player_update = pyqtSignal(int)     # update player frame
    player_stop = pyqtSignal()          # stop player

    def __init__(self, min_value=0, max_value=1, value=0):
        QWidget.__init__(self)
        self.setFixedHeight(20)
        self.setMinimumWidth(100)
        self.min_value = min_value
        self.max_value = max_value
        self.value = value

    def mousePressEvent(self, event):
        """select controller for move"""
        pixel = (self.width() - 10) * (self.value - self.min_value) / (self.max_value - self.min_value)
        if pixel <= event.pos().x() <= pixel + 10:
            self.action = True
            self.update()
        else:
            self.action = False

    def mouseMoveEvent(self, event):
        """calculate left and right values"""
        if not self.action:
            return
        value = round((event.pos().x() - 5) / ((self.width() - 10) / (self.max_value - self.min_value)))
        value = findMiddle(self.min_value, value + self.min_value, self.max_value)
        if value != self.value:
            self.value = value
            self.slider_changed.emit(self.value)
            self.player_update.emit(self.value)
            self.update()

    def paintEvent(self, event):
        """update ui"""
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(231, 234, 234)))
        painter.setPen(QPen(QColor(214, 214, 214)))
        painter.drawRect(0, 8, self.width() - 1, 4)
        painter.setBrush(QBrush(QColor(0, 122, 217)))
        painter.setPen(QPen(QColor(0, 122, 217)))
        painter.drawRect((self.width() - 10) * (self.value - self.min_value) / (self.max_value - self.min_value),
                         0, 10, 20)

    def setMaxValue(self, value):
        self.max_value = max(self.min_value + 1, value)
        current_value = findMiddle(self.min_value, self.value, self.max_value)
        if current_value != self.value:
            self.value = current_value
            self.slider_changed.emit(self.value)
            self.player_update.emit(self.value)
        self.update()

    def setMinValue(self, value):
        self.min_value = findMiddle(0, value, self.max_value - 1)
        current_value = findMiddle(self.min_value, self.value, self.max_value)
        if current_value != self.value:
            self.value = current_value
            self.player_update.emit(self.value)
            self.slider_changed.emit(self.value)
        self.update()

    def setValue(self, value):
        """receive value from range slider or time editor and update player"""
        value = findMiddle(self.min_value, value, self.max_value)
        if value != self.value:
            self.value = value
            self.slider_changed.emit(self.value)    # send into time widget
            self.player_update.emit(self.value)     # send into player
            self.update()

    def setValuePlayer(self, value):
        """receive new value from player. Update TimeEditor widget only"""
        if not self.min_value <= value <= self.max_value:
            self.player_stop.emit()
        else:
            value = findMiddle(self.min_value, value, self.max_value)
            if value != self.value:
                self.value = value
                self.slider_changed.emit(self.value)    # send into time widget
                self.update()


class TimeEdit(QLineEdit):
    """time converting widget"""
    time_changed = pyqtSignal(int)      # send new time into range slider and receive new value

    def __init__(self, value=0):
        QLineEdit.__init__(self)
        self.setFixedSize(44, 20)
        self.value = value
        self.setValue(value)

    def keyPressEvent(self, event):
        if event.key() == 16777220:     # press enter
            try:
                minutes, seconds = [int(t) for t in self.text().split(":")]
                if 0 <= minutes and 0 <= seconds:
                    self.time_changed.emit(minutes * 60 + seconds)
            except (ValueError, TypeError, Exception):  # wrong time entered. restore back
                self.setValue(self.value)
        else:
            QLineEdit.keyPressEvent(self, event)

    def setValue(self, value):
        """set new time value and convert"""
        self.value = value
        self.setText("%i:%.2i" % divmod(value, 60))


if __name__ == "__main__":
    app = QApplication([])
    slider = RangeSlider(100)
    slider.show()
    sys.exit(app.exec())