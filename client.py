
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
PORT = 65000

audio_q = queue.Queue()
video_q = queue.Queue()
frames_q = queue.Queue()
terminate = False
FPS = 0
def stream_audio():

    p = pyaudio.PyAudio()
    CHUNK = 1024
    stream = p.open(format=p.get_format_from_width(2),
                    channels=2,
                    rate=44000,
                    output=True,
                    frames_per_buffer=CHUNK)
    while True:
        if(audio_q.qsize()):
            data = bytes(audio_q.get())
            if len(data):
                stream.write(data)
    

    #sys.exit()

def getFrames():
    begin = 0
    while True:
        if video_q.qsize():
            blockOfFrames = video_q.get()
            for i in range(len(blockOfFrames)):
                if blockOfFrames[i]==0xFF and blockOfFrames[i+1] == 0xD9:
                    frame = blockOfFrames[begin:i+2]
                    if len(frame):
                        frame = np.asarray(frame, dtype="uint8")
                        frame = cv2.imdecode(frame, 1)
                        frames_q.put(frame)
                    begin = i+2        

def stream_video():
    cv2.namedWindow('nigga')   
    while True:
        if FPS > 0:
            displayTime = 1/FPS
        if(frames_q.qsize()):
            startTime = 0
            #fps,st,frames_to_count,cnt = (0,0,1,0)
            while frames_q.qsize():
                deltaTime = time.time() - (startTime if startTime else time.time())
                print(deltaTime, displayTime-deltaTime)
                time.sleep(displayTime-deltaTime if displayTime-deltaTime > 0 else 0)
                
                # if cnt == frames_to_count:
                #     fps = (frames_to_count/(time.time()-st))
                #     st=time.time()
                #     cnt=0
                #     if fps>FPS:
                #         displayTime+=0.0015
                #     elif fps<FPS:
                #         displayTime-=0.0015
                #     else:
                #         pass
                # cnt += 1
          
                cv2.imshow("nigga",frames_q.get())
                startTime = time.time()
                if cv2.waitKey(1) & 0xff == ord('q'):
                        break
                
                
                
def receiveBlockPart(client_socket, length):
        blockFrames = bytearray()
        while len(blockFrames)+DATA_SIZE < length:
            # data = client_socket.recv(DATA_SIZE) TODO: fix size
            data = client_socket.recv(DATA_SIZE)
            if not data:
                break
            # print("TU")
            blockFrames.extend(data)
            
        data = client_socket.recv(length - len(blockFrames))
        blockFrames.extend(data)
        
        return blockFrames

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
isLast = False

video_thread = threading.Thread(
    target=stream_video, args=())
audio_thread = threading.Thread(
    target=stream_audio, args=())
video_parse_thread = threading.Thread(target=getFrames, args=())

video_parse_thread.start()
video_thread.start()
audio_thread.start()

while not isLast:
    args = client_socket.recv(9)
    args = struct.unpack(">?II", args)
    isLast = args[0]
    lengthVideo = args[1]
    FPS = args[2]
    #print("isLast, videoLength from server, FPS from server", isLast, lengthVideo, FPS)
    video_q.put(receiveBlockPart(client_socket, lengthVideo))
    #print("videoFrames size: ", len(videoFrames))
    args = client_socket.recv(5)
    args = struct.unpack(">?I", args)
    isLast = args[0]
    lengthAudio = args[1]
    #print("AUDIO: isLast, audioLength from server: ", isLast, lengthAudio)
    audio_q.put(receiveBlockPart(client_socket, lengthAudio))
    #print("AudioFrames: ", len(audioFrames))
    
terminate = True
