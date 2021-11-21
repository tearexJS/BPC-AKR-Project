from vidgear.gears import VideoGear
from vidgear.gears import NetGear
'''import socket
import cv2
from playsound import playsound
from ffpyplayer.player import MediaPlayer
import os

# Create a stream based socket(i.e, a TCP socket)

# operating on IPv4 addressing scheme
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);

# Bind and listen
serverSocket.bind(("127.0.0.1", 9090));
serverSocket.listen();

def getVideoSource(source, width, height):
    cap = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap

def video_player(file_name):
    sourcePath = file_name
    camera = getVideoSource(sourcePath, 720, 480)
    player = MediaPlayer(sourcePath)
    while True:
        
        ret, frame = camera.read()
        audio_frame, val = player.get_frame()     

        if (ret == 0):
            print("End of video")
            break

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
        cv2.imshow(file_name, frame)
        if val != 'eof' and audio_frame is not None:
            frame, t = audio_frame
            print("Frame:" + str(frame) + " T: " + str(t))
        

    camera.release()
    cv2.destroyAllWindows()


# Accept connections
while  True:
    (clientConnected, clientAddress) = serverSocket.accept();
    print("Accepted a connection request from %s:%s"%(clientAddress[0], clientAddress[1]));

    dataFromClient = clientConnected.recv(1024)

    file_name = dataFromClient.decode()
    x = file_name.split(".")
    
    try:
        f = open("./files/" + file_name, "r")
    except:
        clientConnected.send("File Error".encode());
        break 

    if x[1] == "mp4":
        video_player("./files/" + file_name)
        # Send some data back to the client
        clientConnected.send("End Of File!".encode());
        break

    elif x[1] == "mp3":
        playsound("./files/" + file_name)
        # Send some data back to the client
        clientConnected.send("End Of File!".encode());
        break
    
    else:
        clientConnected.send("Not supported".encode());'''


# open any valid video stream(for e.g `test.mp4` file)
stream = VideoGear(source="files/meme.mp4").start()

# activate Bidirectional mode
options = {"bidirectional_mode": True}

# Define NetGear Server with defined parameters
server = NetGear(logging=True, **options)

# loop over until KeyBoard Interrupted
while True:

    try:
        # read frames from stream
        frame = stream.read()

        # check for frame if Nonetype
        if frame is None:
            break

        # {do something with the frame here}

        # prepare data to be sent(a simple text in our case)
        target_data = "Hello, I am a Server."

        # send frame & data and also receive data from Client
        recv_data = server.send(frame, message=target_data)

        # print data just received from Client
        if not (recv_data is None):
            print(recv_data)

    except KeyboardInterrupt:
        break

# safely close video stream
stream.stop()

# safely close server
server.close()
