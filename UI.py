import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pyupbit
import pandas as pd
import numpy as np
from PyQt5 import QtCore, QtGui
import os

class Stream(QtCore.QObject):
    """Redirects console output to text widget."""
    newText = QtCore.pyqtSignal(str)
 
    def write(self, text):
        self.newText.emit(str(text))

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

         # Note that this sentence can be printed to the console for easy debugging
        sys.stdout = Stream(newText=self.onUpdateText)
 
                 # Initialize a timer
        self.timer = QTimer(self)
                 # Connect the timer timeout signal to the slot function showTime ()
        self.timer.timeout.connect(self.fun)

    
    def fun(self):
        print("test")

 
    def onUpdateText(self, text):
        """Write console output to text widget."""
        cursor = self.process.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.process.setTextCursor(cursor)
        self.process.ensureCursorVisible()
 
    def closeEvent(self, event):
        """Shuts down application on close."""
        # Return stdout to defaults.
        sys.stdout = sys.__stdout__
        super().closeEvent(event)
 
  
    def setupUI(self):
        self.setWindowTitle("201744021 송휘")
        self.setWindowIcon(QIcon('icon.png'))
        
        ####################
        self.actxt = QLineEdit(self)
        self.actxt.setFixedWidth(200)
        
        acbtn = QPushButton("Access Key 저장", self)
        acbtn.setFixedWidth(150)
        acbtn.clicked.connect(self.acbtn_clicked)
        

        self.sctxt = QLineEdit(self)
        self.sctxt.setFixedWidth(200)

        scbtn = QPushButton("Secret Key 저장", self)
        scbtn.setFixedWidth(150)
        scbtn.clicked.connect(self.scbtn_clicked)

        titletxt = QLabel("사용할 전략: ",self)
        titletxt.setFixedWidth(120)
        titletxt.setFixedHeight(50)
        font = titletxt.font()
        font.setPointSize(15)
        font.setBold(True)
        titletxt.setFont(font)

        cb = QComboBox(self)
        cb.setFixedWidth(870)
        cb.addItem('전략 선택')
        cb.addItem('추세추종')
        cb.addItem('역추세')
        cb.addItem('RSI')
        cb.addItem('SMA크로스(5일선+30일선)')
        cb.addItem('이동평균수렴확산지수(MACD)')
        cb.activated[str].connect(self.onActivated)

        pushButton = QPushButton("자동매매시작")
        pushButton.clicked.connect(self.OnBtnClicked)

        self.process = QTextEdit(self, readOnly=True)
        self.process.setLineWrapColumnOrWidth(900)
        self.process.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.process.setFixedWidth(1000)
        self.process.setFixedHeight(200)
        self.process.move(30, 100)

        
        ####################


        acLayout = QHBoxLayout()
        acLayout.addWidget(self.actxt)
        acLayout.addWidget(acbtn)
        acLayout.addStretch(1)

        scLayout = QHBoxLayout()
        scLayout.addWidget(self.sctxt)
        scLayout.addWidget(scbtn)
        scLayout.addStretch(1)

        selectLayout = QHBoxLayout()
        selectLayout.addWidget(titletxt)
        selectLayout.addWidget(cb)
        selectLayout.addWidget(pushButton)
        selectLayout.addStretch(1)

        printLayout = QHBoxLayout()
        printLayout.addWidget(self.process)
        printLayout.addStretch(1)

        layout = QVBoxLayout()
        layout.addLayout(acLayout)
        layout.addLayout(scLayout)
        layout.addLayout(selectLayout)
        layout.addLayout(printLayout)
        layout.setStretchFactor(acLayout, 0)
        layout.setStretchFactor(scLayout, 0)
        layout.setStretchFactor(selectLayout, 0)
        layout.setStretchFactor(printLayout, 0)

        self.setLayout(layout)

    #자동매매 버튼 클릭시
    def OnBtnClicked(self):
        #access, secret 키 저장 여부 확인
        try:
            if os.path.isfile('upbit.txt'):
                print("Yes. it is a file")
            else:
                fp = open('upbit.txt','w')
                print(self.access,file = fp)
                print(self.secret,file = fp) 
                fp.close()
                print("hi")

            
        except AttributeError:
            msg = QMessageBox()
            msg.setWindowTitle("Key 미입력")
            msg.setText("Access Key와 Secret Key를 입력해주세요")
            msg.setStandardButtons(QMessageBox.Ok)
            result = msg.exec_()

    #백테스팅 기법 선택시
    def onActivated(self, text):
        print(text)
        if text == '추세추종':  
            import Momentum

        elif text == '역추세':
            import Momentum_reverse
        
        elif text == 'RSI지수':
            import RSI
            
        elif text == 'SMA크로스(5일선+30일선)':
            import SmaCross

        elif text == '이동평균수렴확산지수(MACD)':
            import MACD
            

    #access키 저장버튼 클릭
    def acbtn_clicked(self):
        print(self.actxt.text())
        self.access = self.actxt.text()

    #secret키 저장버튼 클릭
    def scbtn_clicked(self,actxt):
        print(self.sctxt.text())
        self.secret = self.sctxt.text()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()