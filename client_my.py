import ssl
import queue
import cv2
import imutils
import socket
import numpy as np
import time
import os
import sys
import base64
import json
import threading
import pyaudio
import pickle
import struct
from colored import fg, attr
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSlider, QStyle, QSizePolicy, QFileDialog
import sys
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from mpyg321.mpyg321 import MPyg321Player
from PyQt5.QtGui import QIcon, QPixmap



import icons_rc

DATA_SIZE = 1024
HOST = '127.0.0.1'
PORT = 65000

audio_q = queue.Queue()
video_q = queue.Queue()
frames_q = queue.Queue()
terminate = False
FPS = 0


class DisplayImageWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(DisplayImageWidget, self).__init__(parent)

        self.button = QtWidgets.QPushButton('Show picture')
        self.button.clicked.connect(self.show_image)
        self.image_frame = QtWidgets.QLabel()

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.button)

        self.menubar = QMenuBar()
        self.actionFile = self.menubar.addMenu("Files")
        self.GetFilenames()
        self.layout.addWidget(self.menubar, 0)
        self.menubar.triggered.connect(self.requestFile)

        self.layout.addWidget(self.image_frame)
        self.setLayout(self.layout)
        self.image_frame.resize(664,384)



    @QtCore.pyqtSlot()
    def show_image(self):
        self.image = cv2.imread('confused.jpg')
        self.image = QtGui.QImage(self.image.data, self.image.shape[1], self.image.shape[0], self.image.strides[0],QtGui.QImage.Format_BGR888)
        self.image_frame.setPixmap(QtGui.QPixmap.fromImage(self.image))

    def GetFilenames(self):
        jsonReq = {'type': 'fileListReq'}
        client_socket.sendall(bytes(json.dumps(jsonReq), 'utf-8'))
        data = client_socket.recv(DATA_SIZE)

        if not data:
            os._exit(1)

        data = json.loads(data.decode("utf-8"))
        self.fileId = []
        self.fileName = []

        for i, file in enumerate(data['files']):
            self.actionFile.addAction(str(data['files'][i]))
            #self.actionOpen.setObjectName("actionOpen")
            #_translate = QtCore.QCoreApplication.translate
            #self.actionOpen.setText(_translate("MainWindow", str(data['files'][i])))
            #self.menuOpen.addAction(self.actionOpen)
            self.fileName.append(file)

    def requestFile(self, action):
        txt = action.text()
        client_socket.sendall(
            bytes(json.dumps({'type': 'fileReq', 'fileID': self.fileName.index(action.text())}), 'utf-8'))
        self.isLast = False

        video_thread = threading.Thread(
            target=stream_video, args=())
        audio_thread = threading.Thread(
            target=stream_audio, args=())
        video_parse_thread = threading.Thread(target=getFrames, args=())

        video_parse_thread.start()
        video_thread.start()
        audio_thread.start()

        blockCount = 0
        while not self.isLast:
            args = client_socket.recv(9)
            args = struct.unpack(">?II", args)
            self.isLast = args[0]
            lengthVideo = args[1]
            self.FPS = args[2]
            # print("isLast, videoLength from server, FPS from server", isLast, lengthVideo, FPS)
            video_q.put(receiveBlockPart(client_socket, lengthVideo))
            # print("videoFrames size: ", len(videoFrames))
            args = client_socket.recv(5)
            args = struct.unpack(">?I", args)
            self.isLast = args[0]
            lengthAudio = args[1]
            # print("AUDIO: isLast, audioLength from server: ", isLast, lengthAudio)
            audio_q.put(receiveBlockPart(client_socket, lengthAudio))
            # print("AudioFrames: ", len(audioFrames))

            blockCount += 1
        self.terminate = True

def stream_audio():
    p = pyaudio.PyAudio()
    CHUNK = 1024
    stream = p.open(format=p.get_format_from_width(2),
                    channels=2,
                    rate=44100,
                    output=True,
                    frames_per_buffer=CHUNK)
    while True:
        if (audio_q.qsize()):
            data = bytes(audio_q.get())
            if len(data):
                stream.write(data)

def getFrames():
    while True:
        if video_q.qsize():
            blockOfFrames = video_q.get()
            frameSum = 0
            begin = 0
            for i in range(len(blockOfFrames)):
                if blockOfFrames[i] == 0xFF and blockOfFrames[i + 1] == 0xD9:
                    end = (i + 2) if i < len(blockOfFrames) - 2 else len(blockOfFrames)
                    frame = blockOfFrames[begin: end]
                    frameSum += len(frame)
                    frame = np.asarray(frame, dtype="uint8")
                    frame = cv2.imdecode(frame, 1)
                    frames_q.put(frame)
                    begin = i + 2

def stream_video():
    cv2.namedWindow('window')
    while True:
       # if FPS > 0:
       #     displayTime = 1 / FPS

        startTime = time.time()
        # fps,st,frames_to_count,cnt = (0,0,1,0)
        #frameStart = 0
        global frames_q
        frameCounter = 0
        while frames_q.qsize():
            frameCounter += 1
            #frameTime = (time.time() - frameStart) if frameStart else displayTime
            #frameStart = time.time()

            # displayTime1 = displayTime - deltaTime

        #    cv2.imshow("window", frames_q.get())
            DisplayImageWidget.image = cv2.imread((frames_q.get()))
            DisplayImageWidget.image = QtGui.QImage(DisplayImageWidget.image.data, DisplayImageWidget.image.shape[1], DisplayImageWidget.image.shape[0], DisplayImageWidget.image.strides[0],
                                      QtGui.QImage.Format_BGR888)
            DisplayImageWidget.image_frame.setPixmap(QtGui.QPixmap.fromImage(DisplayImageWidget.image))


            # loopTime = (time.time() - startTime) if (startTime > 0) else 0
            # print(loopTime, FPS)
            #

            if cv2.waitKey(1) & 0xff == ord('q'):
                break
            videoTime = (time.time() - startTime)

            time.sleep(((frameCounter * (1 / 30)) - videoTime) if videoTime < (frameCounter * (1 / 30)) else 0)


def receiveBlockPart(client_socket, length):
    blockFrames = bytearray()
    while len(blockFrames) + DATA_SIZE < length:
        data = client_socket.recv(DATA_SIZE)
        if not data:
            break
        blockFrames.extend(data)

    data = client_socket.recv(length - len(blockFrames))
    blockFrames.extend(data)

    return blockFrames

if __name__ == "__main__":
    import sys

    server_cert = 'files/server.crt'
    client_cert = 'files/client.crt'
    client_key = 'files/client.key'
    hostname = 'server'
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
    context.load_cert_chain(certfile=client_cert, keyfile=client_key)

    # Connection to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket = context.wrap_socket(client_socket, server_side=False, server_hostname=hostname)
    client_socket.connect((HOST, PORT))

    # GUI create
    app = QtWidgets.QApplication(sys.argv)
    display_image_widget = DisplayImageWidget()
    display_image_widget.show()
    sys.exit(app.exec_())

