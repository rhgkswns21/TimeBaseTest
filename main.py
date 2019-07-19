import sys
import time
import datetime as date
import threading
import paho.mqtt.client as mqtt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QTextEdit, QGridLayout, QLabel
from PyQt5.QtCore import QCoreApplication

Device = []
device_type = ["M", "S1", "S2", "S3"]
check_device = [False, False, False, False]
time_info = []
timer = []

class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.imeiTEXTlist = []
        self.deviceLABELlist = []
        self.deviceOKcount = [0, 0, 0, 0, 0]
        self.deviceFailcount = [0, 0, 0, 0, 0]
        self.mqttFlag = False
        self.connectFlag = False

        print("make startBT")
        startBT = QPushButton('Start', self)
        startBT.clicked.connect(self.startBT_event)

        print("make logBT")
        logBT = QPushButton('Log', self)
        logBT.clicked.connect(self.logBT_event)

        print("make exitBT")
        exitBT = QPushButton('Quit', self)
        exitBT.clicked.connect(self.exitBT_event)

        print("make saveBT")
        saveBT = QPushButton('LogSave', self)
        saveBT.clicked.connect(self.saveBT_event)

        print("make Broker text")
        self.brokerTEXT = QLineEdit(self)
        self.brokerTEXT.setPlaceholderText('broker IP')

        print("make PANID text")
        self.panidTEXT = QLineEdit(self)
        self.panidTEXT.setPlaceholderText('PANID')

        print("make TestTime text")
        self.testimeTEXT = QLineEdit(self)
        self.testimeTEXT.setPlaceholderText('Total Time')

        print("make IntervalTime text")
        self.intervaltimeTEXT = QLineEdit(self)
        self.intervaltimeTEXT.setPlaceholderText('Time Interval')

        print("make Device info label")
        for i in range(len(device_type)):
            self.deviceLABEL = QLabel(self)
            self.deviceLABEL.setText(device_type[i] + "\t" + str(self.deviceOKcount[i]) + "    /    " + str(self.deviceFailcount[i]))
            self.deviceLABELlist.append(self.deviceLABEL)

        self.okfailLABEL = QLabel(self)
        self.okfailLABEL.setText("\tOK / Fail")

        self.totalLABEL = QLabel(self)
        self.totalLABEL.setText("Total\t" + str(self.deviceOKcount[4]) + "    /    " + str(self.deviceFailcount[4]))

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
        grid.addWidget(saveBT, 0, 3)
        grid.addWidget(self.brokerTEXT, 1, 0)
        grid.addWidget(self.panidTEXT, 1, 1)
        grid.addWidget(self.testimeTEXT, 1, 2)
        grid.addWidget(self.intervaltimeTEXT, 1, 3)
        for i in range(len(self.imeiTEXTlist)):
            grid.addWidget(self.imeiTEXTlist[i], 2, i)
        grid.addWidget(self.logbox, 3, 0, 6, 3)
        grid.addWidget(self.okfailLABEL, 3, 3, 1, 1)
        for i in range(len(device_type)):
            grid.addWidget(self.deviceLABELlist[i], 4+i, 3, 1, 1)
        grid.addWidget(self.totalLABEL, 8, 3, 1, 1)

        self.setWindowTitle('SHM Test Program')
        self.move(300, 300)
        self.resize(600, 300)
        self.show()

    def startBT_event(self):
        print("startBT click")
        self.log_appand("Start Button click")

        broker = self.brokerTEXT.text()
        time_info.append(self.testimeTEXT.text())
        time_info.append(self.intervaltimeTEXT.text())

        now_time = date.datetime.now()
        set_time = now_time + date.timedelta(minutes=int(time_info[0]))
        if time_info[0] == '0':
            send_text = "TestTime : " + now_time.strftime('%Y-%m-%d %H:%M:%S') + " - "
            self.log_appand(send_text)
        else:
            send_text = "TestTime : " + now_time.strftime('%Y-%m-%d %H:%M:%S') + " - " + set_time.strftime('%Y-%m-%d %H:%M:%S')
            self.log_appand(send_text)

        send_text = "Time Interval : " + time_info[1] + " Minutes"
        self.log_appand(send_text)
        send_text = "Broker IP : " + broker
        self.log_appand(send_text)
        print("broker : ", broker)

        Device.clear()
        for i in range(len(self.imeiTEXTlist)):
            Device.append(self.imeiTEXTlist[i].text())
        self.text_edit_start()

        self.connMQTTbroker(broker)
        time.sleep(1)
        self.intervalTimer()
        if time_info[0] != '0':
            time_list = threading.Timer(int(time_info[0])*60, self.testTimer)
            time_list.start()
            timer.append(time_list)

    def logBT_event(self):
        print("logBT click")
        self.log_appand("LOG Button click")
        Device.clear()
        for i in range(len(self.imeiTEXTlist)):
            Device.append(self.imeiTEXTlist[i].text())
        self.log_start()
        self.client.loop_stop()
        self.client.disconnect()

    def exitBT_event(self):
        print("exitBT click")
        self.client.disconnect()
        for i in timer:
            i.cancel()
        QCoreApplication.instance().quit()

    def saveBT_event(self):
        print("saveBT click")
        now_time = date.datetime.now().strftime('%Y-%m-%d %H%M%S')
        f = open(now_time + "log.txt", "a")
        save_text = self.logbox.toPlainText()
        f.write(save_text)
        f.close()

    def text_edit_start(self):
        for i in range(len(Device)):
            log_text = device_type[i] + " : " + Device[i]
            self.log_appand(str(log_text))

    def waitTimer(self):
        print("Wait Timer")
        for i in range(len(Device)):
            if check_device[i] == False:
                log_txt = str("FAIL Device : " + "\t" + device_type[i] + " " + Device[i])
                self.log_appand(log_txt)
        self.client.loop_stop()
        self.client.disconnect()

        for i in range(len(check_device)):
            if Device[i] != "":
                if check_device[i] == True:
                    self.deviceOKcount[i] = self.deviceOKcount[i] + 1
                else:
                    self.deviceFailcount[i] = self.deviceFailcount[i] + 1

        if False in check_device:
            self.deviceFailcount[4] = self.deviceFailcount[4] + 1
        else:
            self.deviceOKcount[4] = self.deviceOKcount[4] + 1

        for i in range(len(device_type)):
            self.deviceLABELlist[i].setText(device_type[i] + "\t" + str(self.deviceOKcount[i]) + "    /    " + str(self.deviceFailcount[i]))
        self.totalLABEL.setText("Total\t" + str(self.deviceOKcount[4]) + "    /    " + str(self.deviceFailcount[4]))


    def intervalTimer(self):
        print("interval timer")
        if self.mqttFlag == False:
            self.connMQTTbroker(self.brokerTEXT.text())
        time.sleep(1)
        self.sample_start()
        time_list = threading.Timer((int(time_info[1])*60)-2, self.intervalTimer)
        time_list.start()
        timer.append(time_list)
        set_time = date.datetime.now() + date.timedelta(minutes=int(time_info[1]))
        send_text = "Next Sampling Start Time : " + str(set_time.strftime('%Y-%m-%d %H:%M:%S'))
        self.log_appand(send_text)

    def testTimer(self):
        print("testTimer")
        self.log_appand("Test Complete")
        self.client.loop_stop()
        self.client.disconnect()
        for i in timer:
            i.cancel()

    def mqttconnectTimer(self):
        print("mqttconnectTimer")
        if self.mqttFlag == False:
            self.intervalTimer()

    def log_start(self):
        print("Log Start...")
        self.connMQTTbroker(self.brokerTEXT.text())
        for i in Device:
            if i != "":
                self.client.publish("Entity/SHM/Node/"+i+"/OTA",'{"nId":"'+i+'","nT":"SHM","status":{"OP":"TestLog"},"timestamp":'+str(int(time.time()))+'}')

    def sample_start(self):
        print("Sample_Start....")
        self.log_appand("Sampleing Start")
        PANID = self.panidTEXT.text()
        self.client.publish("Entity/SHM/Node/" + PANID + "/OTA", '{"nId":"' + PANID + '","nT":"SHM","status":{"OP":"Sample"},"timestamp":' + str(int(time.time())) + '}')
        for i in range(len(check_device)):
            if Device[i] == "":
                check_device[i] = True
            else:
                check_device[i] = False

        time_list = threading.Timer(120, self.waitTimer)
        # time_list = threading.Timer(30, self.waitTimer)    #Test Time
        time_list.start()
        timer.append(time_list)

    def connMQTTbroker(self, broker):
        print("Run connMQTTbroker")

        self.connectFlag = False
        time_list = threading.Timer(10, self.mqttconnectTimer)
        time_list.start()
        timer.append(time_list)

        if(self.mqttFlag == False):
            print("Connect Broker")
            self.log_appand("Connecting...")
            self.client = mqtt.Client()  # MQTT Client 오브젝트 생성

            self.client.on_log = self.on_log  # on_log callback 설정
            self.client.on_message = self.on_message  # on_message callback 설정
            self.client.on_connect = self.on_connect  # on_connect callback 설정
            self.client.on_disconnect = self.on_disconnect #on_disconnect callback 설정
            self.client.connect(broker)  # MQTT 서버에 연결

            self.connectFlag = True

            self.client.loop_start()    #MQTT Loop Start

    def on_log(self, *args):
        print(args[3])

    def on_connect(self, *args):
        print(args[3])
        if args[3] == 0:
            self.log_appand("Broker Connection Complete")
            self.mqttFlag = True
            for i in Device:
                if i != "":
                    time.sleep(1)
                    self.client.subscribe('Entity/SHM/Node/'+i+'/Device/Status')

    def on_disconnect(self, *args):
        print("Disconnect")
        self.log_appand("Disconnect Broker\n")
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
                send_text = "OK Device :" + "\t" + device_type[i] + " " + Device[i]
                self.log_appand(send_text)
        print("check deivce ", check_device)

        if False in check_device:
            print("list False")
        else:
            self.client.loop_stop()
            self.client.disconnect()

    def log_appand(self, text):
        now_time = date.datetime.now()
        print_text = str(now_time.strftime('%Y-%m-%d %H:%M:%S')) + "\t" + text
        self.logbox.append(print_text)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())

