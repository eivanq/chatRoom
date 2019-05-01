import socket
import threading
import queue
import json
import ssl
#import time

'''Reserved or improper user name'''
invalidNameSet = ("SERVER", "CLIENT", "ASS")



def messageIn(connection, nickname):
    displayServerInfo('Thread: ' + threading.currentThread().getName() + ' has Started !!')
    while True:
        try:
            #msg = connection.recv(1024).decode()
            msg = connection.recv().decode()
            messageQueue.put(msg)
            displayServerInfo(f'Received Message from {nickname}: {msg}')
            
        except:
            connection.close()
            del connectionList[nickname]
            
            notifyMsg = {}
            notifyMsg["Name"] = "Server"
            notifyMsg["Message"] = f"[{nickname}] had been leaving this conversation!!"
            notifyMsg["Color"] = "red"
            messageQueue.put(json.dumps(notifyMsg))
            displayServerInfo(f'Connection from {nickname} has closed!!')
            return


def messageOut():
    while True:
        if not messageQueue.empty():
            msg = messageQueue.get()

            try:
                jsonMsg = json.loads(msg)
            except json.decoder.JSONDecodeError:
                displayServerInfo(f'Invalid Message Format (Convert to JSON failed): {msg}, pass it !!')
                continue
            except:
                displayServerInfo(f'Invalid Message Format: {msg}, pass it !!')
                continue

            if not "Name" in jsonMsg or not "Message" in jsonMsg:
                displayServerInfo(f'Invalid JSON Message Format: {msg}, pass it !!')
                continue
            
            displayServerInfo(f'Deliver Message: {msg}')
            for name in connectionList.keys():
                try:
                    if not name==jsonMsg["Name"]:
                        connectionList[name].send(msg.encode())
                except:
                    displayServerInfo("Exception while message OUT !!!")
                    connectionList[name].close()
                    

def checkNameValidation(nickname):
    if nickname.upper() in invalidNameSet:
        return False
    
    elif nickname in connectionList:
        return False
    
    else:
        return True


def displayServerInfo(msg):
    displayLock.acquire()
    print(msg)
    displayLock.release()


messageQueue = queue.Queue(256)
displayLock = threading.Lock()
connectionList = {}
Host = 'localhost'
Port = 23456

#SSL file path definition
server_cert = 'server_cafile/server.crt'
server_key = 'server_cafile/server.key'
client_certs = 'client_cafile/client.crt'


context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile=server_cert, keyfile=server_key)
context.load_verify_locations(cafile=client_certs)


serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serverSocket.bind((Host, Port))
serverSocket.listen(5)
print("Server Socket was created and now listening ...")


'''Only one thread had been created to handle message delivery for all user connection.'''
threading.Thread(name="messageOutManager",target=messageOut).start()

while True:

    try:
        sslSocket,addr = serverSocket.accept()
        displayServerInfo('Requesting Connection from ' + str(addr))
        conn = context.wrap_socket(sslSocket, server_side=True)
        nickname = conn.recv(256).decode()
        
    except ssl.SSLCertVerificationError:
        displayServerInfo("Invalid SSL Certification, reject connection!!")
        continue
    
    except:
        displayServerInfo("Unknown Error occured, reject connection!!")
        continue
    
    
    if checkNameValidation(nickname):
        connectionList[nickname] = conn
        '''Create a new thread to receive user message for each connection. '''
        threading.Thread(name=nickname+"Manager", target=messageIn,args=(conn,nickname)).start()
        
        notifyMsg = {}
        notifyMsg["Name"] = "Server"
        notifyMsg["Message"] = f"Welcom [{nickname}] to join our conversation !!"
        notifyMsg["Color"] = "red"

        messageQueue.put(json.dumps(notifyMsg))
        displayServerInfo("Connection from " + str(addr) + " has developed !!")
        
    else:
        errorMsg = {}
        errorMsg["Name"] = "Server"
        errorMsg["Message"] = "Invalid/Duplicated User Name, your connection would be closed!!"
        errorMsg["Color"] = "red"
        conn.send(json.dumps(errorMsg).encode())
        conn.close()
        displayServerInfo("Reject Connection from " + str(addr) + " and Close it!!")


    '''Show statuse of Current Active threads'''
    threadsNumber = threading.active_count()
    threadsList = []
    for thread in threading.enumerate():
        threadsList.append(thread.name)

    displayServerInfo(f"Active Threads Number: {threadsNumber}; {str(threadsList)}")
        
    
