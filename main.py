import sys
import time
import datetime as date
import paho.mqtt.client as mqtt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QAction, qApp, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtCore import QCoreApplication

Device = []
device_type = ["M", "S1", "S2", "S3"]
check_device = [False, False, False, False]
timer = []

class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.imeiTEXTlist = []
        self.mqttFlag = False

        print("make startBT")
        startBT = QPushButton('Start', self)
        startBT.clicked.connect(self.startBT_event)

        print("make logBT")
        logBT = QPushButton('Log', self)
        logBT.clicked.connect(self.logBT_event)

        print("make exitBT")
        exitBT = QPushButton('Quit', self)
        exitBT.clicked.connect(self.exitBT_event)

        print("make Broker text")
        self.brokerTEXT = QLineEdit(self)
        self.brokerTEXT.setPlaceholderText('broker IP')

        print("make PANID text")
        self.panidTEXT = QLineEdit(self)
        self.panidTEXT.setPlaceholderText('PANID')

        print("make TestTime text")
        self.testimeTEXT = QLineEdit(self)
        self.testimeTEXT.setPlaceholderText('Minutes')

        print("make IntervalTime text")
        self.intervaltimeTEXT = QLineEdit(self)
        self.intervaltimeTEXT.setPlaceholderText('Minutes')

        print("make Device IMEI text")
        for i in range(len(device_type)):
            self.imeiTEXT = QLineEdit(self)
            self.imeiTEXT.setPlaceholderText(device_type[i] + 'IMEI')
            self.imeiTEXTlist.append(self.imeiTEXT)

        self.logbox = QTextEdit(self)
        self.logbox.setAcceptRichText(False)

        grid = QGridLayout()
        self.setLayout(grid)
        grid.addWidget(startBT, 0, 0)
        grid.addWidget(logBT, 0, 1)
        grid.addWidget(exitBT, 0, 2)
        grid.addWidget(self.brokerTEXT, 1, 0)
        grid.addWidget(self.panidTEXT, 1, 1)
        grid.addWidget(self.testimeTEXT, 1, 2)
        grid.addWidget(self.intervaltimeTEXT, 1, 3)
        for i in range(len(self.imeiTEXTlist)):
            grid.addWidget(self.imeiTEXTlist[i], 2, i)
        grid.addWidget(self.logbox, 3, 0, 1, 0)

        self.setWindowTitle('My First Application')
        self.move(300, 300)
        self.resize(500, 300)
        self.show()

    def test(self):
        print("Test Func")

    def startBT_event(self):
        print("startBT click")
        # 111.93.235.82
        broker = self.brokerTEXT.text()
        print("broker : ", broker)
        Device.clear()
        for i in range(len(self.imeiTEXTlist)):
            Device.append(self.imeiTEXTlist[i].text())
        # self.connMQTTbroker(broker)
        self.connMQTTbroker("111.93.235.82")
        print(Device)

    def logBT_event(self):
        print("logBT click")
        Device.clear()
        for i in range(len(self.imeiTEXTlist)):
            Device.append(self.imeiTEXTlist[i].text())
        self.log_start()
        self.client.disconnect()

    def exitBT_event(self):
        print("exitBT click")
        QCoreApplication.instance().quit()

    def log_start(self):
        print("Log Start...")
        # self.connMQTTbroker(self.brokerTEXT.text())
        self.connMQTTbroker("111.93.235.82")
        for i in Device:
            if i != "":
                time.sleep(1)
                self.client.publish("Entity/SHM/Node/"+i+"/OTA",'{"nId":"'+i+'","nT":"SHM","status":{"OP":"TestLog"},"timestamp":'+str(int(time.time()))+'}')



    def sample_start(self):
        print("Sample_Start....")
        PANID = self.panidTEXT.text()
        self.client.publish("Entity/SHM/Node/" + PANID + "/OTA", '{"nId":"' + PANID + '","nT":"SHM","status":{"OP":"Sample"},"timestamp":' + str(int(time.time())) + '}')
        for i in range(len(check_device)):
            if Device[i] == "":
                check_device[i] = True
            else:
                check_device[i] = False
        self.sample_start()

    def connMQTTbroker(self, broker):
        print("Run connMQTTbroker")
        if(self.mqttFlag == False):
            print("Connect Broker")
            self.client = mqtt.Client()  # MQTT Client 오브젝트 생성

            self.client.on_log = self.on_log  # on_log callback 설정
            self.client.on_message = self.on_message  # on_message callback 설정
            self.client.on_connect = self.on_connect  # on_connect callback 설정
            self.client.on_disconnect = self.on_disconnect #on_disconnect callback 설정
            self.client.connect(broker)  # MQTT 서버에 연결

            self.client.loop_start()

    def on_log(self, *args):
        print(args[3])

    def on_connect(self, *args):
        print(args[3])
        if args[3] == 0:
            self.mqttFlag = True
            for i in Device:
                if i != "":
                    time.sleep(1)
                    self.client.subscribe('Entity/SHM/Node/'+i+'/Device/Status')

    def on_disconnect(self, *args):
        print("Disconnect")
        self.mqttFlag = False

    # 서버에게서 PUBLISH 메시지를 받을 때 호출되는 콜백
    def on_message(self, mqttc, obj, msg):
        print("On_Message")
        topic = msg.topic
        mqtt_data = str(msg.payload)
        for i in range(len(Device)):
            if (Device[i] != "") and (topic.find(Device[i]) >= 0) and (mqtt_data.find('"GENERIC"') >= 0) and (check_device[i] == False):
                print(Device[i] + "  GENERIC")
                check_device[i] = True
        print("check deivce ", check_device)

        if False in check_device:
            print("list False")
        else:
            self.client.disconnect()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
