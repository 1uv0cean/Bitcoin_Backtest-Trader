import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pyupbit
import pandas as pd
import numpy as np


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()
  
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
        titletxt.setFixedWidth(170)
        titletxt.setFixedHeight(50)
        font = titletxt.font()
        font.setPointSize(15)
        font.setBold(True)
        titletxt.setFont(font)

        cb = QComboBox(self)
        cb.setFixedWidth(870)
        cb.addItem('전략 선택')
        cb.addItem('변동성 돌파')
        cb.addItem('변동성 돌파+상승장')
        cb.addItem('SMA크로스(5일선+30일선)')
        cb.addItem('이동평균수렴확산지수(MACD)')
        cb.activated[str].connect(self.onActivated)

        pushButton = QPushButton("자동매매시작")
        pushButton.clicked.connect(self.pushButtonClicked)
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

        layout = QVBoxLayout()
        layout.addLayout(acLayout)
        layout.addLayout(scLayout)
        layout.addLayout(selectLayout)
        layout.setStretchFactor(acLayout, 0)
        layout.setStretchFactor(scLayout, 0)
        layout.setStretchFactor(selectLayout, 0)

        self.setLayout(layout)

    #자동매매 버튼 클릭시
    def pushButtonClicked(self):
        #access, secret 키 저장 여부 확인
        try:
            print(self.access, self.secret)
        except AttributeError:
            msg = QMessageBox()
            msg.setWindowTitle("Key 미입력")
            msg.setText("Access Key와 Secret Key를 입력해주세요")
            msg.setStandardButtons(QMessageBox.Ok)
            result = msg.exec_()

    #백테스팅 기법 선택시
    def onActivated(self, text):
        print(text)
        if text == '변동성 돌파 기법':  
            ax = self.fig.add_subplot(111)
            ax.plot([1,2,3],[4,5,6])
            ax.grid()
            self.canvas.draw()
        
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
    window.showMaximized()
    app.exec_()