import sys
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPalette, QColor

class Profiles(QDialog):
    def __init__(self, profiles):
        super(Profiles, self).__init__()
        # loadUi('profiles.ui', self)

        self.layout = QVBoxLayout(self)

        self.setStyleSheet('background-color:rgb(54, 54, 54)')

        for i in range(0, len(profiles)):
            button = QtWidgets.QPushButton(f'button {i}')
            button.setStyleSheet('background-color:rgb(255, 255, 255); font-size:20pt')
            button.setText(profiles[i])
            button.setFixedHeight(50)
            self.layout.addWidget(button)

        exitButton = QtWidgets.QPushButton('Register Now')
        exitButton.clicked.connect(self.closeFunction)
        self.layout.addWidget(exitButton)

    def closeFunction(self):
        QApplication.closeAllWindows()

profiles = {
    'name': ['Marshall', 'Ali', 'Javier', 'Nick', 'Josh', 'Mo'],
    'height': [150, 150, 150, 150, 150, 150],
    'weight': [180, 180, 180, 180, 180, 180]
}

df = pd.DataFrame(profiles)
df.to_csv('profiles/profiles.csv', index=False)

app = QApplication(sys.argv)
mainwindow = Profiles(profiles['name'])
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedHeight(600)
widget.setFixedWidth(480)
widget.show()
app.exec()
