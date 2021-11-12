import glob 
import socket
import argparse
import json

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65443        # Port to listen on (non-privileged ports are > 1023)

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--client', action="store_true",help='app works as a client')
    parser.add_argument('--server', action="store_true",help='app works as a client')
    args = parser.parse_args()
    if args.client:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            with open("img.png", "rb") as img:
                data = img.read()
                s.connect((HOST, PORT))
                s.sendall(data)


    elif args.server:
        files = glob.glob("*.png")
        filesDict = {}
        length = len(files)
        for i in range(length):
            files[i] = files[i]
        files = filesDict
        filesDict = json.dumps(filesDict, indent=4)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                
                data = conn.recv(1024)# snazim sa zistit ako funguje posielanie variable length message
                if data == "request":
                    s.sendall(bytes(filesDict))
                data = conn.recv(1024)
                        
                
                    
                
if __name__ == "__main__":
    main()
