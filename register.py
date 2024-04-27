import sys
import os
import shutil
from PyQt5 import QtWidgets
from PyQt5.QtCore import QModelIndex, QObject, Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QVBoxLayout
from PyQt5.uic import loadUi
import pandas as pd

dfExists = os.path.isfile(r'C:\SeniorDesign\gui\PhysicalDistressMonitor\profiles\profiles.csv')

if not dfExists:
    f = open(r'C:\SeniorDesign\gui\PhysicalDistressMonitor\profiles\profiles.csv', 'w')
    f.write('name,height,weight')
    f.close()

df = pd.read_csv('profiles/profiles.csv')

src = r'C:\SeniorDesign\gui\PhysicalDistressMonitor\keras\baseline.keras'

class Register(QDialog):
    def __init__(self, parent=None):
        super(Register, self).__init__(parent)
        loadUi('uis/register_dialog.ui', self)
        self.registerButton.clicked.connect(self.registerFunction)

        # Only allows up to 3 ints to be input
        # Weird bug right now will have to fix eventually
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
            button.clicked.connect(self.loginFunction(name))
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
        model = profile
        print(model)

app = QApplication(sys.argv)
mainwindow = Profiles()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedWidth(480)
widget.show()
app.exec()
