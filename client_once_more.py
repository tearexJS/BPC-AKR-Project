import ssl
import queue
import cv2
import socket
import numpy as np
import time
import os
import json
import threading
import pyaudio
import keyboard
import struct
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent




import icons_rc

DATA_SIZE = 1024
HOST = '127.0.0.1'
PORT = 65000

audio_q = queue.Queue()
video_q = queue.Queue()
frames_q = queue.Queue()
terminate = False
FPS = 0


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        MainWindow.resize(721, 617)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/player.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(721, 566))
        self.centralwidget.setMaximumSize(QtCore.QSize(721, 566))
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.frame_main = QtWidgets.QFrame(self.centralwidget)
        self.frame_main.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_main.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_main.setObjectName("frame_main")
        self.frame_video = QtWidgets.QLabel()
        self.frame_video.setGeometry(QtCore.QRect(12, 12, 664, 384))
        #self.frame_video.setFrameShape(QtWidgets.QFrame.StyledPanel)
        #self.frame_video.setFrameShadow(QtWidgets.QFrame.Raised)
        #self.frame_video.setObjectName("frame_video")4
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.frame_video)
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame_video)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.openGLWidget_video = QtWidgets.QOpenGLWidget(self.frame_video)
        self.openGLWidget_video.setMinimumSize(QtCore.QSize(640, 360))
        self.openGLWidget_video.setObjectName("openGLWidget_video")
        self.gridLayout_2.addWidget(self.openGLWidget_video, 0, 0, 1, 1)
        self.layoutWidget = QtWidgets.QWidget(self.frame_main)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 450, 661, 91))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.playPB = QtWidgets.QPushButton(self.layoutWidget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.playPB.setIcon(icon1)
        self.playPB.setObjectName("playPB")
        self.horizontalLayout.addWidget(self.playPB)
        self.pausePB = QtWidgets.QPushButton(self.layoutWidget)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pausePB.setIcon(icon2)
        self.pausePB.setObjectName("pausePB")
        self.horizontalLayout.addWidget(self.pausePB)
        self.stopPB = QtWidgets.QPushButton(self.layoutWidget)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.stopPB.setIcon(icon3)
        self.stopPB.setObjectName("stopPB")
        self.horizontalLayout.addWidget(self.stopPB)
        self.layoutWidget1 = QtWidgets.QWidget(self.frame_main)
        self.layoutWidget1.setGeometry(QtCore.QRect(20, 400, 641, 24))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.volume_Slider = QtWidgets.QSlider(self.layoutWidget1)
        self.volume_Slider.setMinimumSize(QtCore.QSize(20, 5))
        self.volume_Slider.setMaximumSize(QtCore.QSize(120, 16777215))
        self.volume_Slider.setOrientation(QtCore.Qt.Horizontal)
        self.volume_Slider.setObjectName("volume_Slider")
        self.horizontalLayout_2.addWidget(self.volume_Slider)

        self.progress_Slider = QtWidgets.QSlider(self.layoutWidget1)
        self.progress_Slider.setOrientation(QtCore.Qt.Horizontal)
        self.progress_Slider.setObjectName("progress_Slider")
        self.horizontalLayout_2.addWidget(self.progress_Slider)

        self.gridLayout.addWidget(self.frame_main, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 721, 26))
        self.menubar.setObjectName("menubar")
        self.menuOpen = QtWidgets.QMenu(self.menubar)
        self.menuOpen.setObjectName("menuOpen")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.GetFilenames()
        self.menubar.addAction(self.menuOpen.menuAction())

        self.retranslateUi(MainWindow)
        self.menuOpen.triggered.connect(self.requestFile)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Pro Player Media Advanced Supreme"))
        self.playPB.setText(_translate("MainWindow", "Play"))
        self.pausePB.setText(_translate("MainWindow", "Pause"))
        self.stopPB.setText(_translate("MainWindow", "Stop"))
        self.menuOpen.setTitle(_translate("MainWindow", "Files"))


    # Nacitanie suborov dostupnych na servery
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
            self.actionOpen = QtWidgets.QAction(MainWindow)
            self.actionOpen.setObjectName("actionOpen")
            _translate = QtCore.QCoreApplication.translate
            self.actionOpen.setText(_translate("MainWindow", str(data['files'][i])))
            self.menuOpen.addAction(self.actionOpen)
            self.fileName.append(file)


    # Odoslanie poziadavky na prehranie suboru zo servera
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


# Stream audiocasti zvoleneho suboru
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


# Stream videocasti zvoleneho suboru
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

                    #images = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    #img = QtGui.QImage(images.data, images.shape[1], images.shape[0], QtGui.QImage.Format_RGB888)
                    #pix = QtGui.QPixmap.fromImage(img)
                    #pix = pix.scaled(664, 384, Qt.KeepAspectRatio, Qt.SmoothTransformation)


                    frames_q.put(frame)
                    begin = i + 2

# Stream videocasti zvoleneho suboru
def stream_video():
    cv2.namedWindow("Pro Player Media Advanced Supreme")
    cv2.moveWindow("Pro Player Media Advanced Supreme", 630, 230)
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

            cv2.imshow("Pro Player Media Advanced Supreme", frames_q.get())
            #images = frames_q.get()
            #ui.frame_video.setPixmap(images)
            #images2 = cv2.cvtColor(images, cv2.COLOR_BGR2RGB)
            #img = QtGui.QImage(images2.data, images2.shape[1], images2.shape[0], QtGui.QImage.Format_RGB888)
            #pix = QtGui.QPixmap.fromImage(img)
            #pix = pix.scaled(664, 384, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            #ui.frame_video.setPixmap(pix)

            #ui.frame = pix
            # loopTime = (time.time() - startTime) if (startTime > 0) else 0
            # print(loopTime, FPS)
            #

            if frames_q == 0:
                break


            if cv2.waitKey(1) & 0xff == ord('q'):
                break
            videoTime = (time.time() - startTime)

            #if val == 'eof' and audio_frame is None:
            #    break

            time.sleep(((frameCounter * (1 / 30)) - videoTime) if videoTime < (frameCounter * (1 / 30)) else 0)

        cv2.destroyAllWindows()




# Prijimanie audio/video blokov zo servera
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

def connection():
    # Pripojenie clienta na server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket = context.wrap_socket(client_socket, server_side=False, server_hostname=hostname)
    client_socket.connect((HOST, PORT))


if __name__ == "__main__":
        server_cert = 'files/server.crt'
        client_cert = 'files/client.crt'
        client_key = 'files/client.key'
        hostname = 'server'
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
        context.load_cert_chain(certfile=client_cert, keyfile=client_key)

        # Pripojenie clienta na server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket = context.wrap_socket(client_socket, server_side=False, server_hostname=hostname)
        client_socket.connect((HOST, PORT))

        # Vytvorenie zakladneho GUI
        app = QtWidgets.QApplication(sys.argv)
        MainWindow = QtWidgets.QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(MainWindow)
        MainWindow.show()
        sys.exit(app.exec_())


