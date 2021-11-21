#----- A simple TCP client program in Python using send() function -----

'''import socket

print("Enter name:")
file_name = input()

# Create a client socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);

# Connect to the server
clientSocket.connect(("127.0.0.1", 9090));

# Send data to server
data = file_name;
clientSocket.send(data.encode());

# Receive data from server
dataFromServer = clientSocket.recv(1024);

# Print to the console
print(dataFromServer.decode());'''
from vidgear.gears import NetGear
import cv2

# activate Bidirectional mode
options = {"bidirectional_mode": True}

# define NetGear Client with `receive_mode = True` and defined parameter
client = NetGear(receive_mode=True, logging=True, **options)

# loop over
while True:

    # prepare data to be sent
    target_data = "Hi, I am a Client here."

    # receive data from server and also send our data
    data = client.recv(return_data=target_data)

    # check for data if None
    if data is None:
        break

    # extract server_data & frame from data
    server_data, frame = data

    # again check for frame if None
    if frame is None:
        break

    # {do something with the extracted frame and data here}

    # lets print extracted server data
    if not (server_data is None):
        print(server_data)

    # Show output window
    cv2.imshow("Output Frame", frame)

    # check for 'q' key if pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# close output window
cv2.destroyAllWindows()

# safely close client
client.close()