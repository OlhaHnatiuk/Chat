from _thread import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import *
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox
from PyQt5.QtWidgets import *
import sys, socket
from threading import *
from socket import *
import queue
import re
import select
import time



def msg_box(title, data):
	w = QWidget()
	QMessageBox.information(w, title, data)

queue = queue.Queue()

class myMain(QMainWindow):

    def __init__(self, otherClass):
        super().__init__()
        self.other = otherClass

    def closeEvent(self, event):
        #print("in event")
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            #   logout#>nick
            if self.other.logged:
                msg = "logout" + "#>" + self.other.Nickname
                global queue
                queue.put(bytes(msg, 'utf-8'))
            event.accept()
        else:
            event.ignore()


class Ui_MainWindow(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.nicks = ['all']
        self.logged = False
        self.Nickname = None
        self.MainWindow = None

    def setupUi(self, MainWindow):

        class textEditor(QTextEdit):
            def __init__(self, parent, outer):
                super().__init__(parent=parent)
                self.outer = outer

            def keyPressEvent(self, qKeyEvent):
                if qKeyEvent.key() == QtCore.Qt.Key_Return: 
                    self.outer.client_send_message()
                else:
                    super().keyPressEvent(qKeyEvent)


        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(662, 430)
        MainWindow.setFixedSize(662, 430)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QFrame(self.centralwidget)
        self.frame.setGeometry(QRect(10, 10, 651, 41))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label = QLabel(self.frame)
        self.label.setGeometry(QRect(10, 10, 131, 21))
        self.label.setObjectName("label")
        self.lineEdit = QLineEdit(self.frame)
        self.lineEdit.setGeometry(QRect(90, 10, 161, 21))
        self.lineEdit.setObjectName("lineEdit")
        self.label_2 = QLabel(self.frame)
        self.label_2.setGeometry(QRect(260, 10, 131, 21))
        self.label_2.setObjectName("label_2")
        self.pushButton_login = QPushButton(self.frame)
        self.pushButton_login.setGeometry(QRect(280, 9, 130, 23))
        self.pushButton_login.setObjectName("pushButton_login")

        #############################################################
        # Executes When The Send Message Button Is Clicked
        self.pushButton_login.clicked.connect(self.login_function)
        ############################################################



        self.frame_2 = QFrame(self.centralwidget)
        self.frame_2.setGeometry(QRect(10, 60, 301, 321))
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.textEdit = textEditor(self.frame_2, self)
        self.textEdit.setGeometry(QRect(10, 10, 281, 261))
        self.textEdit.setObjectName("textEdit")
        self.pushButton_3 = QPushButton(self.frame_2)
        self.pushButton_3.setGeometry(QRect(10, 280, 170, 31))
        self.pushButton_3.setObjectName("pushButton_3")




        #############################################################
        # Executes When The Send Message Button Is Clicked
        self.pushButton_3.clicked.connect(self.client_send_message)
        ############################################################


        self.combo = QComboBox(self.frame_2)
        self.combo.setGeometry(QRect(190, 280, 100, 31))
        self.combo.addItems(["all"])
        self.combo.setObjectName("combo")


        self.frame_3 = QFrame(self.centralwidget)
        self.frame_3.setGeometry(QRect(320, 60, 331, 321))
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.listWidget = QListWidget(self.frame_3)
        self.listWidget.setGeometry(QRect(10, 10, 311, 301))
        self.listWidget.setObjectName("listWidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 662, 29))
        self.menubar.setObjectName("menubar")
        self.menuAction = QMenu(self.menubar)
        self.menuAction.setObjectName("menuAction")
        MainWindow.setMenuBar(self.menubar)

        self.actionExit_2 = QAction(MainWindow)
        self.actionExit_2.setObjectName("actionExit_2")

        #######################################################
        # Executes When The SubMenu Item Exit Is Clicked
        self.actionExit_2.triggered.connect(self.logout_function)
        #######################################################

        self.menuAction.addAction(self.actionExit_2)
        self.menubar.addAction(self.menuAction.menuAction())
        
        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)


        
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QApplication.translate("MainWindow", 
        	"Chat Program", None, 1))
        self.label.setText(QApplication.translate("MainWindow", "Nickname:", 
        	None, 1))
        self.pushButton_3.setText(QApplication.translate("MainWindow", 
        	"Send Message", None, 1))
        self.menuAction.setTitle(QApplication.translate("MainWindow", 
        	"Menu", None, 1))
        self.actionExit_2.setText(QApplication.translate("MainWindow", 
        	"Exit", None, 1))
        self.pushButton_login.setText(QApplication.translate("MainWindow", "Login", 
            None, 1))

    #   logout#>nick
    def logout_function(self):
        
        #time.sleep(0.05)
        self.MainWindow.close()
        


    #   message#>target_nick#>sender_nick#>text
    def client_send_message(self):
        if not self.logged:
            msg_box("", "Please, log in")
        else:
            text = self.textEdit.toPlainText()
            if len(text) < 1:
                msg_box("", "Enter some text")
                return
            else:
                target = str(self.combo.currentText())
                msg = "message" + "#>" + target + "#>" + self.Nickname + "#>" + text 
                global queue
                queue.put(bytes(msg, 'utf-8'))
                self.textEdit.clear()
                msg_box("", "You send message to "+ target)

    #  login#>nickname#>host#>port
    def login_function(self):
        if not self.logged:
            nick = self.lineEdit.text()
            if len(nick) < 3:
                msg_box(nick, "Length of nick should be minimum 3 characters")
            elif not re.compile("^([A-Za-z0-9])+$").match(nick):
                msg_box(nick, "Nick should consist from letters and digits only")
            elif nick in self.nicks:
                msg_box(nick, "Nick is already used")
            else:
                msg = "login" + "#>" + nick + "#>" + str(self.host) + "#>" + str(self.port)
                global queue
                queue.put(bytes(msg, 'utf-8'))
                self.logged = True
                self.Nickname = nick
                msg_box(nick, "Login success!")
        else:
            msg_box("msg", "You are already logged in")



class Client(Thread):
    """docstring for Client"""
    def __init__(self, host, port, gui):
        super().__init__(daemon=False, target = self.run)
        self.host = host
        self.port = port
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((str(self.host), int(self.port)))
        #self.sock.send(bytes("all#>hi, 'utf-8'))
        self.buffer = 1024
        self.gui = gui
        self.Rlock = RLock()
        self.start()


    def run(self):
        inputs = [self.sock]
        outputs = [self.sock]
        while inputs:
            try:
                read, write, exceptional = select.select(inputs, outputs, inputs)
            # if server unexpectedly quit, this will get ValueError (file descriptor < 0)
            except ValueError:
                #print('Server error')
                #cos do error
                self.sock.close()
                break

            if self.sock in read:
                with self.Rlock:
                    try:
                        data = self.sock.recv(self.buffer)
                    except socket.error:
                        #messagebox.showinfo('Error', 'Server error has occurred. Exit app')
                        self.sock.close()
                        break

                if data:
                    message = data.decode('utf-8')
                    message_type = message.split("#>", 1)
                    #print(message)

                    if(message_type[0] == "login"):
                        self.gui.nicks.append(message_type[1])
                        self.gui.combo.clear()
                        self.gui.combo.addItems(self.gui.nicks)

                    elif(message_type[0] == "logout"):
                        self.gui.nicks.remove(message_type[1]);
                        self.gui.combo.clear()
                        self.gui.combo.addItems(self.gui.nicks)

                    elif(message_type[0] == "insert"):
                        listofnicks = message_type[1].split("#>")

                        for i in listofnicks:
                            if i:
                                self.gui.nicks.append(i)
                        self.gui.combo.clear()
                        self.gui.combo.addItems(self.gui.nicks)


                    else:
                        self.gui.listWidget.addItem(message+'\n')





            if self.sock in write:
                global queue
                if not queue.empty():
                    data = queue.get()
                    self.send_message(data)
                    #print("message send")
                else:
                    time.sleep(0.05)

            if self.sock in exceptional:
                #print('Server error')
                #messagebox.showinfo('Error', 'Server error has occurred. Exit app')
                self.sock.close()
                break


    def send_message(self, data):
        with self.Rlock:
            try:
                self.sock.send(data)
                #print("sock.send")
            except socket.error:
                #print('error')
                self.sock.close()
                #messagebox.showinfo('Error', 'Server error has occurred. Exit app')


        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    ui = Ui_MainWindow('localhost', 65535)
    MainWindow = myMain(ui)
    ui.setupUi(MainWindow)
    
    MainWindow.show()
    
    client = Client('localhost', 65535, ui)
    sys.exit(app.exec_())