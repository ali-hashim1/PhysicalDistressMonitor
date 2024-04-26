import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QModelIndex, QObject, Qt
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.uic import loadUi
from PyQt5.QtGui import QDoubleValidator
import pandas as pd

df = pd.read_csv('profiles/profiles.csv')

class Register(QDialog):
    def __init__(self):
        super(Register, self).__init__()
        loadUi('uis/register_profile.ui', self)
        self.registerButton.clicked.connect(self.registerFunction)

        # Only allows up to 3 ints to be input
        # Weird bug right now will have to fix eventually
        self.heightLine.setInputMask('000')
        self.weightLine.setInputMask('000')

    def registerFunction(self):
        newEntry = {
            'name': self.nameLine.text(),
            'height': int(self.heightLine.text()),
            'weight': int(self.weightLine.text())
        }

        if len(df.index) < 20:
            print('Thank you for registering ' + newEntry['name'])
            df.loc[len(df.index)] = newEntry
            print(df)
            df.to_csv('profiles/profiles.csv', index=False)

app = QApplication(sys.argv)
mainwindow = Register()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedHeight(600)
widget.setFixedWidth(480)
widget.show()
app.exec()
