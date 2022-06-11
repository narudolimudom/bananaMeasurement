from PyQt5 import QtGui
from PyQt5.QtWidgets import QCheckBox, QGroupBox,QApplication,QWidget, QMessageBox, QHBoxLayout,QGridLayout, QVBoxLayout, QPushButton, QFileDialog , QLabel, QRadioButton
import sys
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread, Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2
import main
import numpy as np



class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Banana measurement"
        self.top = 200
        self.left = 500
        self.width = 1080
        self.height = 720
        self.image = None
        self.imagePath = ''
        self.capture_flag = False

        self.InitWindow()

    def InitWindow(self):
        self.setWindowIcon(QtGui.QIcon(r'bananameasurementLogo.png'))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(800, 480)
        mainBox = QGridLayout()

        imageBox = QVBoxLayout()
        self.image_label = QLabel()
        default_image = QPixmap(r'defaultImage.png')
        default_image = default_image.scaled(760, 430)
        self.image_label.setPixmap(default_image)
        self.resize(default_image.width(),default_image.height())
        imageBox.addWidget(self.image_label)

        panelBox = QVBoxLayout()

        capture_btn = QPushButton('Capture from camera')
        capture_btn.setFixedSize(200,50)
        capture_btn.clicked.connect(self.exitProgram)
        


        

        visualBox = QHBoxLayout()
      


        visualBox.addStretch()

        process_btn = QPushButton('Start the process')
        process_btn.setFixedSize(200,50)
        process_btn.clicked.connect(self.startProcess)

        self.diameter_label = QLabel("Diameter :")
        self.length_label = QLabel("Length :")
        self.time_label = QLabel("Time used :")
        self.sizeNumber_label = QLabel("Size number : ")


        panelBox.addWidget(capture_btn)
 
        panelBox.addWidget(process_btn)
        panelBox.addWidget(self.diameter_label)
        panelBox.addWidget(self.length_label)
        panelBox.addWidget(self.sizeNumber_label)
        panelBox.addWidget(self.time_label)
        panelBox.addStretch()

        mainBox.addLayout(imageBox,0,0)
        mainBox.addLayout(panelBox,0,1)

        self.setLayout(mainBox)
        self.show()

    
    def exitProgram(self):
        sys.exit()



        

    def startProcess(self):
        self.diameter_label.setText('Diameter :')
        self.length_label.setText('Length :')
        self.time_label.setText('Time used :')

        
        th = main.ProcessWorker(self)
        th.changePixmap.connect(self.setImage)
        th.length.connect(self.setLength)
        th.diameter.connect(self.setDiameter)
        th.timeUsed.connect(self.setTimeUsed)
        th.sizeNumber.connect(self.setSizeNumber)
        th.start()
        
            
    @pyqtSlot(int)
    def setSizeNumber(self, sizeNumber):
        self.sizeNumber_label.setText('Size number : ' + str(sizeNumber))
    @pyqtSlot(QImage)
    def setImage(self, image):
        self.image_label.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot(float)
    def setLength(self, length):
        self.length_label.setText('Length : {0:.2f} cm'.format(length))

    @pyqtSlot(float)
    def setDiameter(self, diameter):
        self.diameter_label.setText('Diameter : {0:.2f} cm'.format(diameter))

    @pyqtSlot(float)
    def setTimeUsed(self, time):
        self.time_label.setText('Time used : {0:.2f} second'.format(time))


            

App = QApplication(sys.argv)
window = Window()
App.setStyle('Fusion')
sys.exit(App.exec())