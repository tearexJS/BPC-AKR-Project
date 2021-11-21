import cv2
import imutils
import socket
import time
import base64
import threading
import wave
import pyaudio
import pickle
import struct
import sys
import queue
import os
import struct
import json
from dataclasses import dataclass

HOST = "1270.0.0.1"
PORT = 6555
DATA_SIZE = 1024
FILE_PATH = "files/"
BLOCK_SIZE = 10


@dataclass
class Block:
    video: bytes
    audio: bytes


block_q = queue.Queue()


def extract_sound(filename):
    command = "ffmpeg -i {} -ab 160k -ac 2 -ar 44100 -vn {}".format(
        filename, 'files/temp.wav')
    os.system(command)

def generatePacket(FPS):
    block = block_q.get()
    video_packet = struct.pack(">II", len(block.video), FPS) + block.video
    audio_packet = struct.pack(">I", len(block.audio)) + block.audio
    return video_packet, audio_packet

def createBlock(video_q, audio_q):
    video_list = bytearray()
    while video_q.qsize() and audio_q.qsize():
        
        for i in range(10):
            if i > video_q.qsize():
                break
            video_list.extend(video_q.get())
        block = Block(bytes(video_list), audio_q.get())
        block_q.put(block)
        video_list.clear()

def video_stream_gen(vid):

    WIDTH = 400
    video = queue.Queue()
    while vid.isOpened():
        isNotEmpty, frame = vid.read()
        if not isNotEmpty:
            break
        _,frame = cv2.imencode('.jpeg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
        video.put(bytes(frame))
    print('Player closed')
    BREAK = True
    vid.release()
    return video


def audio_stream(frame_count):

    audio = queue.Queue()
    wf = wave.open("files/temp.wav", 'rb')
    audioFramesPerVideoFrame = wf.getnframes()/frame_count
    audio_frames = wf.getnframes()
    while wf.tell() < audio_frames:
        audio.put(wf.readframes(int(audioFramesPerVideoFrame*BLOCK_SIZE)))
    wf.close()
    os.remove("files/temp.wav")
    return audio

def main():
    files = ["meme.mp4"]
    filename = ""
    server_socket = socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    conn, addr = server_socket.accept()
    with conn:
        print("Connected by", addr)
        while True:
            data = conn.recv(DATA_SIZE)
            if not data:
                break
            data = json.loads(data.decode("utf-8"))
            if data["type"] == "fileListReq":
                conn.sendall(bytes(json.dumps(files), "utf-8"))
            elif data["type"] == "fileReq":
                if(int(data["fileID"]) ==1):
                    filename = FILE_PATH+files[0]
                    video = cv2.VideoCapture("files/meme.mp4")
                    FPS = int(video.get(cv2.CAP_PROP_FPS))
                    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                    video_q = video_stream_gen(video)
                    audio_q = audio_stream(frame_count)
                    createBlock(video_q, audio_q)
                    video_packet, audio_packet = generatePacket()
                    conn.sendall(video_packet)
                    conn.sendall(audio_packet)
                    
if __name__ == "main":
    main()