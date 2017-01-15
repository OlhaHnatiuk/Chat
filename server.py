from socket import *
from threading import *
import sys
import queue
import time


class Server(Thread):
    def __init__(self, host, port):

        super(Server, self).__init__()

        self.host = host
        self.port = port
        self.buffer = 1024
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        self.connected = []
        self.nicknames  = []
        self.login_dict = {}
        # to from message
        self.action_queue = queue.Queue()

        self.turned_off = False

        try:
            
            self.sock.bind( (str(self.host), int(self.port)) )
            
            self.sock.listen(5)
            
            self.sock.setblocking(0)

        except Exception as e:
            print(e)
            self.turned_off = True

        if self.turned_off:
            print("Error, please, restart the server")
            sys.exit()
        self.Rlock = RLock()

        connection_creator = Thread(target=self.create_connection, daemon=True)
        receiver = Thread(target=self.receive_message, daemon=True)
        sender = Thread(target=self.send_message, daemon=True)

        connection_creator.start()
        receiver.start()
        sender.start()
        print("Server created")

        self.main_function()

    def create_connection(self):
        
        while True:
            try:
                
                self.Rlock.acquire()
                connection, address = self.sock.accept()
                connection.setblocking(0)
                if connection not in self.connected:
                    self.connected.append(connection)
                
            except:
                pass
            finally:
                self.Rlock.release()
            time.sleep(0.01)

    def receive_message(self):
        while True:
            if len(self.connected) > 0:
                #print("conncetion exists")
                for conn in self.connected:
                    try:
                        self.Rlock.acquire()
                        data = conn.recv(self.buffer)
                    except:
                        data = None
                    finally:
                        self.Rlock.release()

                    if data:
                        
                        message = data.decode('utf-8')
                        msg_type = message.split("#>", 1)[0]
                        if msg_type == "login":
                            #  login#>nickname#>host#>port
                            message = message.split("#>", 3)
                         
                            self.login_dict[message[1]] = conn
                            
                            self.action_queue.put( ('all', 'login', message[1]) )
                            self.nicknames.append(message[1])

                        elif msg_type == "logout":
                        	#  logout#>nickname
                        	message = message.split("#>", 3)
                        	try:
                        	    self.nicknames.remove(message[1])
                        	    self.connected.remove(self.login_dict[message[1]])
                        	    self.login_dict.pop(message[1], None)

                        	except:
                        		pass
                        	self.action_queue.put( ('all', 'logout', message[1]) )

                        else:

                        	# message#>target_nick#>sender_nick#>text
                        	message = message.split("#>", 3)
                        	self.action_queue.put( (message[1], message[2], message[3]) )


    def send_message(self):
        while True:
            if not self.action_queue.empty():
                (target, sender, message) = self.action_queue.get()
                if target == 'all':
                    self.send_to_all(sender, message)
                else:
                    self.send_to_special(target, sender, message)

                self.action_queue.task_done()
            else:
                time.sleep(0.01)

    def send_to_all(self, sender, message):
        data  = sender + "#>" + message
        for conn in self.connected:
            try:
                
                self.Rlock.acquire()
                
                conn.send(bytes(data, 'utf-8'))
                
            except Exception as e:
               
                print(e)
            finally:
                self.Rlock.release()

        if sender == "login":
            new_list = ""

            if self.nicknames:
                for i in self.nicknames:
                    if i is not message:
                        new_list += i + "#>"

            if new_list is not "":
                time.sleep(0.05)
                self.send_to_special(message, "insert", new_list)





    def send_to_special(self, target, sender, message):
        data = sender + "#>" + message
        address = self.login_dict[target]

        try:
            self.Rlock.acquire()
            #print("send")
            address.send(bytes(data, 'utf-8'))
            #print("send ok")
        except:
            pass
        finally:
            self.Rlock.release()


    def main_function(self):
        input_message = input()
        while input_message != "exit":
            input_message = input()
            continue
        print("Turn off")
        self.sock.close()
        sys.exit()

if __name__ == '__main__':
    server = Server('localhost', 65535)