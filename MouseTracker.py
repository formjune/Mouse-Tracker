import threading
import itertools
import math
import cv2
import numpy as np


class VideoReader(object):
    """multi threading video reader writer"""

    def __init__(self, input_name, output_name, size=(1280, 720), start=0, end=5, frame_queue=None):
        self.video_reader = cv2.VideoCapture(input_name)
        self.fps = self.video_reader.get(cv2.CAP_PROP_FPS)
        self.size = size
        self.current_second_in = self.current_second_out = self.start_second = start
        self.end_second = end
        self.current_frame_out = itertools.count()   # to be increased after giving away frame
        self.current_frame_in = 0    # to be increased after taking frame
        self.lock = threading.Lock()
        self.frames_stock = {}
        self.points_stock = []
        self.frame_queue = frame_queue
        self.video_writer = cv2.VideoWriter(output_name, cv2.VideoWriter_fourcc(*'PIM1'), self.fps, self.size)

    def getBackground(self):
        """get background once and set time we need start from"""
        background = self.video_reader.read()[1]
        background = cv2.resize(background, self.size)
        background = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
        background = cv2.GaussianBlur(background, (11, 11), 0)
        self.video_reader.set(cv2.CAP_PROP_POS_FRAMES, self.fps * self.start_second)
        return background

    def getFrame(self):
        """get frame and frame number"""
        with self.lock:
            if self.current_second_out > self.end_second:   # out of range
                return None, None
            self.current_second_out += 1. / self.fps
            is_frame, frame = self.video_reader.read()
            if not is_frame:    # if no return None
                return None, None
            return next(self.current_frame_out), cv2.resize(frame, self.size)

    def setFrame(self, frame_number, frame_array, point):
        """write frame and display if need"""
        with self.lock:
            self.frames_stock[frame_number] = frame_array, point
            while self.current_frame_in in self.frames_stock:
                frame_array, point = self.frames_stock.pop(self.current_frame_in)
                self.points_stock = self.points_stock[-250:]  # leave last 25 path points only
                if point is not None:
                    moments = cv2.moments(point)
                    x = int(moments["m10"] / moments["m00"])
                    y = int(moments["m01"] / moments["m00"])
                    self.points_stock.append((x, y))
                for i in range(len(self.points_stock) - 1):
                    cv2.line(frame_array, self.points_stock[i], self.points_stock[i + 1], (0, 0xff, 0xff))

                self.video_writer.write(frame_array)
                if self.frame_queue:
                    self.frame_queue.put((self.current_second_in, frame_array))
                self.current_frame_in += 1
                self.current_second_in += 1. / self.fps

    def stop(self):
        """finish recording"""
        with self.lock:
            if self.video_writer.isOpened():
                self.video_writer.release()


def threadProceed(video_reader, background, border, mask):
    """thread for mouse tracking
    background - first frame. gray
    border - circle or None, made for drawing on frame
    mask - boolean matrix for filters"""

    def checkContour(contour):
        """analyze contours for border and return true if contour is good"""
        for line in contour:
            x = line[0][0] - border[0]
            y = line[0][1] - border[1]
            length = math.sqrt(x ** 2 + y ** 2)
            if length / border[2] >= .99:
                return False
        return True

    while video_reader.video_writer.isOpened():

        number, original = video_reader.getFrame()
        if number is None:
            break

        if border is not None:
            cv2.circle(original, (border[0], border[1]), border[2], (0, 0xff, 0), thickness=2)

        frame = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)  # convert to gray
        frame = cv2.GaussianBlur(frame, (11, 11), 0)    # smooth
        frame = cv2.absdiff(frame, background)  # find difference
        # video_reader.setFrame(number, cv2.merge((frame, frame, frame)), None)

        frame = cv2.threshold(frame, 20, 255, cv2.THRESH_BINARY)[1]     # remove small difference
        frame = cv2.dilate(frame, None, iterations=10)   # swell mouse
        frame &= mask   # remove outside borders
        contours = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]  # find contours
        contours.sort(key=lambda x: cv2.contourArea(x), reverse=True)   # sort by size

        for contour in contours:
            if checkContour(contour):
                cv2.drawContours(original, [contour], 0, (0, 0, 255), 2)
                video_reader.setFrame(number, original, contour)
                break
        else:
            video_reader.setFrame(number, original, None)


def startTracking(video_reader, center, radius):
    """main thread for tracking mouse"""
    background = video_reader.getBackground()

    mask = np.zeros(background.shape, dtype=np.uint8)
    x = int(center[0] * background.shape[1])
    y = int(center[1] * background.shape[0])
    radius = int(radius * background.shape[1])
    cv2.circle(mask, (x, y), radius, (0xff, ), thickness=-1)
    circle = [x, y, radius]

    # circle, mask = findCircleMask(background)
    # cv2.imshow("w", mask)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    threads = []
    for i in range(8):  # 8 threads is most optimal +100% of speed
        threads.append(threading.Thread(target=threadProceed, args=(video_reader, background, circle, mask)))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    video_reader.stop()


if __name__ == "__main__":
    a = VideoReader("D:/downloads/videoplayback.mp4", "D:/a.avi", end=10)
    startTracking(a)
