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
import rsa
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from dataclasses import dataclass

HOST = "localhost"
PORT = 65000
DATA_SIZE = 1024
FILE_PATH = "files/"
BLOCK_SIZE = 10

@dataclass
class Block:
    video: bytes
    audio: bytes

block_q = queue.Queue()


#Generovanie klucov do suborov
def generate_keys():
    (pubKey, privKey) = rsa.newkeys(2048)
    with open('keys/pubkey.pem', 'wb') as f:
        f.write(pubKey.save_pkcs1('PEM'))

    with open('keys/privkey.pem', 'wb') as f:
        f.write(privKey.save_pkcs1('PEM'))

#Nacitanie klucov zo suborov
def load_keys():
    with open('keys/pubkey.pem', 'rb') as f:
        pubKey = rsa.PublicKey.load_pkcs1(f.read())

    with open('keys/privkey.pem', 'rb') as f:
        privKey = rsa.PrivateKey.load_pkcs1(f.read())

    return pubKey, privKey

#Sifrovanie
def encrypt(msg, key):
    return rsa.encrypt(msg.decode('cp437'), key)

#Podpis
def sign_sha1(msg, key):
    return rsa.sign(msg.encode('ascii'), key, 'SHA-1')

#Overenie podpisu
def verify_sha1(msg, signature, key):
    try:
        return rsa.verify(msg.encode('ascii'), signature, key) == 'SHA-1'
    except:
        return False



def extract_sound(filename):
    command = "ffmpeg -i {} -ab 160k -ac 2 -ar 44100 -vn {}".format(
        filename, 'files/temp.wav')
    os.system(command)

def generatePacket(FPS, isLast):
    block = block_q.get()
    video_packet = struct.pack(">?II", isLast, len(block.video), FPS) + block.video
    audio_packet = struct.pack(">?I", isLast,len(block.audio)) + block.audio
    return video_packet, audio_packet

def createBlock(video_q, audio_q):
    video_list = bytearray()
    while video_q.qsize() and audio_q.qsize():
        
        for i in range(BLOCK_SIZE):
            if video_q.qsize() == 0:
                break
            video_list.extend(video_q.get())
        block = Block(bytes(video_list), audio_q.get())
        block_q.put(block)
        video_list.clear()

def video_stream_gen(vid):

    video = queue.Queue()
    while vid.isOpened():
        isNotEmpty, frame = vid.read()
        if not isNotEmpty:
            break
        _,frame = cv2.imencode('.jpeg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
        video.put(bytes(frame))
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


generate_keys()
pubKey, privKey = load_keys()

files = [f for f in os.listdir("./files") if os.path.isfile(os.path.join("./files", f))]
filename = ""
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print(type(server_socket))
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
            conn.sendall(bytes(json.dumps({'files':files}), "utf-8"))
        elif data["type"] == "fileReq":
            file_number = int(data["fileID"])
            filename = FILE_PATH+files[file_number]
            video = cv2.VideoCapture(filename)
            extract_sound(filename)
            FPS = int(video.get(cv2.CAP_PROP_FPS))
            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))


            video_q = video_stream_gen(video)
            audio_q = audio_stream(frame_count)
            createBlock(video_q, audio_q)
            video_packet: bytes
            audio_packet: bytes

            while block_q.qsize():
                if block_q.qsize() == 1:
                    video_packet, audio_packet = generatePacket(FPS, True)
                else:
                    video_packet, audio_packet = generatePacket(FPS, False)

                    data_video = encrypt(video_packet, pubKey)
                    data_audio = encrypt(audio_packet, pubKey)

                    conn.send(data_video)
                    conn.send(data_audio)
