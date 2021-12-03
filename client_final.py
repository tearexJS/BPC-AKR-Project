import ssl
import queue
import sys
import cv2
import socket
import numpy as np
import time
import os
import json
import threading
import pyaudio
import struct
from colored import fg, attr
import trace

DATA_SIZE = 1024
HOST = '127.0.0.1'
PORT = 65000

audio_q = queue.Queue()
video_q = queue.Queue()
frames_q = queue.Queue()
terminate = False
FPS = 0

# Streamovanie audiočasti zvoleného súboru
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
    p.terminate()
    #sys.exit()

# Získavanie snímkov z vyžiadaného videa
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
    #cv2.destroyAllWindows()
    sys.exit()

# Streamovanie videočasti zvoleného súboru
def stream_video():
    cv2.namedWindow('Pro Player Advanced')
    while True:
        if FPS > 0:
            displayTime = 1 / FPS

        startTime = time.time()
        frameStart = 0
        frameCounter = 0

        while frames_q.qsize():
            frameCounter += 1
            cv2.imshow("Pro Player Advanced", frames_q.get())

            if cv2.waitKey(1) & 0xff == ord('q'):
                break

            videoTime = (time.time() - startTime)
            time.sleep(((frameCounter * displayTime) - videoTime) if videoTime < (frameCounter * displayTime) else 0)
    cv2.destroyAllWindows()
    sys.exit()

# Prijímanie audio/video blokov zo serveru
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

server_cert = 'crt/server.crt'
client_cert = 'crt/client.crt'
client_key = 'crt/client.key'
hostname = 'server'
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
context.load_cert_chain(certfile=client_cert, keyfile=client_key)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

client_socket = context.wrap_socket(client_socket, server_side=False, server_hostname=hostname)
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

selectedFileId = input("Select file to stream\n")
while int(selectedFileId) > i:
        print(fg('red') + "ERROR: You choosen non-existent file. Please try again" + attr('reset'))
        selectedFileId = input("Select file to stream\n")


# Vyžiadanie súboru zo serveru
client_socket.sendall(
    bytes(json.dumps({'type': 'fileReq', 'fileID': selectedFileId}), 'utf-8'))
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
    video_q.put(receiveBlockPart(client_socket, lengthVideo))
    args = client_socket.recv(5)
    args = struct.unpack(">?I", args)
    isLast = args[0]
    lengthAudio = args[1]
    audio_q.put(receiveBlockPart(client_socket, lengthAudio))
    blockCount += 1

video_parse_thread.terminate()
video_thread.terminate()
audio_thread.terminate()
