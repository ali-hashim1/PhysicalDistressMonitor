import pandas as pd
import tensorflow as tf
from tensorflow import keras
import numpy as np
import serial.tools.list_ports
import re
import sys, os
import PyQt5
import serial
import shutil

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5 import uic

ports = serial.tools.list_ports.comports()
serialObj = serial.Serial()
liveData = [0,0,0,0]
# model = tf.keras.models.load_model('keras/baseline.keras')
model = None

dfExists = os.path.isfile(r'C:\SeniorDesign\gui\PhysicalDistressMonitor\profiles\profiles.csv')

if not dfExists:
    f = open(r'C:\SeniorDesign\gui\PhysicalDistressMonitor\profiles\profiles.csv', 'w')
    f.write('name,height,weight')
    f.close()

df = pd.read_csv('profiles/profiles.csv')

src = r'C:\SeniorDesign\gui\PhysicalDistressMonitor\keras\baseline.keras'

def readSerial():
    global liveData
    if serialObj.isOpen() and serialObj.in_waiting:
        recentPacket = serialObj.readline()
        recentPacketString = recentPacket.decode('utf').rstrip('\n')
        liveData = [int(s) for s in re.findall(r'\b\d+\b', recentPacketString)]


class startPage(QMainWindow):

    def __init__(self):
       super().__init__()
       uic.loadUi('start.ui', self)
       self.LaunchUserGUI = None
       self.show()
       self.liveButton.clicked.connect(self.liveBtnClick)
       self.trainButton.clicked.connect(self.trainBtnClick)
       
       dialog = Profiles(self)
       dialog.setWindowTitle('Select Profile')
       dialog.setFixedWidth(480)
       dialog.exec()

    def liveBtnClick(self):
        QApplication.closeAllWindows()
        self.LaunchUserGUI = livePortSelect()

    def trainBtnClick(self):
        QApplication.closeAllWindows()
        self.LaunchUserGUI = trainModeSelect()


class trainModeSelect(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi('training_select.ui', self)
        self.LaunchUserGUI = None
        self.show()
        self.connectedButton.clicked.connect(self.connectedMode)
        self.unconnectedButton.clicked.connect(self.unconnectedMode)

    def connectedMode(self):
        QApplication.closeAllWindows()
        self.LaunchUserGUI = trainPortSelect()

    def unconnectedMode(self):
        QApplication.closeAllWindows()
        self.LaunchUserGUI = unconnectedTraining()


class livePortSelect(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi('port_select.ui', self)
        self.LaunchUserGUI = None
        self.selectButton.clicked.connect(self.setPort)

        portsList = []
        for onePort in ports:
            portsList.append(str(onePort))
        self.portList.addItems(portsList)
        self.portList.setCurrentRow(0)

        self.show()

    def setPort(self):
        portIndex = self.portList.currentRow()  # Get the current row index
        fullPortText = self.portList.item(portIndex).text()  # Get the full text of the item at the current row index
        portName = fullPortText.split(' ')[0]  # Split the text by spaces and take the first part, which should be the port name
        serialObj.port = portName  # Set the port of the serial object to just the port name (e.g., "COM5")
        serialObj.baudrate = 115200
        serialObj.open()
        QApplication.closeAllWindows()
        self.LaunchUserGUI = liveMode()


class trainPortSelect(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi('port_select.ui', self)
        self.LaunchUserGUI = None
        self.selectButton.clicked.connect(self.setPort)

        portsList = []
        for onePort in ports:
            portsList.append(str(onePort))
        self.portList.addItems(portsList)
        self.portList.setCurrentRow(0)

        self.show()

    def setPort(self):
        portIndex = self.portList.currentRow()  # Get the current row index
        fullPortText = self.portList.item(portIndex).text()  # Get the full text of the item at the current row index
        portName = fullPortText.split(' ')[0]  # Split the text by spaces and take the first part, which should be the port name
        serialObj.port = portName  # Set the port of the serial object to just the port name (e.g., "COM5")
        serialObj.baudrate = 115200
        serialObj.open()
        QApplication.closeAllWindows()
        self.LaunchUserGUI = connectedTraining()


class connectedTraining(QMainWindow):
    global model
    df = pd.DataFrame(columns=['Male', 'Female', 'Weight', 'Height', 'Age', 'Pulse', 'Temp', 'Oxygen', 'Hydration', 'Label'])

    def __init__(self):
        super().__init__()
        self.LaunchUserGUI = None
        uic.loadUi('connected_training.ui', self)
        self.pauseBtn.clicked.connect(self.pauseTraining)
        self.endBtn.clicked.connect(self.endTraining)
        self.show()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateGUI)  # Connect timeout signal to slot

    def pauseTraining(self):
        if self.pauseBtn.isChecked():
            self.timer.start(200)
            self.pauseBtn.setText("Pause")
            self.df.loc[len(self.df.index)] = [1, 0, 0.66, 0.69, 0.21, (liveData[0]/300), (liveData[3]/116), (liveData[1]/1000), (liveData[2]/512), 0]

        else:
            self.timer.stop()
            self.pauseBtn.setText("Start")

    def endTraining(self):
        X = self.df[self.df.columns[:-1]].values
        Y = self.df[self.df.columns[-1]].values
        model.fit(X, Y, epochs=20)
        QApplication.closeAllWindows()
        self.LaunchUserGUI = startPage()

    def updateGUI(self):
        readSerial()
        self.heart_rate.setText(str(liveData[0]))
        self.spo2.setText(str((liveData[1]/10)))
        self.gsr.setText(str(liveData[2]))
        self.temp.setText(str(liveData[3]))


class liveMode(QMainWindow):
    global liveData

    def __init__(self):
        super().__init__()
        self.LaunchUserGUI = None
        uic.loadUi('live.ui', self)
        self.show()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateGUI)  # Connect timeout signal to slot
        self.timer.start(200)

    def updateGUI(self):
        readSerial()
        self.heart_rate.setText(str(liveData[0]))
        self.spo2.setText(str((liveData[1]/10)))
        self.gsr.setText(str(liveData[2]))
        self.temp.setText(str(liveData[3]))

        test_data = np.array([[[1, 0, 0.66, 0.69, 0.21 , (liveData[0]/300), (liveData[3]/116), (liveData[1]/1000), (liveData[2]/512)]]])
        test_data = test_data.reshape(1, 9)

        # Predict and extract the prediction value
        risk_prediction = model.predict(test_data)
        risk_value = risk_prediction.flatten()[0]  # Flatten the array and get the first value

        # Assuming risk_value needs to be an integer for the GUI component
        risk_value = int(risk_value * 100)  # Scale the prediction value appropriately if needed
        self.risk.setValue(risk_value)  # Set the integer value to the GUI component

class Register(QDialog):
    def __init__(self, parent=None):
        super(Register, self).__init__(parent)
        uic.loadUi('uis/register_dialog.ui', self)
        self.registerButton.clicked.connect(self.registerFunction)

        # Mask is janky need different way to require int input
        self.heightLine.setInputMask('000')
        self.weightLine.setInputMask('000')

    def registerFunction(self):
        name = self.nameLine.text()
        height = self.heightLine.text()
        weight = self.weightLine.text()

        if not name and not height and not weight:
            print('Please input valid values')
        else:
            newEntry = {
                'name': name,
                'height': height,
                'weight': weight
            }

            if len(df.index) < 20:
                print('Thank you for registering ' + newEntry['name'])
                df.loc[len(df.index)] = newEntry
                df.to_csv('profiles/profiles.csv', index=False)

                dest = r'C:\SeniorDesign\gui\PhysicalDistressMonitor\keras'
                dest = dest + '\\' + name + '.keras'

                shutil.copyfile(src, dest)
            else:
                print('Maximum number of profiles')
            
            self.close()

class Profiles(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.setStyleSheet('background-color:rgb(54, 54, 54)')

        for i in range(0, len(df.index)):
            name = df.loc[i]['name']

            button = QtWidgets.QPushButton(f'button {i}')
            button.setStyleSheet('background-color:rgb(255, 255, 255); font-size:20pt')
            button.setText(name)
            button.setFixedHeight(50)
            button.clicked.connect(lambda checked, profile=name : self.loginFunction(profile))
            self.layout.addWidget(button)

        registerButton = QtWidgets.QPushButton('Register Now')
        registerButton.setStyleSheet('background-color:rgb(21, 96, 243); color:rgb(225, 225, 255); font-size:20pt')
        registerButton.clicked.connect(self.registerFunction)
        self.layout.addWidget(registerButton)

    def registerFunction(self):
        dialog = Register(self)
        dialog.setWindowTitle('Register')
        dialog.setFixedHeight(600)
        dialog.setFixedWidth(480)
        dialog.exec()

        self.close()

    def loginFunction(self, profile):
        model = tf.keras.models.load_model(f'keras/{profile}.keras')

        self.close()


app = QApplication([])
window = startPage()
app.exec()
sys.exit(app.exec_())
