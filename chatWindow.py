import tkinter as tk
import socket
import ssl
import threading
import queue
import json


class chatWindow(tk.Frame):
    
    def __init__(self, master, sock):
        tk.Frame.__init__(self, master)
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        #self.columnconfigure(0, weight=160)
        self.createWidgets()
        self.msgQueue = queue.Queue()
        self.sslsocket = sock
        self.updateMessageRoutine()
        self.nickname = ""
        

    def createWidgets(self):
        top=self.winfo_toplevel()
        top.rowconfigure(3, weight=1)
        top.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)
	
        self.messageAreaLabel = tk.Label(self)
        self.messageAreaLabel["text"] = "Message Area"
        self.messageAreaLabel.grid(row=0, column=0, sticky=tk.N+tk.W)

        self.messageArea = tk.Text(self, takefocus=0)
        self.messageArea.grid(row=1, column=0,columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W, padx =5, pady = 5)
        self.messageArea.configure(state="disable")
        self.messageArea.tag_config("MyWords", foreground="blue")
        self.messageArea.tag_config("redWords", foreground="red")

        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.messageArea.yview)
        self.scrollbar.grid(row=1, column=3, sticky='ns')

        self.messageArea.configure(yscrollcommand=self.scrollbar.set)
        #self.scrollbar.config(command=self.messageArea.yview)

        self.messageInputLabel = tk.Label(self)
        self.messageInputLabel["text"] = "Typing Message"
        self.messageInputLabel.grid(row=3, column=0, sticky=tk.N+tk.W)

        self.messageInput = tk.Text(self, height = 5, width=60)
        self.messageInput.grid(row=4, column=0, sticky=tk.N+tk.S+tk.E+tk.W, padx =5, pady = 5)
        self.messageInput.bind("<Return>", self.sendMessage)
        self.messageInput.bind("<Shift-Return>", self.inputMessageNewLine)
               
        self.button = tk.Button(self)
        self.button["text"] = "Send Message"
        self.button.grid(row=4, column=1)
        self.button.bind('<Button-1>', self.sendMessage)


    def sendMessage(self, event):
        msg = self.messageInput.get("1.0", tk.END)
        #msg = self.messageInput.get("1.0", "end-1c")
        msg = msg.rstrip()
        self.messageInput.delete("1.0", tk.END)

        if not msg == "" and not msg == None:
            self.messageArea.configure(state="normal")
            tag_begin = self.messageArea.index("end-1c")
            self.messageArea.insert(tk.END, self.nickname + ": " + msg +"\n")
            tag_end = self.messageArea.index("end-1c")
            #print(f"begin:{tag_begin}, end{tag_end}")

            self.messageArea.tag_add("MyWords", tag_begin, tag_end)
            self.messageArea.configure(state="disable")
            self.messageArea.see(tk.END)

            msgObject = {}
            msgObject['Name'] = self.nickname
            msgObject['Message'] = msg
            jsonMessage=json.dumps(msgObject)
            self.sslsocket.send(jsonMessage.encode())

        return 'break'


    def inputMessageNewLine(self, event):
        msg = self.messageInput.insert(tk.END, "\n")
        return 'break'

    
    def writeMessage(self, msg):
        self.msgQueue.put(msg)
        

    def setNicknamee(self, name):
        top=self.winfo_toplevel()
        top.title(name + "\'s chatting room") 
        self.nickname = name


    def updateMessageRoutine(self):
        try:
            while True:
                if not self.msgQueue.empty(): 
                    raw_msg = self.msgQueue.get()
                    json_msg =  json.loads(raw_msg)
                    output_msg = f'[{json_msg["Name"]}]: {json_msg["Message"]}'
                    self.messageArea.configure(state="normal")
                    
                    if "Color" in json_msg:
                        if json_msg["Color"] == "red":
                            tag_begin = self.messageArea.index("end-1c")
                            self.messageArea.insert(tk.END, output_msg +"\n")
                            tag_end = self.messageArea.index("end-1c")
                            self.messageArea.tag_add("redWords", tag_begin, tag_end)
                        else:
                            self.messageArea.insert(tk.END, output_msg +"\n")
                    else:
                        self.messageArea.insert(tk.END, output_msg +"\n")

                    self.messageArea.configure(state="disable")
                    self.messageArea.see(tk.END)
                else:
                    break
        except:
            pass
        self.after(200, self.updateMessageRoutine)
