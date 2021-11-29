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


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        #MainWindow.resize(721, 617)
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
        self.frame_video = QtWidgets.QFrame(self.frame_main)
        self.frame_video.setGeometry(QtCore.QRect(12, 12, 664, 384))
        self.frame_video.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_video.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_video.setObjectName("frame_video")
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

        """
        WORK IN PROGRESS
        def changeValue(self, value):
             if value == 0:
                    self.label.setPixmap(QtGui.QPixmap('mute.png'))     
             elif 0 < value <= 30:
                    self.label.setPixmap(QtGui.QPixmap('min.png'))
             elif 30 < value < 80:
                    self.label.setPixmap(QtGui.QPixmap('med.png'))
             else :
                    self.label.setPixmap(QtGui.QPixmap('max.png'))"""

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
        #self.menuOpen.setObjectName("menuOpen")
        #MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        # self.actionOpen = QtWidgets.QAction(MainWindow)
        # self.actionOpen.setObjectName("actionOpen")
        self.GetFilenames()
        self.actionSearch = QtWidgets.QAction(MainWindow)
        #self.actionSearch.setObjectName("actionSearch")
        # self.menuOpen.addAction(self.actionOpen)
        # self.menuOpen.addAction(self.actionSearch)
        self.menubar.addAction(self.menuOpen.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Pro Player"))
        self.playPB.setText(_translate("MainWindow", "Play"))
        self.pausePB.setText(_translate("MainWindow", "Pause"))
        self.stopPB.setText(_translate("MainWindow", "Stop"))
        self.menuOpen.setTitle(_translate("MainWindow", "Files"))
        #self.actionOpen.setText(_translate("MainWindow", "Open"))
        #self.actionSearch.setText(_translate("MainWindow", "Search"))

    def GetFilenames(self):
        jsonReq = {'type': 'fileListReq'}
        client_socket.sendall(bytes(json.dumps(jsonReq), 'utf-8'))
        data = client_socket.recv(DATA_SIZE)

        if not data:
            os._exit(1)

        data = json.loads(data.decode("utf-8"))

        for i, file in enumerate(data['files']):
            self.actionOpen = QtWidgets.QAction(MainWindow)
            self.actionOpen.setObjectName("actionOpen")
            _translate = QtCore.QCoreApplication.translate
            self.actionOpen.setText(_translate("MainWindow", str(data['files'][i])))
            self.menuOpen.addAction(self.actionOpen)
            self.menuOpen.addAction(self.actionOpen)
            #client_socket.sendall(bytes(json.dumps({'type': 'fileReq', 'fileID': i}), 'utf-8'))

    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)


import icons_rc


DATA_SIZE = 1024
HOST = '127.0.0.1'
PORT = 65000

audio_q = queue.Queue()
video_q = queue.Queue()
frames_q = queue.Queue()
terminate = False
FPS = 0

#Nacitanie klucov zo suborov
def load_keys():
    with open('keys/pubkey.pem', 'rb') as f:
        pubKey = rsa.PublicKey.load_pkcs1(f.read())

    with open('keys/privkey.pem', 'rb') as f:
        privKey = rsa.PrivateKey.load_pkcs1(f.read())

    return pubKey, privKey

#Desifrovanie
def decrypt(cipherText, key):
    try:
        return rsa.decrypt(cipherText, key).encode('cp437')
    except:
        return False

def run():
    jsonReq = {'type': 'fileListReq'}
    client_socket.sendall(bytes(json.dumps(jsonReq), 'utf-8'))
    data = client_socket.recv(DATA_SIZE)

    if not data:
        os._exit(1)

    data = json.loads(data.decode("utf-8"))
    for i, file in enumerate(data['files']):
        print(i, ": ", file)

    selectedFileId = input("Select file to stream\n")

    while int(selectedFileId) > i:
        print(fg('red') + "ERROR: You choosen non-existent file. Please try again" + attr('reset'))
        selectedFileId = input("Select file to stream\n")

    # Request selected file from server
    client_socket.sendall(
        bytes(json.dumps({'type': 'fileReq', 'fileID': selectedFileId}), 'utf-8'))
    isLast = False

    client_socket.sendall(bytes(json.dumps({'type': 'fileReq', 'fileID': 0}), 'utf-8'))
    isLast = False

    video_thread = threading.Thread(
        target=stream_video, args=())
    audio_thread = threading.Thread(
        target=stream_audio, args=())
    video_parse_thread = threading.Thread(target=getFrames, args=())

    video_parse_thread.start()
    video_thread.start()
    audio_thread.start()

    blockCount = 0
    while not isLast:
        args = client_socket.recv(9)
        args = struct.unpack(">?II", args)
        isLast = args[0]
        lengthVideo = args[1]
        FPS = args[2]
        # print("isLast, videoLength from server, FPS from server", isLast, lengthVideo, FPS)
        video_q.put(receiveBlockPart(client_socket, lengthVideo))
        # print("videoFrames size: ", len(videoFrames))
        args = client_socket.recv(5)
        args = struct.unpack(">?I", args)
        isLast = args[0]
        lengthAudio = args[1]
        # print("AUDIO: isLast, audioLength from server: ", isLast, lengthAudio)
        audio_q.put(receiveBlockPart(client_socket, lengthAudio))
        # print("AudioFrames: ", len(audioFrames))

        blockCount += 1

    terminate = True

def stream_audio():
    p = pyaudio.PyAudio()
    CHUNK = 1024
    stream = p.open(format=p.get_format_from_width(2),
                    channels=2,
                    rate=44100,
                    output=True,
                    frames_per_buffer=CHUNK)
    while True:
        if(audio_q.qsize()):
            data = bytes(audio_q.get())
            if len(data):
                stream.write(data)
    

    #sys.exit()

def getFrames():
    while True:
        if video_q.qsize():
            blockOfFrames = video_q.get()
            frameSum = 0
            begin = 0
            for i in range(len(blockOfFrames)):
                if blockOfFrames[i]==0xFF and blockOfFrames[i+1] == 0xD9:
                    end = (i + 2) if i < len(blockOfFrames) - 2 else len(blockOfFrames)
                    frame = blockOfFrames[begin: end]
                    frameSum += len(frame)
                    frame = np.asarray(frame, dtype="uint8")
                    frame = cv2.imdecode(frame, 1)
                    frames_q.put(frame)
                    begin = i+2 



def stream_video():
    cv2.namedWindow('window')
    while True:

        if FPS > 0:
            displayTime = 1/FPS
            
        startTime = time.time()
        #fps,st,frames_to_count,cnt = (0,0,1,0)
        frameStart = 0
        frameCounter = 0
        while frames_q.qsize():
            frameCounter += 1
            frameTime = (time.time() - frameStart) if frameStart else displayTime
            frameStart = time.time()
            
            #displayTime1 = displayTime - deltaTime

            cv2.imshow("window",frames_q.get())
            # loopTime = (time.time() - startTime) if (startTime > 0) else 0
            # print(loopTime, FPS)
            # 
            videoTime = (time.time() - startTime)
            if cv2.waitKey(1) & 0xff == ord('q'):
                break
            
            
            time.sleep(((frameCounter * displayTime) - videoTime) if videoTime < (frameCounter * displayTime) else 0)                
                
def receiveBlockPart(client_socket, length):
        blockFrames = bytearray()
        while len(blockFrames)+DATA_SIZE < length:
            data = client_socket.recv(DATA_SIZE)
            if not data:
                break
            blockFrames.extend(data)
            
        data = client_socket.recv(length - len(blockFrames))
        blockFrames.extend(data)
        
        return blockFrames

if __name__ == "__main__":
    import sys

    #Connection to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.connect((HOST, PORT))

    #GUI create
    #app = QtWidgets.QApplication(sys.argv)
    #MainWindow = QtWidgets.QMainWindow()
    #ui = Ui_MainWindow()
    #ui.setupUi(MainWindow)
    #MainWindow.show()
    #sys.exit(app.exec_())
    run()