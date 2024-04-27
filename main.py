import re
import sys
import PyQt5
import serial
import asyncio
import pandas as pd
import tensorflow as tf
from tensorflow import keras
import numpy as np
import serial.tools.list_ports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from qasync import QEventLoop, asyncSlot
from bleak import BleakClient, BleakScanner


ports = serial.tools.list_ports.comports()
serialObj = serial.Serial()
liveData = [0, 0, 0, 0]
users = pd.read_csv('users.csv')
model_path = 'initializing_model.keras'
model = tf.keras.models.load_model(model_path)


def readSerial():
    global liveData
    if serialObj.isOpen() and serialObj.in_waiting:
        recentPacket = serialObj.readline()
        recentPacketString = recentPacket.decode('utf').rstrip('\n')
        liveData = [int(s) for s in re.findall(r'\b\d+\b', recentPacketString)]


class userSelect(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi('uix/user_select.ui', self)
        self.LaunchUserGUI = None
        global users
        usersList = []

        for user in users['Username']:
            usersList.append(str(user))
        self.userList.addItems(usersList)
        self.userList.setCurrentRow(0)

        self.newUserButton.clicked.connect(self.newUser)
        self.selectUserButton.clicked.connect(self.selectUser)
        self.show()

    def newUser(self):
        QApplication.closeAllWindows()
        self.LaunchUserGUI = newUser()

    def selectUser(self):
        global model
        global model_path

        userSelected = self.userList.item(self.userList.currentRow()).text()
        model_path = 'user_models/' + userSelected + '.keras'
        model = tf.keras.models.load_model(model_path)

        QApplication.closeAllWindows()
        self.LaunchUserGUI = startPage()


class newUser(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi('uix/create_user.ui', self)
        self.LaunchUserGUI = None
        self.addButton.clicked.connect(self.createUser)
        self.show()

    def createUser(self):
        global users
        global model
        global model_path
        username = self.nameInput.text()
        age = self. ageInput.value()
        height = self.heightInput.value()
        weight = self.weightInput.value()

        if len(username) == 0:
            warningBox = QMessageBox()
            warningBox.setText("Enter an alphanumeric username.")
            z = warningBox.exec_()

        elif username in users['Username'].values:
            warningBox = QMessageBox()
            warningBox.setText("Username already used.")
            z = warningBox.exec_()

        else:
            users.loc[len(users.index)] = [username, age, height, weight]
            users.to_csv('users.csv', index=False)

            unhealthy_data = pd.read_csv('Unhealthy Training Data - Random.csv')

            unhealthy_data['Pulse'] = unhealthy_data['Pulse'] / 300  # maximum human pulse
            unhealthy_data['Temp'] = unhealthy_data['Temp'] / 116  # maximum human temperature
            unhealthy_data['Oxygen'] = unhealthy_data['Oxygen'] / 100  # maximum human oxygen
            unhealthy_data['Hydration'] = unhealthy_data['Hydration'] / 512  # maximum hydration index

            X = unhealthy_data[unhealthy_data.columns[:-1]].values
            Y = unhealthy_data[unhealthy_data.columns[-1]].values

            model = keras.Sequential([
                keras.layers.Dense(4, activation="relu"),
                keras.layers.Dense(8, activation="relu"),
                keras.layers.Dense(8, activation="relu"),
                keras.layers.Dense(8, activation="relu"),
                keras.layers.Dense(4, activation="relu"),
                keras.layers.Dense(1, activation="sigmoid")
            ])

            model.compile(loss="binary_crossentropy", metrics=["accuracy"])
            model.fit(X, Y, epochs=20)

            model_path = 'user_models/' + username + '.keras'
            model.save(model_path)

            QApplication.closeAllWindows()
            self.LaunchUserGUI = startPage()


class startPage(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi('uix/start.ui', self)
        self.LaunchUserGUI = None
        self.show()
        self.liveButton.clicked.connect(self.liveBtnClick)
        self.trainButton.clicked.connect(self.trainBtnClick)

    def liveBtnClick(self):
        QApplication.closeAllWindows()
        self.LaunchUserGUI = livePortSelect()

    def trainBtnClick(self):
        QApplication.closeAllWindows()
        self.LaunchUserGUI = trainPortSelect()


class livePortSelect(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi('uix/port_select.ui', self)
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
        uic.loadUi('uix/port_select.ui', self)
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
        self.LaunchUserGUI = trainingMode()


class trainingMode(QMainWindow):
    global model
    global model_path
    recorded = pd.DataFrame(columns=['Pulse', 'Temp', 'Oxygen', 'Hydration', 'Label'])

    def __init__(self):
        super().__init__()
        self.LaunchUserGUI = None
        uic.loadUi('uix/connected_training.ui', self)
        self.pauseBtn.clicked.connect(self.pauseTraining)
        self.endBtn.clicked.connect(self.endTraining)
        self.show()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateGUI)  # Connect timeout signal to slot

    def pauseTraining(self):
        if self.pauseBtn.isChecked():
            self.timer.start(200)
            self.pauseBtn.setText("Pause")

        else:
            self.timer.stop()
            self.pauseBtn.setText("Start")

    def endTraining(self):
        X = self.recorded[self.recorded.columns[:-1]].values
        Y = self.recorded[self.recorded.columns[-1]].values
        model.fit(X, Y, epochs=20)
        model.save(model_path)
        self.timer.stop()
        QApplication.closeAllWindows()
        self.LaunchUserGUI = startPage()

    def updateGUI(self):
        readSerial()
        self.heart_rate.setText(str(liveData[0]))
        self.spo2.setText(str((liveData[1]/10)))
        self.gsr.setText(str(liveData[2]))
        self.temp.setText(str(liveData[3]))
        self.recorded.loc[len(self.recorded.index)] = [(liveData[0] / 300), (liveData[3] / 116), (liveData[1] / 1000),
                                                       (liveData[2] / 512), 0]
        print(self.recorded.loc[len(self.recorded.index) - 1])


class liveMode(QMainWindow):
    global liveData
    global model

    def __init__(self):
        super().__init__()
        self.LaunchUserGUI = None
        uic.loadUi('uix/live.ui', self)
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

        test_data = np.array([[[(liveData[0]/300), (liveData[3]/116), (liveData[1]/1000), (liveData[2]/512)]]])
        test_data = test_data.reshape(1, 4)

        # Predict and extract the prediction value
        risk_prediction = model.predict(test_data)
        risk_value = risk_prediction.flatten()[0]  # Flatten the array and get the first value

        # Assuming risk_value needs to be an integer for the GUI component
        risk_value = int(risk_value * 100)  # Scale the prediction value appropriately if needed
        self.risk.setValue(risk_value)  # Set the integer value to the GUI component


app = QApplication([])
window = userSelect()
app.exec()
sys.exit(app.exec_())
