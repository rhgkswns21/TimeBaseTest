import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QAction, qApp
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication

class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        btn = QPushButton('Quit', self)
        btn.move(50,50)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(self.on_click)

        # btn.click(QCoreApplication.instance().quit())

        self.setWindowTitle('My First Application')
        self.move(300, 300)
        self.resize(400, 200)
        self.show()

    def on_click(self):
        print('PyQt5 button click')
        QCoreApplication.instance().quit()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
