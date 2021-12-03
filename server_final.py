import cv2
import ssl
import socket
import wave
import struct
import queue
import os
import struct
import json
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

# extracting the sound from video by utilizing ffmpeg
def extract_sound(filename):
    command = "ffmpeg -i {} -ab 160k -ac 2 -ar 44100 -vn {}".format(
        filename, 'files/temp.wav')
    os.system(command)

# generating the video and audio packets
def generatePacket(FPS, isLast):
    block = block_q.get()
    video_packet = struct.pack(">?II", isLast, len(block.video), FPS) + block.video
    audio_packet = struct.pack(">?I", isLast, len(block.audio)) + block.audio
    return video_packet, audio_packet

# creating the blocks which will be transfered to client
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

# extracting the frames from the video utilizing the read function from cv2 lib
def video_stream_gen(vid):
    video = queue.Queue()
    while vid.isOpened():
        isNotEmpty, frame = vid.read()
        if not isNotEmpty:
            break
        _, frame = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        video.put(bytes(frame))
    vid.release()
    return video

# creating an audio chunk which is as long as the corresponding video length
def audio_stream(frame_count):
    audio = queue.Queue()
    wf = wave.open("files/temp.wav", 'rb')
    audioFramesPerVideoFrame = wf.getnframes() / frame_count
    audio_frames = wf.getnframes()
    while wf.tell() < audio_frames:
        audio.put(wf.readframes(int(audioFramesPerVideoFrame * BLOCK_SIZE)))
    wf.close()
    os.remove("files/temp.wav")
    return audio


files = [f for f in os.listdir("./files") if os.path.isfile(os.path.join("./files", f))]
filename = ""
# opening the connection
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print(type(server_socket))
server_socket.bind((HOST, PORT))
server_socket.listen()

server_cert = 'crt/server.crt'
server_key = 'crt/server.key'
client_certs = 'crt/client.crt'
# transforming the normal socket into ssl socket to ensure authetication and encryption
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile=server_cert, keyfile=server_key)
context.load_verify_locations(cafile=client_certs)

conn, addr = server_socket.accept()
conn = context.wrap_socket(conn, server_side=True)
with conn:
    print("Connected by", addr)
    while True:
        data = conn.recv(DATA_SIZE)
        if not data:
            break
        data = json.loads(data.decode("utf-8"))
        # sending the available files to client
        if data["type"] == "fileListReq":
            conn.sendall(bytes(json.dumps({'files': files}), "utf-8"))
        # extracting the requested file
        elif data["type"] == "fileReq":
            file_number = int(data["fileID"])
            filename = FILE_PATH + files[file_number]
            video = cv2.VideoCapture(filename)
            extract_sound(filename)
            FPS = int(video.get(cv2.CAP_PROP_FPS))
            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

            video_q = video_stream_gen(video)
            audio_q = audio_stream(frame_count)
            createBlock(video_q, audio_q)
            video_packet: bytes
            audio_packet: bytes
            # sending the packets to client
            while block_q.qsize():
                if block_q.qsize() == 1:
                    video_packet, audio_packet = generatePacket(FPS, True)
                else:
                    video_packet, audio_packet = generatePacket(FPS, False)

                conn.send(video_packet)
                conn.send(audio_packet)
    video.release()
    exit()