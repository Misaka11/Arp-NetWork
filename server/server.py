# coding=utf-8
# 通过socket建立网络连接的步骤:
# 至少需要2个套接字, server和client
# 需要建立socket之间的连接, 通过连接来进行收发data
# client 和 server连接的过程:
# 1. 建立server的套接字,绑定主机和端口,并监听client的连接请求
# 2. client套接字根据server的地址发出连接请求, 连接到server的socket上; client socket需要提供自己的 socket fd,以便server socket回应
# 3. 当server监听到client连接请求时, 响应请求, 建立一个新的线程, 把server fd 发送给client
# 而后, server继续监听其他client请求, 而client和server通过socket连接互发data通信
from PyQt5 import QtWidgets, uic,QtCore
from PyQt5.QtWidgets import QMessageBox
from serverUI import Ui_MainWindow
import socket, threading,sys,json,time

host = socket.gethostname()
port = 12345
server_addr = (host, port)
thread_alive = True

# oneConnection
def oneConn(conn,updated):
    while True:
        # data received from client
        data = conn.recv(1024).decode()
        if not data:
            break
        data = json.loads(data)
        # demanding handle
        updated.emit('receive data: '+str(data))
        updated.emit('searching...')
        destMac = 'xx'
        fo = open('arp.dat','r')
        try:
            for line in fo :
                destinfo = line.replace('\n','').split('    ')
                if destinfo[0]== data['destIP']:
                    destMac = destinfo[1]
        finally:
            fo.close()
        if destMac == 'xx' :
            updated.emit('not found the destMac')
        else:
            updated.emit('find the destMac='+destMac)

        # send back data to client
        rdata = destMac
        conn.send(json.dumps(rdata).encode('utf-8'))
        updated.emit('send back success')
    # connection closed
    conn.close()
    updated.emit('connect closed.')
# 
def run(updated):
    ss = socket.socket()  # create server socket
    ss.setblocking(False)
    ss.bind(server_addr)  #bind server addr
    updated.emit("socket binded to port " + str(port))
    ss.listen(10)  # listen the port, max connection 10
    updated.emit("socket is listening")

    # a forever loop until client wants to exit
    global thread_alive
    while thread_alive:
        try:
            # establish connection with client
            conn,addr = ss.accept()
            updated.emit('Connected from :'+(str)(addr[0])+":"+(str)(addr[1]))

            # start a new thread and return its identifier
            t1 = threading.Thread(target = oneConn,args=(conn,updated,))
            t1.start()
        except :
            time.sleep(0.2)
            pass
    ss.close()
    updated.emit("socket closed.")

class mywindow(QtWidgets.QMainWindow):
    updated = QtCore.pyqtSignal(str)
    def __init__(self):
        super(mywindow,self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.btnClicked)
        self.updated.connect(self.log) #important
    
    def log(self,msg):
        self.ui.textBrowser.append(msg)

    def btnClicked(self):
        global thread_alive
        if self.ui.pushButton.text() == 'Start':
            thread_alive = True
            t0 = threading.Thread(target = run,args = (self.updated,))
            t0.start()
            self.ui.pushButton.setText('Stop')
            self.ui.label.setText('server is working!')
        else:
            thread_alive = False
            self.ui.pushButton.setText('Start')
            self.ui.label.setText('I want to connect something...')
            pass
      

# 主函数，调用run
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = mywindow()
    win.show()
    sys.exit(app.exec())

