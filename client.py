
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




DATA_SIZE = 1024
HOST = '127.0.0.1'
PORT = 9999


def stream_audio(audioFrames, terminate):

    p = pyaudio.PyAudio()
    CHUNK = 1024
    stream = p.open(format=p.get_format_from_width(2),
                    channels=2,
                    rate=44100,
                    output=True,
                    frames_per_buffer=CHUNK)
    while not audioFrames:
        pass
    while not terminate:
        stream.write(audioFrames)
    sys.exit()


def stream_video(videoFrames, FPS, terminate):
    displayTime = 1/FPS
    begin = 0
    while not videoFrames:
        pass
    while not terminate:
        for i in range(begin, len(videoFrames)):
            if(videoFrames[i] == 0xFF and videoFrames[i+1] == 0xD9):
                arr1 = videoFrames[begin:i+2]
                begin = i+2
                frame = cv2.imdecode(arr1, 1)
                cv2.imshow(frame)
                cv2.waitKey(int(displayTime*1000))


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

client_socket.connect((HOST, PORT))

jsonReq = {'type': 'fileListReq'}
client_socket.sendall(bytes(json.dumps(jsonReq), 'utf-8'))
data = client_socket.recv(DATA_SIZE)

if not data:
    os._exit(1)

data = json.loads(data.decode("utf-8"))
# Select file
for i, file in enumerate(data['files']):
    print(i, ": ", file)

selectedFileId = input("Select file to stream")

# Request selected file from server
client_socket.sendall(
    bytes(json.dumps({'type': 'fileReq', 'fileID': selectedFileId}), 'utf-8'))
isNotLast = True
terminate = False
FPS = None
videoFrames = bytearray()
audioFrames = bytearray()
video_thread = threading.Thread(
    target=stream_video, args=(videoFrames, FPS, terminate))
audio_thread = threading.Thread(
    target=stream_audio, args=(audioFrames, terminate))
video_thread.start()
audio_thread.start()
while isNotLast:
    args = client_socket.recv(9)
    args = struct.unpack(">?II", args)
    isNotLast = args[0]
    length = args[1]
    FPS = args[2]

    while len(videoFrames) < length:
        data = client_socket.recv(DATA_SIZE)
        if not data:
            break
        videoFrames.extend(data)

    args = client_socket.recv(5)

    args = struct.unpack(">?I", args)
    isNotLast = args[0]
    length = args[1]

    while len(audioFrames) < length:
        data = client_socket.recv(DATA_SIZE)
        if not data:
            break
        audioFrames.extend(data)
terminate = True
