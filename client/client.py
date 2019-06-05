from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QMessageBox
from clientUI import Ui_MainWindow
import sys,socket,threading,json

host = socket.gethostname()
port = 12345
client_addr = (host,port) #equal to server addr

destMac ='Not Found'

def send(updated,sourIP,sourMac,destIP):
    # client socket
    cs = socket.socket()
    cs.connect(client_addr)
    updated.emit('connect success!')
    data = {'sourIP' : sourIP,'sourMac':sourMac,'destIP':destIP}
    cs.send(json.dumps(data).encode('utf-8'))
    updated.emit('send data: ' + str(data))
    rdata = json.loads(cs.recv(1024).decode())
    global destMac
    if rdata == 'xx':
        updated.emit('not find destMac')
        destMac = 'Not Found'
    else:
        updated.emit('find destMac = '+str(rdata))
        destMac = rdata

    # close the connection
    cs.close()
    updated.emit('connect close.')

class mywindow(QtWidgets.QMainWindow):
    updated = QtCore.pyqtSignal(str)
    def __init__(self):
        super(mywindow,self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.btnClicked)
        self.updated.connect(self.log)

    def log(self,msg):
        self.ui.textEdit.append(msg)

    def btnClicked(self):
        sourIP = self.ui.lineEdit.text()
        sourMac = self.ui.lineEdit_2.text()
        destIP = self.ui.lineEdit_3.text()
        if sourIP == '':
            QMessageBox.information(self,"请填写完整信息","本机IP未填写")
            return
        if sourMac == '':
            QMessageBox.information(self,"请填写完整信息","本机Mac未填写")
            return
        if destIP == '':
            QMessageBox.information(self,"请填写完整信息","目的IP未填写")
            return
        
        # create a thread to send message
        t0 = threading.Thread(target = send,args=(self.updated,sourIP,sourMac,destIP))
        t0.start()
        t0.join()
        self.ui.lineEdit_4.setText(destMac)
        pass
    

if __name__ == "__main__":
    
    app = QtWidgets.QApplication([])
    win = mywindow()
    win.show()
    sys.exit(app.exec())
