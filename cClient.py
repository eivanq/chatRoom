import tkinter as tk
import socket
import ssl
import threading
import queue
import json
import time
import argparse
from tkinter import messagebox
from chatWindow import chatWindow


def messageInHandler(isock, msgUI):
    while True:
        try:
            #inString = isock.recv(1024).decode()
            inString = isock.recv().decode()
            msgUI.writeMessage(inString)
            #jsonString = json.loads(inString)
            #msgUI.write(f'[{jsonString["Name"]}]:{jsonString["Message"]}')
            
        except:
            isock.close()
            errorMsg = {}
            errorMsg["Name"] = "Client Warning Message"
            errorMsg["Message"] = "Connection has been closed, please re-execute this program again."
            errorMsg["Color"] = "red"
            msgUI.writeMessage(json.dumps(errorMsg))
            
            return

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        sslsocket.close()
        root.destroy()
        

parser = argparse.ArgumentParser()
parser.add_argument("-p", help="port number", default=23456, type=int)
parser.add_argument("-scert", help="Server Certification File", default="server_cafile/server.crt")
parser.add_argument("-ccert", help="Client Certification File", default="client_cafile/client.crt")
parser.add_argument("-ckey", help="Client Encryption Key", default="client_cafile/client.key")
myargs = parser.parse_args()


messageQueue = queue.Queue(100)
user_input = input("Please input your nick name (less than 12 words):")
nick_name = (user_input[:12]) if len(user_input) > 12 else user_input


#SSL Test
#server_cert = 'errasdserver.crt'
#client_cert = 'client.crt'
#client_key = 'client.key'
server_sni_hostname = 'example.com'
server_cert = myargs.scert
client_cert = myargs.ccert
client_key = myargs.ckey
#print(f'{server_cert}, {client_cert}, {client_key}, {myargs.p}')


try:
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
    context.load_cert_chain(certfile=client_cert, keyfile=client_key)

    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sslsocket = context.wrap_socket(sock, server_side=False, server_hostname=server_sni_hostname)
    sslsocket.connect(('localhost', myargs.p))
    sslsocket.send(nick_name.encode())

    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    appWindow = chatWindow(root, sslsocket)
    appWindow.setNicknamee(nick_name)
    threading.Thread(target=messageInHandler,args=(sslsocket, appWindow)).start()
    root.mainloop()
    
except ssl.SSLError:
    print("Invalid SSL Certification, connection has been rejected from server!!")
    
except FileNotFoundError:
    print("Certification File or Key not found !!")
    
except:
    print("Unknown Error occured during developing SSL socket connection !!")

