import threading
import itertools
import math
import cv2
import numpy as np


class VideoReader(object):
    """multi threading video reader writer"""

    def __init__(self, input_name, output_name, size=(720, 480), start=0, end=5, frame_queue=None):
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
                self.points_stock.append(point)
                self.points_stock = self.points_stock[-25:]     # leave last 25 path points only
                # record path info frame !!!
                self.video_writer.write(frame_array)
                if self.frame_queue:
                    self.frame_queue.put((self.current_second_in, frame_array))
                self.current_frame_in += 1
                self.current_second_in += 1. / self.fps

    def stop(self):
        """finish recording"""
        if self.video_writer.isOpened():
            self.video_writer.release()


def findCircleMask(array):
    """find circle from gray array. returns binary mask"""

    def contourSort(contour_block):
        """get new contour block like (x, y, radius) and return it's vector length"""
        x = (contour_block[0] - center_x) ** 2
        y = (contour_block[1] - center_y) ** 2
        r = (contour_block[2] - center_y) ** 2
        return math.sqrt(x + y + r)     # vector length

    # array = cv2.threshold(array, 220, 255, cv2.THRESH_BINARY)[1]
    circles = cv2.HoughCircles(array, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30)[0]
    center_x = array.shape[1] / 2.
    center_y = array.shape[0] / 2.
    circles = sorted(circles, key=contourSort)
    if circles:
        mask_array = np.zeros(array.shape, dtype=np.uint8)
        c = circles[0]
        cv2.circle(mask_array, (c[0], c[1]), c[2], (0xff, ), thickness=-1)
        return mask_array

    else:   # return whole field as mask
        return np.ones(array.shape, dtype=np.uint8) * 255






def threadProceed(video_reader, background):
    """thread for mouse tracking"""
    while video_reader.video_writer.isOpened():


        t, f = video_reader.getFrame()
        if t is None:
            break
        a.setFrame(t, cv2.GaussianBlur(f, (13, 13), 0), None)


def startTracking(video_reader):
    """main thread for tracking mouse"""
    background = video_reader.getBackground()
    mask = findCircleMask(background)
    cv2.imshow("w", mask)
    cv2.waitKey()
    cv2.destroyAllWindows()
    return

    threads = []
    for i in range(8):  # 8 threads is most optimal +100% of speed
        threads.append(threading.Thread(target=threadProceed, args=(video_reader, background)))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    video_reader.stop()


a = VideoReader("D:/downloads/videoplayback.mp4", "D:/a.avi", end=10)
startTracking(a)
