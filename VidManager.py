import datetime
import os

import sys
import threading

from PyQt5.QtGui import (QPixmap, QImage)
from PyQt5.QtCore import (QThread, Qt, pyqtSignal, pyqtSlot)
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QLabel, QWidget, QApplication, QPushButton)

import pyrealsense2 as rs
import numpy as np
import cv2
import time


def hundred_format(number):
    if int(number) < 10:
        return "0{0}".format(number)
    return number


class RealSense(QThread):
    kill = threading.Event()
    changePixmap = pyqtSignal(
        QImage)  # Сигнал создаётся с помощью pyqtSignal() как атрибут внешнего класса Thread.

    def __init__(self, parent, name, video_source, cam_type, path):
        super(RealSense, self).__init__(parent=parent)

        self.width = 640
        self.height = 480
        self.name = name
        self.video_source = int(video_source)
        self.cam_type = cam_type
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')

        self.filename = str(
            self.name + "-" + str(self.cam_type) + "-" + str(datetime.datetime.now().year) + "-" + str(
                hundred_format(datetime.datetime.now().month)) + "-" + str(
                hundred_format(datetime.datetime.now().day)) + "-" + str(
                hundred_format(datetime.datetime.now().hour)) + str(
                hundred_format(datetime.datetime.now().minute)) + str(
                hundred_format(datetime.datetime.now().second)))
        print("Name of the file: " + self.filename + ", Video Source:" + str(video_source))

        # Configure depth and color streams
        ctx = rs.context()
        if len(ctx.devices) > 0:
            for d in ctx.devices:
                print('Found device: ',
                      d.get_info(rs.camera_info.name), ' ',
                      d.get_info(rs.camera_info.serial_number))
        else:
            print("No Intel Device connected")
            exit(0)
        self.pipeline = rs.pipeline(ctx)
        config = rs.config()
        config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, self.width, self.height, rs.format.bgr8, 30)
        self.path = path
        config.enable_record_to_file("{0}{1}.bag".format(self.path, self.filename))

        self.out_color = cv2.VideoWriter(self.path + self.filename + "_color.avi", self.fourcc, 30,
                                         (self.width, self.height))
        self.out_depth = cv2.VideoWriter(self.path + self.filename + "_depth.avi", self.fourcc, 30,
                                         (self.width, self.height))

        # Start streaming
        self.pipeline.start(config)

    def run(self):
        try:
            while not RealSense.kill.is_set():
                # Wait for a coherent pair of frames: depth and color
                frames = self.pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                if not depth_frame or not color_frame:
                    continue

                # Convert images to numpy arrays
                # depth_image = np.asanyarray(depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())
                color_image = cv2.flip(color_image, 1)
                color_image = self.add_timestamp(color_image, self.width, self.height)

                depth_image = np.asanyarray(depth_frame.get_data())
                depth_image = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
                depth_image = cv2.flip(depth_image, 1)
                depth_image = self.add_timestamp(depth_image, self.width, self.height)

                self.out_color.write(color_image)
                self.out_depth.write(depth_image)

                rgbImage = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
                convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                                           # img, width,height
                                           QImage.Format_RGB888)
                p = convertToQtFormat.scaled(360, 240, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)  # sends signal
                cv2.waitKey(1)

        finally:
            # Stop streaming
            self.pipeline.stop()

    def stop(self):
        self.pipeline.stop()

    @staticmethod
    def add_timestamp(frame, width, height):
        font = cv2.FONT_HERSHEY_SIMPLEX
        # text = 'Width: ' + str(width) + ' Height:' + str(height)
        datet = str(datetime.datetime.now())
        # frame = cv2.putText(frame, text, (10, 50), font, 1,
        #                     (0, 255, 255), 2, cv2.LINE_AA)
        frame = cv2.putText(frame, datet, ((int(width) - 370), int(height) - 10), font, 0.7,
                            (0, 255, 255), 1, cv2.LINE_AA)
        return frame


class Eken(QThread):
    kill = threading.Event()
    changePixmap = pyqtSignal(
        QImage)  # Сигнал создаётся с помощью pyqtSignal() как атрибут внешнего класса Thread.

    def __init__(self, parent, name, video_source, cam_type, path):
        super(Eken, self).__init__(parent=parent)
        self.name = name
        self.video_source = int(video_source)
        self.cam_type = cam_type
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        # name of the output file in format :
        # [full name]-[type of camera (F (face), L (left hand), R (Right hand))]-YYYY-MM-DD-HHMMSS (H-hour, M-minute, S-second)
        # (time from the beginning of the exercise)
        self.filename = str(
            self.name + "-" + str(self.cam_type) + "-" + str(datetime.datetime.now().year) + "-" + str(
                hundred_format(datetime.datetime.now().month)) + "-" + str(
                hundred_format(datetime.datetime.now().day)) + "-" + str(
                hundred_format(datetime.datetime.now().hour)) + str(
                hundred_format(datetime.datetime.now().minute)) + str(
                hundred_format(datetime.datetime.now().second)) + ".avi")
        print("Name of the file: " + self.filename + ", Video Source:" + str(video_source))
        self.path = path

    def run(self):
        self.vid = cv2.VideoCapture(self.video_source, cv2.CAP_DSHOW)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.fps = self.calc_fps()
        self.out = cv2.VideoWriter(self.path + self.filename, self.fourcc, self.fps, (640, 480))
        print("height: " + str(self.height) + " width: " + str(self.width) + " fps: " + str(self.fps))
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", self.video_source)
        while not Eken.kill.is_set():
            ret, frame = self.vid.read()
            if ret:
                # flip frame to mirror img
                frame = cv2.flip(frame, 1)
                resized_cropped_frame = self.scale(frame, 130)
                resized_cropped_timestamp = self.add_timestamp(resized_cropped_frame, self.width,
                                                               self.height)
                # write the flipped frame
                self.out.write(resized_cropped_timestamp)
                # cv2.imshow('{0}'.format(self.video_source), resized_cropped_timestamp)
                rgbImage = cv2.cvtColor(resized_cropped_timestamp, cv2.COLOR_BGR2RGB)
                convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                                           # img, width,height
                                           QImage.Format_RGB888)
                p = convertToQtFormat.scaled(360, 240, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)  # sends signal
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        self.stop()

    def stop(self):
        # When everything done, release the video capture object
        self.vid.release()

        # Closes all the frames
        cv2.destroyAllWindows()

    @staticmethod
    def add_timestamp(frame, width, height):
        font = cv2.FONT_HERSHEY_SIMPLEX
        # text = 'Width: ' + str(width) + ' Height:' + str(height)
        datet = str(datetime.datetime.now())
        # frame = cv2.putText(frame, text, (10, 50), font, 1,
        #                     (0, 255, 255), 2, cv2.LINE_AA)
        frame = cv2.putText(frame, datet, ((int(width) - 370), int(height) - 10), font, 0.7,
                            (0, 255, 255), 1, cv2.LINE_AA)
        return frame

    @staticmethod
    def scale(frame, scale):
        # get the webcam size
        height, width, channels = frame.shape
        # prepare the crop
        centerX, centerY = int(height / 2), int(width / 2)
        radiusX, radiusY = int(scale * height / 100), int(scale * width / 100)

        minX, maxX = centerX - radiusX, centerX + radiusX
        minY, maxY = centerY - radiusY, centerY + radiusY

        cropped = frame[minX:maxX, minY:maxY]
        resized_cropped = cv2.resize(cropped, (width, height))
        return resized_cropped

    def calc_fps(self, num_frames=50):
        # Number of frames to capture  num_frames

        # Start time
        start = time.time()

        # Grab a few frames
        for i in range(0, num_frames):
            ret, frame = self.vid.read()

        # End time
        end = time.time()

        # Time elapsed
        seconds = end - start
        # print("Time taken : {0} seconds".format(seconds))

        # Calculate frames per second
        fps = num_frames / seconds
        # print("Estimated frames per second : {0}".format(fps))
        return int(fps)


class App(QWidget):
    th_eken = []
    th_rs = []
    kill = threading.Event()

    def __init__(self, name, video_source, cam_type, left, top):
        super(App, self).__init__()

        self.cam_type = str(cam_type)
        self.name = str(name)
        self.path = r"D:/iBella/{0}/".format(self.name)
        self.left = left
        self.top = top
        self.width = 320
        self.height = 240
        self.video_source = video_source
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.initUI()

    def initUI(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        # self.setGeometry(self.left, self.top, self.width, self.height)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # create a label for video layout
        self.label = QLabel(self)
        self.label.move(0, 0)
        self.label.resize(640, 240)

        if self.cam_type == "L" or self.cam_type == "R":
            th = Eken(self, self.name, self.video_source, self.cam_type, self.path)

            th.changePixmap.connect(
                self.setImage)  # Пользовательский сигнал changePixmap присоединяется к слоту setImage() класса App.
            App.th_eken.append(th)
            th.start()
        elif self.cam_type == "F":
            th = RealSense(self, self.name, self.video_source, self.cam_type, self.path)

            th.changePixmap.connect(
                self.setImage)  # Пользовательский сигнал changePixmap присоединяется к слоту setImage() класса App.
            App.th_rs.append(th)
            th.start()
        else:
            print("Wrong camera type")
            exit(0)

    @pyqtSlot(QImage)  # makes slot of type QImage
    def setImage(self, image):
        # converts the given image to a pixmap (QPixmap.fromImage(image)) and add to label
        self.label.setPixmap(QPixmap.fromImage(image))

    @staticmethod
    def stop():
        print("closing the broadcast...")
        Eken.kill.set()
        RealSense.kill.set()
        for t_e in App.th_eken:
            Eken.stop(t_e)
        os._exit(0)


class add_button_close(QWidget):
    def __init__(self, left, top):
        super(add_button_close, self).__init__()
        self.left = left
        self.top = top
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setGeometry(self.left, self.top, 24, 21)
        button = QPushButton(self)
        # button.setToolTip('Stop video')
        rMyIcon = QtGui.QPixmap("Close_Box_Red")
        button.setIcon(QtGui.QIcon(rMyIcon))
        button.setIconSize(QtCore.QSize(20, 20))
        button.setStyleSheet('border-width: 0px;border-radius: 0px;')
        # button.setIcon('Close_Box_Red.ico')
        button.clicked.connect(self.on_click)
        button.move(0, 0)

    @pyqtSlot()
    def on_click(self):
        App.stop()


if __name__ == '__main__':
    print("starting the broadcast...")
    app = QApplication([])  # Новый экземпляр QApplication
    window0 = App("Test", 0, "F", 850, 50)  # Создаём объект класса App
    window1 = App("Test", 2, "L", 200, 50)
    window2 = App("Test", 3, "R", 525, 50)
    button_close = add_button_close(850, 50)

    window0.show()  # Показываем окно
    window1.show()  # Показываем окно
    window2.show()

    button_close.show()
    app.exec_()  # и запускаем приложение
