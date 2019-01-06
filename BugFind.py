import logging
import pyperclip,pickle,sys, re, webbrowser, xlrd, os, json, requests, time, threading,signal,image_rc
from PyQt5.QtWidgets import (QApplication, QWidget,QCalendarWidget, QLabel, QListView, QSystemTrayIcon, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QDesktopWidget, QDialog, QAction, QMenu, QCompleter, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QFont, QPixmap, QPalette
from PyQt5.QtCore import * 
from PyQt5.Qt import *
from time import sleep
from atexit import register

from datetime import datetime,timedelta
from xlrd import xldate_as_tuple
from bs4 import BeautifulSoup

import queue
from ph import *

class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        self.style = """QPushButton{background-color:rgba(50, 50, 50, 40);}
                        QLabel{color: rgb(0, 100, 255);}
                        QCheckBox{color: rgb(0, 100, 255);}
                        QLineEdit{background-color: rgba(50, 50, 50, 20);color:rgb(0, 85, 255);}
                        QListView{background-color: rgba(230, 238, 243, 220);color:rgb(0, 85, 255);}
                         searchWindow{ background:pink; }
                         #set{color:#008300;}
                         searchEdit{background-color:#f0f0f0;color:#393939;selection-color:#ffff7f;}
                         up-widget{background-color: rgb(71, 71, 106);}
                         buttom-widget{background-color: rgb(71, 71, 106);}
                         search-widget{background-color: rgb(71, 71, 106);}
                         #loginWindow{background-color: rgb(71, 71, 106);}
                         """
        self.setStyleSheet(self.style)
        self.setWindowFlags(Qt.FramelessWindowHint)  #去掉窗口顶部title栏
        self.setAttribute(Qt.WA_TranslucentBackground, True)  #设置窗口透明
        self.center()
        self.setWindowTitle('Bug查询工具')
        self.setWindowIcon(QIcon(':image/icons/window_icon.png'))
        self.setObjectName('searchWindow')

        font = QFont()
        '''搜索栏'''
        self.widgetMain = QWidget(self)
        self.widgetMain.setGeometry(0, 31, 800, 69)
        self.widgetMain.setObjectName('search-widget')
        palette1 = QPalette()
        palette1.setBrush(self.widgetMain.backgroundRole(), QBrush(QPixmap(':image/icons/searchMain.png')))
        self.widgetMain.setPalette(palette1)
        self.widgetMain.setAutoFillBackground(True)

        label = QLabel('', self.widgetMain)
        #label.setTextFormat(QtCore.Qt.RichText)
        label.setPixmap(QPixmap(":image/icons/mac.png"))
        # label.setStyleSheet(" border: 1px solid rgb(255, 255, 0);")
        label.setObjectName("label")
        label.setGeometry(0, 0, 40, 30)
        font.setFamily('等线 Light')
        font.setPointSize(18)
        label.setFont(font)

        self.set = QPushButton(self.tr('Ŏ'), self.widgetMain)
        self.set.setGeometry(40, 0, 30, 30)
        self.set.setObjectName('set')
        font.setPointSize(20)
        self.set.setFont(font)


        self.searchEdit = QLineEdit(self.widgetMain)
        self.searchEdit.setObjectName('searchEdit')
        self.searchEdit.setGeometry(71, 1, 698, 28.5)
        self.searchEdit.setStyleSheet(" border: 1px solid rgb(181, 53, 255);")
        font.setFamily('Times New Roman')
        font.setPointSize(12)
        self.searchEdit.setFont(font)
        self.searchEdit.setFocus()


        self.listnum = QLabel('', self.widgetMain)
        self.listnum.setGeometry(660, 5, 100, 20)
        self.listnum.setStyleSheet("font: 14pt \"Times New Roman\";\n"
        "text-decoration: underline;""color:rgb(0, 85, 255);")
        self.listnum.setAlignment(Qt.AlignCenter)   #居中显示
        self.listnum.setObjectName('listnum')

        self.btn_close = QPushButton('×', self.widgetMain)     #self在后面？：定义一个按钮名称为：关闭，并定义他的容器为self，也就是放到窗口里
        self.btn_close.setObjectName('close')
        self.btn_close.setStyleSheet("color: rgb(6, 124, 197);")
        self.btn_close.setGeometry(770, 0, 30, 30)
        font.setFamily('等线 Light')
        font.setPointSize(30)
        self.btn_close.setFont(font)


        #第二行，左侧grid
        tgrid = QGridLayout()
        font.setFamily('宋体')
        font.setPointSize(11)

        statuses = QLabel('Status:')
        statuses.setMinimumSize(12, 12)
        statuses.setFont(font)
        self.checkClosed = QCheckBox('Closed')
        self.checkClosed.setMinimumSize(14, 14)
        self.checkDelayed = QCheckBox('Delayed')
        self.checkDelayed.setMinimumSize(14, 14)
        self.checkDevfixed = QCheckBox('Devfixed')
        self.checkDevfixed.setMinimumSize(14, 14)
        self.checkNew = QCheckBox('New')
        self.checkNew.setMinimumSize(14, 14)
        self.checkRejected = QCheckBox('Rejected')
        self.checkRejected.setMinimumSize(14, 14)
        self.checkReOpen = QCheckBox('ReOpen')
        self.checkReOpen.setMinimumSize(14, 14)

        priorities = QLabel('Prio.:')
        priorities.setMinimumSize(14, 14)
        priorities.setFont(font)
        self.check5 = QCheckBox('阻碍')
        self.check5.setMinimumSize(14, 14)
        self.check4 = QCheckBox('严重')
        self.check4.setMinimumSize(14, 14)
        self.check3 = QCheckBox('正常')
        self.check3.setMinimumSize(14, 14)
        self.check2 = QCheckBox('轻微')
        self.check2.setMinimumSize(14, 14)
        self.check1 = QCheckBox('建议')
        self.check1.setMinimumSize(14, 14)

        tgrid.addWidget(statuses, 0, 0)
        tgrid.addWidget(self.checkNew, 0, 1)
        tgrid.addWidget(self.checkReOpen, 0, 2)
        tgrid.addWidget(self.checkDevfixed, 0, 3)
        tgrid.addWidget(self.checkDelayed, 0, 4)
        tgrid.addWidget(self.checkClosed, 0, 5)
        tgrid.addWidget(self.checkRejected, 0, 6)
        tgrid.addWidget(priorities, 1, 0)
        tgrid.addWidget(self.check1, 1, 1)
        tgrid.addWidget(self.check2, 1, 2)
        tgrid.addWidget(self.check3, 1, 3)
        tgrid.addWidget(self.check4, 1, 4)
        tgrid.addWidget(self.check5, 1, 5)

		#第二行，右侧vbox_date
        search_date1 = QLabel('Date Updated:')
        search_date1.setFont(font)
        search_date1.setFixedSize(110,15)
        self.start_date1 = MyLineEdit()
        self.start_date1.setObjectName('start_date1')
        self.start_date1.setStyleSheet("color: rgb(0, 85, 255);""background-color: rgba(244, 244, 244, 255);")
        self.start_date1.setFixedSize(70,15)

        time_x1 = QLabel('—')
        time_x1.setFixedSize(15,15)
        self.end_date1 = MyLineEdit()
        self.end_date1.setObjectName('end_date1')
        self.end_date1.setStyleSheet("color: rgb(0, 85, 255);""background-color: rgba(244, 244, 244, 255);")
        self.end_date1.setFixedSize(70,15)

        hbox_date1 = QHBoxLayout()
        hbox_date1.addSpacing(20)
        hbox_date1.addWidget(search_date1)
        hbox_date1.addWidget(self.start_date1)
        hbox_date1.addWidget(time_x1)
        hbox_date1.addWidget(self.end_date1)
        hbox_date1.addStretch()
        hbox_date1.setStretch(0,10)
        hbox_date1.setStretch(1,110)
        hbox_date1.setStretch(2,70)
        hbox_date1.setStretch(3,2)
        hbox_date1.setStretch(4,70)
        hbox_date1.setStretch(5,2)
		
        search_date2 = QLabel('Date Created:')
        search_date2.setFont(font)
        search_date2.setFixedSize(110,15)
        self.start_date2 = MyLineEdit()
        self.start_date2.setObjectName('start_date2')
        self.start_date2.setStyleSheet("color: rgb(0, 85, 255);""background-color: rgba(244, 244, 244, 255);")
        self.start_date2.setFixedSize(70,15)

        time_x2 = QLabel('—')
        time_x2.setFixedSize(15,15)
        self.end_date2 = MyLineEdit()
        self.end_date2.setObjectName('end_date2')
        self.end_date2.setStyleSheet("color: rgb(0, 85, 255);""background-color: rgba(244, 244, 244, 255);")
        self.end_date2.setFixedSize(70,15)

        hbox_date2 = QHBoxLayout()
        hbox_date2.addSpacing(20)
        hbox_date2.addWidget(search_date2)
        hbox_date2.addWidget(self.start_date2)
        hbox_date2.addWidget(time_x2)
        hbox_date2.addWidget(self.end_date2)
        hbox_date2.addStretch()
        hbox_date2.setStretch(0,10)
        hbox_date2.setStretch(1,110)
        hbox_date2.setStretch(2,70)
        hbox_date2.setStretch(3,2)
        hbox_date2.setStretch(4,70)
        hbox_date2.setStretch(5,2)

        vbox_date = QVBoxLayout()
        # vbox_date.addSpacing(40)
        vbox_date.addLayout(hbox_date1)
        # vbox_date.addSpacing(5)
        vbox_date.addLayout(hbox_date2)

        hbox_search = QHBoxLayout()
        hbox_search.addLayout(tgrid)
        hbox_search.addLayout(vbox_date)

        vbox_main = QVBoxLayout()
        vbox_main.addSpacing(30)    #添加40像素的宽度
        vbox_main.addLayout(hbox_search)
        self.widgetMain.setLayout(vbox_main)
        self.widgetMain.hide()

        '''设置栏'''

        self.widgetSet = QWidget(self)
        self.widgetSet.setGeometry(0, 0, 800, 30)
        self.widgetSet.setObjectName('up-widget')
        palette1 = QPalette()
        palette1.setBrush(self.widgetSet.backgroundRole(), QBrush(QPixmap(':image/icons/set.png')))
        self.widgetSet.setPalette(palette1)
        self.widgetSet.setAutoFillBackground(True)

        #第一行，hbox_all放hbox_auth和hbox_obj
        hbox_all = QHBoxLayout()
        hbox_all.setSpacing(0)    #设置间距
        hbox_all.setContentsMargins(2, 0, 90, 0) #左上右下
        hbox_all.setObjectName('hbox_all')

        #hbox_auth放authorlabel、hbox_a、auth_Combo
        self.hbox_auth = QHBoxLayout()
        self.hbox_auth.setSpacing(1)
        self.hbox_auth.setObjectName('hbox_auth')

        author = QLabel('Author:')
        font.setFamily('Times New Roman')
        font.setPointSize(11)
        author.setFont(font)
        self.hbox_auth.addWidget(author)
        #用来添加控件
        self.hbox_a = QHBoxLayout()
        self.hbox_a.setSpacing(1)
        self.hbox_auth.addLayout(self.hbox_a)

        self.auth_Combo = QComboBox()
        #self.auth_Combo.resize(150, 0)
        self.auth_Combo.setMaximumSize(130, 20)
        self.auth_Combo.setObjectName('authorEdit')
        self.auth_Combo.setSizeAdjustPolicy(QComboBox.AdjustToContents) #匹配内容长度
        # self.auth_Combo.setPlaceholderText('Updating...')
        self.auth_Combo.setEditable(True)

        self.hbox_auth.addWidget(self.auth_Combo)

        self.hbox_auth.setStretch(0, 1)
        self.hbox_auth.setStretch(1, 1)
        self.hbox_auth.setStretch(2, 15)

        #hbox_obj放objectlabel、hobx_o、obj_Combo
        self.hbox_obj = QHBoxLayout()
        self.hbox_obj.setSpacing(1)
        self.hbox_obj.setObjectName('hbox_obj')

        object = QLabel('Tag:')
        font.setFamily('Times New Roman')
        font.setPointSize(11)
        object.setFont(font)
        self.hbox_obj.addWidget(object)

        #用来添加控件
        self.hbox_o = QHBoxLayout()
        self.hbox_o.setSpacing(1)
        self.hbox_obj.addLayout(self.hbox_o)

        self.obj_Combo = QComboBox()
        self.obj_Combo.setObjectName('objectEdit')
        #self.obj_Combo.resize(300, 0)
        self.obj_Combo.setMinimumSize(200, 0)
        self.obj_Combo.setMaximumSize(490, 20)
        self.obj_Combo.setSizeAdjustPolicy(QComboBox.AdjustToContents) #匹配内容长度
        # self.obj_Combo.setPlaceholderText('Updating...')
        self.obj_Combo.setEditable(True)
        self.hbox_obj.addWidget(self.obj_Combo)

        self.hbox_obj.setStretch(0, 1)
        self.hbox_obj.setStretch(1, 1)
        self.hbox_obj.setStretch(2, 15)

        self.renew = QPushButton('Renew',self.widgetSet)
        # self.renew.setStyleSheet(" border: 1px solid rgb(181, 53, 255);")
        self.renew.setGeometry(745,5,50,21)
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        self.renew.setFont(font)
        self.renew.setMinimumSize(50, 21)
        self.renew.setObjectName('renew')
        self.renew.setEnabled(False)
        #self.renew.setStyleSheet("background-color: rgba(50, 50, 50, 20)")

        #spacerItem = QSpacerItem(50, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        hbox_all.addLayout(self.hbox_auth)
        #hbox_all.addItem(spacerItem)
        hbox_all.addLayout(self.hbox_obj)

        hbox_all.setStretch(0, 5)
        hbox_all.setStretch(1, 15)
        self.widgetSet.setLayout(hbox_all)
        self.widgetSet.hide()

        '''列表栏'''
        font.setFamily('Times New Roman')

        self.widgetList = QWidget(self)
        self.widgetList.setGeometry(0, 102, 10, 10)
        self.widgetList.setObjectName('buttom-widget')
        # self.widgetList.setStyleSheet("border: 2px solid rgb(181, 53, 255);")
        palette1 = QPalette()
        palette1.setBrush(self.widgetList.backgroundRole(), QBrush(QPixmap(':image/icons/searchList.png')))
        self.widgetList.setPalette(palette1)
        self.widgetList.setAutoFillBackground(True)

        self.list = QTableView(self.widgetList)    #控件添加到窗口上
        self.list.setGeometry(-2, 0, 10, 10)
        self.list.setStyleSheet("border: 1px solid rgb(0, 10, 255);""background-color: rgba(200, 200, 200, 30);""alternate-background-color: rgba(50, 50, 50, 30);""font: 11pt \"Times New Roman\";\n") #
        self.list.setObjectName('resultList')
        self.list.verticalHeader().hide()      #隐藏行头
        self.list.horizontalHeader().hide()  #隐藏列头
        self.list.setShowGrid(False)  #设置是否显示网格
        self.list.verticalHeader().setDefaultSectionSize(24)  #设置行高
        self.list.setAlternatingRowColors(True) #背景色交替
        self.list.setSelectionBehavior(QAbstractItemView.SelectRows) #设置一次选中一行
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)    #设置允许右键菜单
        self.list.setColumnWidth(0, 20)
        self.list.setColumnWidth(1, 60)
        self.list.setColumnWidth(2, 630)
        self.list.setColumnWidth(3, 90)

        self.widgetList.hide()


        '''登入窗口初始化'''
        font.setFamily('Times New Roman')
        font.setPointSize(12)

        self.loginWindow = QDialog(self)
        self.loginWindow.setWindowTitle('loginWindow')
        self.loginWindow.setGeometry(0, 0, 250, 150)
        self.loginWindow.setWindowFlags(Qt.FramelessWindowHint)  #去掉窗口顶部title栏
        #self.loginWindow.setAttribute(Qt.WA_TranslucentBackground, True)  #设置窗口透明
        #self.loginWindow.setStyleSheet("background-color:rgb(71, 71, 106);")
        #self.loginWindow.setWindowOpacity(0.7)
        palette1 = QPalette()
        palette1.setBrush(self.loginWindow.backgroundRole(), QBrush(QPixmap(':image/icons/loginbackground.png')))
        self.loginWindow.setPalette(palette1)
        '''
        #设置窗口半透明
        palette2 = QPalette()
        palette2.setColor(QPalette.Background, QColor(100, 100, 100, 50))
        self.loginWindow.setPalette(palette2)
        '''
        self.loginWindow.setAutoFillBackground(True)

        self.userEdit = QLineEdit()
        self.userEdit.setFont(font)
        self.userEdit.setPlaceholderText('Username or Email')  #输入框文字提示语
        self.userEdit.setStyleSheet(" border: 1px solid rgb(150, 219, 255);""background-color: rgba(250, 250, 250, 100);""color:rgb(0, 85, 255);")
        self.userEdit.setFocus()

        self.passwordEdit = QLineEdit()
        self.passwordEdit.setEchoMode(QLineEdit.Password)
        self.passwordEdit.setFont(font)
        self.passwordEdit.setPlaceholderText('Password')
        self.passwordEdit.setStyleSheet(" border: 1px solid rgb(150, 219, 255);""background-color: rgba(250, 250, 250, 100);""color:rgb(0, 85, 255);")

        self.loginButton = QPushButton('Login')
        self.loginButton.setObjectName('LoginBtn')
        self.loginButton.setMinimumSize(60, 25)
        self.loginButton.setStyleSheet("color:rgb(85, 85, 255);""font: 75 11pt \"Times New Roman\";")
        self.loginButton_no = QPushButton('Cancel')
        self.loginButton_no.setObjectName('CancelBtn')
        self.loginButton_no.setMinimumSize(60, 25)
        self.loginButton_no.setStyleSheet("color:rgb(85, 85, 255);""font: 75 11pt \"Times New Roman\";")


        vbox = QVBoxLayout()
        vbox.addWidget(self.userEdit)
        vbox.addWidget(self.passwordEdit)
        #vbox.addStretch()

        self.autoCheckBox = QCheckBox('Automatic login next time')
        self.autoCheckBox.setObjectName('automaticLogin')
        #self.caseCheckBox.setStyleSheet("color: rgb(235, 235, 235);")
        self.autoCheckBox.setChecked(False)
        self.loginInfo = QLabel(' ')   #同时保存登入状态，为空时表示成功登入了
        self.loginInfo.setObjectName('loginInfo')
        self.loginInfo.setStyleSheet("color: rgb(0, 85, 255);")
        self.loginInfo.setAlignment(Qt.AlignCenter)

        vbox.addWidget(self.autoCheckBox)
        vbox.addWidget(self.loginInfo)

        hbox = QHBoxLayout()
        hbox.addSpacing(100)
        hbox.addWidget(self.loginButton)
        hbox.addWidget(self.loginButton_no)
        vbox.addLayout(hbox)

        self.loginWindow.setLayout(vbox)
        self.loginWindow.hide()

class searchWindow(UI):
    searchdata = pyqtSignal(str, str) #参数为字符串
    
    def __init__(self):
        super().__init__()
        self.m_drag=False
        self.login_status=0 #标记登入0:未登入，1:登入成功，2：退出，重新登入,3:原用户地鞥人，4:新的用户登入
        self.list_resize=[800, 360]
        self.authorBtnList=[]   #保存author控件列表
        self.objectBtnList=[]   #保存object控件列表
        self.login_data=[]  #保存临时登入数据
        self.keyworddata = ''   #保存临时搜索数据
        self.date_edit_name = ''    #保存临时时间输入框选择用
        self.checkdata = [[],[]]         #保存临时check序列
        self.date = ['','','','']              #保存date序列
        self.flage_renew=False          #保存更新状态 (暂未使用）
        self.milestone_url=set()        #临时保存里程碑URL
        self.mycalendar = MyCalendar()

        self.initSignal()
        self.start_main() #开启程序

    def initSignal(self):
        self.set.clicked.connect(self.btnClicked)
        self.searchEdit.textChanged.connect(lambda:self.search('searchEdit'))
        self.btn_close.clicked.connect(self.btnClicked)
        self.checkClosed.clicked.connect(lambda:self.search('check'))
        self.checkDelayed.clicked.connect(lambda:self.search('check'))
        self.checkDevfixed.clicked.connect(lambda:self.search('check'))
        self.checkNew.clicked.connect(lambda:self.search('check'))
        self.checkRejected.clicked.connect(lambda:self.search('check'))
        self.checkReOpen.clicked.connect(lambda:self.search('check'))
        self.check5.clicked.connect(lambda:self.search('check'))
        self.check4.clicked.connect(lambda:self.search('check'))
        self.check3.clicked.connect(lambda:self.search('check'))
        self.check2.clicked.connect(lambda:self.search('check'))
        self.check1.clicked.connect(lambda:self.search('check'))
        self.start_date1.clicked.connect(self.date_set)
        self.start_date1.textChanged.connect(lambda :self.search('date'))
        self.end_date1.clicked.connect(self.date_set)
        self.end_date1.textChanged.connect(lambda :self.search('date'))
        self.start_date2.clicked.connect(self.date_set)
        self.start_date2.textChanged.connect(lambda :self.search('date'))
        self.end_date2.clicked.connect(self.date_set)
        self.end_date2.textChanged.connect(lambda :self.search('date'))
        self.auth_Combo.activated.connect(self.addBtnCheck)
        self.obj_Combo.activated.connect(self.addBtnCheck)
        self.renew.clicked.connect(lambda:self.search('renew'))
        self.list.customContextMenuRequested.connect(self.generateMenu)
        self.list.doubleClicked.connect(self.getListIndex)
        self.loginButton.clicked.connect(self.login)
        self.loginButton_no.clicked.connect(self.loginWindow.reject)
        self.loginWindow.rejected.connect(self.deleteLater)

        self.mycalendar.qdate.connect(self.date_get)

        self.thread_tr=MyThread()
        self.thread_tr.phid.connect(self.updateQuery)
        self.thread_tr.login_status.connect(self.show_loginInfo)
        self.thread_tr.init_data.connect(self.initQueryData)
        self.thread_tr.searchBug_result.connect(self.bug_From_xlsx)

    def btnClicked(self):
        sender = self.sender()
        obj = sender.objectName()
        if obj=='close':
            self.mycalendar.hide()
            self.showMinimized()
        elif obj=='set':
            if self.widgetSet.isVisible():
                self.widgetSet.hide()
                self.searchEdit.setFocus()
            else:
                self.widgetSet.show()
                self.auth_Combo.clearEditText()
                self.auth_Combo.setFocus()
                self.obj_Combo.clearEditText()
    #居中显示
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    #获取控件坐标
    def getWidgetPos(self, widget):
        '''qwidget.pos().x()和qwidget.pos().y()分别获取控件的x、y坐标，但是是topLeft坐标'''

        rect = widget.rect()
        #tl = widget.mapToGlobal(rect.topLeft())   #相对于全局坐标
        #tl = widget.mapToParent(rect.topLeft())  #相对于父窗口坐标
        #br = widget.mapToGlobal(rect.bottomRight())
        #bl = widget.mapToGlobal(rect.bottomLeft())
        bl = widget.mapToParent(rect.bottomLeft())
        pos = [bl.x(), bl.y()]
        return pos

    def initQueryData(self,list,name,*args):
        '''数据初始化
           1.初始化下拉列表（添加下拉列表数据）--登入成功后，读取people和tag，在这里保存
           2.初始化搜索条件（添加相关搜索项）--将从ini读取的数据与网络数据进行校验后再设置搜索条件
        '''
        if 'login' in args:     #登入时调用
            self.authorBtnList=[]
            self.objectBtnList=[]
            for a in var.authorConfig.keys():
                btn = QPushButton(self.widgetSet)
                btn.setStyleSheet("font: 75 9pt \"Arial\";""color: rgb(255, 95, 2);""background-color: rgba(0,0xff,0,10);")
                btn.clicked.connect(self.closeBtn)
                btn.setObjectName('authorEdit')
                btn.setText(a)
                btn.setToolTip(a)
                self.hbox_a.addWidget(btn)
                self.authorBtnList.append(btn)
            for o in var.objectConfig.keys():
                btn = QPushButton(self.widgetSet)
                btn.setStyleSheet("font: 75 9pt \"Arial\";""color: rgb(255, 95, 2);""background-color: rgba(0,0xff,0,10);")
                btn.clicked.connect(self.closeBtn)
                btn.setObjectName('objectEdit')
                btn.setText(o)
                btn.setToolTip(o)
                self.hbox_o.addWidget(btn)
                self.objectBtnList.append(btn)
        if name=='user':
            logging.info('成功接收user')
            var.people_List=list  #需要这个变量
            peoples = [u[0] for u in list]
            self.auth_Combo.addItems(peoples)
            self.completer = QCompleter(peoples)
            self.completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.completer.setFilterMode(Qt.MatchContains)
            self.completer.setMaxVisibleItems(10)
            self.auth_Combo.setCompleter(self.completer)
        elif name=='tag':
            logging.info('成功接收tag')
            var.object_List.extend(list)
            tags=[l[0] for l in list]   #
            tags1=[o[0] for o in var.object_List]
            # tags=list(set(tags))        #去重操作
            # tags.sort(key=tags.index)   #还原排序
            self.obj_Combo.addItems(tags)
            self.completer = QCompleter(tags1)
            self.completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.completer.setFilterMode(Qt.MatchContains)
            self.completer.setMaxVisibleItems(15)
            self.obj_Combo.setCompleter(self.completer)
        elif name=='milestone':
            logging.info('成功接收milestone')
            var.milestones_List = list
            var.object_List.extend(list)
            tags=[m[0] for m in var.milestones_List]
            tags1=[o[0] for o in var.object_List]
            self.obj_Combo.addItems(tags)
            self.completer = QCompleter(tags1)
            self.completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.completer.setFilterMode(Qt.MatchContains)
            self.completer.setMaxVisibleItems(15)
            self.obj_Combo.setCompleter(self.completer)
            self.renew.setEnabled(True)
        elif name=='milestone_url':
            self.milestone_url=list


    def showSearchListWidget(self, len):
        if len>=15:
            self.list_resize=[800, 360]
        elif len>0:
            self.list_resize=[800, 4+24*len]
        else:
            self.list_resize=[800, 0]
        self.list.resize(self.list_resize[0]+22, self.list_resize[1])
        self.widgetList.resize(self.list_resize[0], self.list_resize[1])
        self.resize(800, self.list_resize[0]+102)
        if not self.widgetList.isVisible() and len>0:
            self.widgetList.show()

    def show_loginInfo(self, status='',*args):
        '''接收一个'''
        self.loginInfo.setText(status)
        self.loginInfo.repaint()  #重新绘制
        if status=='login Error' or status=='login Fail':
            self.loginButton.setEnabled(True)
        elif status=='login Success':
            sleep(0.5)
            self.loginSuccess()
        elif status=='finished loading.':
            sleep(0.5)
            self.loginInfo.setText("")
            self.loginButton.setEnabled(True)
            self.renew.setEnabled(False)
            if self.loginWindow.isVisible():
                self.loginWindow.accept()  #关闭对话框并返回1
                ##QMessageBox.critical(self, '错误', '账号或密码错误')
            self.thread_tr.getData('milestones')
        elif status=="":
            self.clearSearch()
            self.renew.setEnabled(True)
            self.set.setEnabled(True)
            self.searchEdit.setPlaceholderText('')
            self.searchEdit.setEnabled(True)
            self.searchEdit.setFocus()
            self.widgetList.hide()  #列表隐藏
            
    def showLoginWindow(self,list=[]):
        self.resize(250, 150)
        if not self.isVisible():
            self.show()
        self.widgetMain.hide()
        self.widgetSet.hide()
        self.widgetList.hide()
        self.loginWindow.show()
        if len(list)==3:    #如果传参有数据
            self.userEdit.setText(list[2])
            self.passwordEdit.setText(list[1])
            self.autoCheckBox.setChecked(list[0])
            self.loginWindow.repaint()
            # self.loginWindow.processEvents()
            
    def showSearchMain(self):
        self.resize(800, 100)
        if not self.isVisible():
            self.show()
        self.widgetMain.show()

     #重写三个方法使我们的Example窗口支持拖动,上面参数window就是拖动对象

    def mousePressEvent(self, event):
        if event.button()==Qt.LeftButton:
            self.m_drag=True
            self.m_DragPosition=event.globalPos()-self.pos()  #记录点击坐标
            event.accept()


    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_drag:
            self.move(QMouseEvent.globalPos()-self.m_DragPosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_drag=False

    ###########################################
    def addBtnCheck(self):
        '''先判断按钮是否已经有啦
           1.发送后，可获取所选项的PHID以及添加按钮（更新查询）
        '''
        sender = self.sender()
        # print(sender.text())
        object = sender.objectName()
        if object == self.auth_Combo.objectName():
            if self.auth_Combo.currentText() in [user[0] for user in var.people_List]:  #如果名字在人员列表中
                if self.auth_Combo.currentText() not in var.authorConfig.keys():  #检查是否已经存在
                    text_search = self.auth_Combo.currentText()[:self.auth_Combo.currentText().find(' ')] #只输入前面
                    var.dataSourceParams['q'] = text_search
                    var.dataSourceParams['raw'] = text_search
                    self.thread_tr.getPHID(self.auth_Combo.currentText(),'people')  #text_search为人名含括号
            # print(self.auth_Combo.currentText())
            self.auth_Combo.clearEditText()
        elif object == self.obj_Combo.objectName():
            if self.obj_Combo.currentText() not in var.objectConfig.keys():  #如果尚没有添加该搜索项
                for obj in var.object_List:
                    if self.obj_Combo.currentText()==obj[0]:   #如果在项目名单中
                        if obj[2]=='Milestone':         #如果是Milestones，则直接获取PHID
                            self.updateQuery(obj)
                        else:
                            text_search = self.obj_Combo.currentText()
                            var.dataSourceParams['q'] = text_search
                            var.dataSourceParams['raw'] = text_search
                            self.thread_tr.getPHID(self.obj_Combo.currentText(),'object')  #text_search为人名含括号
                        break
            self.obj_Combo.clearEditText()

    def closeBtn(self):
        sender = self.sender()
        ##if isinstance(sender, QPushButton)  #类型判断
        btnText = sender.text()
        btnObject = sender.objectName()
        if btnObject=='authorEdit':
            del var.authorConfig[btnText]
            self.authorBtnList.remove(sender)
        elif btnObject=='objectEdit':
            del var.objectConfig[btnText]
            self.objectBtnList.remove(sender)
        sender.close()

    def clearData(self):
        if var.login_data==[]:
            #写入文件
            logging.info('首次登入成功时')
            var.login_data = self.login_data
            self.config_write()
            return
        if var.login_data[2]!=self.login_data[2]:
            var.authorConfig={}
            var.objectConfig={}
            var.authorConfigLen=0
            var.objectConfigLen=0
        var.login_data=self.login_data
        for l in self.authorBtnList:
            l.close()
        self.authorBtnList=[]
        for l in self.objectBtnList:
            l.close()
        self.objectBtnList=[]
		
		#写入文件
        logging.info('login Success')
        self.config_write()

    def clearSearch(self):
        self.checkNew.setChecked(False)
        self.checkReOpen.setChecked(False)
        self.checkDevfixed.setChecked(False)
        self.checkDelayed.setChecked(False)
        self.checkClosed.setChecked(False)
        self.checkRejected.setChecked(False)
        self.check1.setChecked(False)
        self.check2.setChecked(False)
        self.check3.setChecked(False)
        self.check4.setChecked(False)
        self.check5.setChecked(False)
        self.searchEdit.setText('')
        self.start_date1.setText('')
        self.end_date1.setText('')
        self.start_date2.setText('')
        self.end_date2.setText('')

    def fuzzyFinder(self,user_input, collection):
        '''模糊查询'''
        suggestions = []
        pattern = '.*?'.join(user_input)    # Converts 'djm' to 'd.*?j.*?m'
        regex = re.compile(pattern,re.I)         # Compiles a regex.
        for item in collection:
            match = regex.search((item[0]+item[6]))      # Checks if the current item matches the regex.先将bug代号和标题和到一起
            if match:
                suggestions.append((len(match.group()), match.start(), item))
        return [x for _, _, x in sorted(suggestions)]

    def getListIndex(self, text):
        sender = self.sender()
        if sender.objectName()=='resultList':
            bug = var.searchBugList[int(text.row())][0]
            if int(text.column())==2:
                webbrowser.open('http://review.mprtimes.net/'+bug)
            if int(text.column())==1:
                pyperclip.copy('http://review.mprtimes.net/'+bug)

    def generateMenu(self,pos):
        # print(pos)
        row_num=-1
        for i in self.list.selectionModel().selection().indexes():
            row_num = i.row()
        menu = QMenu()
        action1 = menu.addAction('Copy bug title')
        action2 = menu.addAction('Copy bug links')
        action3 = menu.addAction('Copy all bug links')
        # action1.triggered.connect(xxx)  #槽的方式
        action = menu.exec_(self.list.mapToGlobal(pos))
        clipdata = ''
        if action==action1:
            clipdata=var.searchBugList[row_num][6]
        elif action==action2:
            clipdata = 'http://review.mprtimes.net/'+var.searchBugList[row_num][0]+'\n'
        elif action==action3:
            for bug in var.searchBugList:
                clipdata = clipdata+'http://review.mprtimes.net/'+bug[0]+'\n'
        pyperclip.copy(clipdata)
        # print(self.list.item(row_num,1).text())


    def bug_From_xlsx(self,res):
        '''根据查询表结果，获取bug数据
           res=Success或者No data
        '''
		#查询到结果，首先保存查询数据
        logging.info('已查询到结果')
        self.config_write()
		
        # logging.info('bug_From_xlsx')
        # self.show_loginInfo('renew bug ...')
        #重置bugList
        var.bugForms = []
        var.renewBugForms=[]
        if res=="Success":
            data = xlrd.open_workbook(var.xls_file)
            table = data.sheets()[0]
            nrows = table.nrows
            for i in range(1, nrows):
                rowdata=[]
                for n in range(7):
                    ##ctype： 0 empty,1 string, 2 number, 3 date, 4 boolean, 5 error
                    ctype = table.cell(i, n).ctype
                    cell = table.cell(i, n).value
                    if ctype==3:
                        cdata = datetime(*xldate_as_tuple(cell, 0))
                        cell = (cdata+timedelta(hours=8)).strftime('%Y/%m/%d %H:%M')
                    rowdata.append(cell)
                var.bugForms.append(rowdata)
            os.remove(var.xls_file)
            #更新renewBugForms数据
            var.renewBugForms=var.bugForms  #更新搜索bug列表
        if self.loginInfo.text():      #不为空时
            self.show_loginInfo('finished loading.')  #只有在登入时需要用到该语句，先不处理
        else:
            self.show_loginInfo()
        self.listnum.setText('Tasks: {}'.format(len(var.bugForms)))

    def loginSuccess(self):
        '''登入成功后的初始化'''
        self.show_loginInfo('renew data ...')
        #先清除数据,保存登入参数
        self.clearData()
        #先查询操作
        self.initQueryData(None,None,'login')
        self.setPostData()
        #读取数据
        if not var.people_List:     #或许这样可以
            self.thread_tr.getData('peoples')
        if not var.object_List:     #或许这样可以
            self.thread_tr.getData('tags')

    def login(self):
        if self.autoCheckBox.isChecked():
            auto = True
        else:
            auto = False
        self.login_data=[auto,self.passwordEdit.text(),self.userEdit.text()]

        self.loginButton.setEnabled(False)
        self.thread_tr.login(self.login_data[1:])

    def config_read(self):
        #读取信息
        if not os.path.isfile(var.config_file):
            #创建一个空配置
            Authority = {'Auto':False,
						 'UserName':'',
						 'Password':''}
            SearchData = {}
            SearchData['authorConfig'] = {}
            SearchData['objectConfig'] = {}

            with open(var.config_file,'wb') as file:    #如果没有会自动创建
                pickle.dump((Authority,SearchData),file,-1)
            return
        with open(var.config_file,'rb') as file:
            try:
                authority,searchdata = pickle.load(file)
            except:
                authority,searchdata = None,None
        if not authority==None:
            var.login_data = [authority['Auto'], authority['Password'], authority['UserName']]
        if not searchdata==None:
            var.authorConfig = searchdata['authorConfig']
            var.authorConfigLen = len(var.authorConfig)
            var.objectConfig = searchdata['objectConfig']
            var.objectConfigLen = len(var.objectConfig)

    def config_write(self,logindata=None):
        if var.login_data != []:
            Authority = {'Auto':var.login_data[0],
                         'UserName':var.login_data[2],
                         'Password':var.login_data[1]}
        else:
            Authority = {'Auto':self.login_data[0],
                         'UserName':self.login_data[2],
                         'Password':self.login_data[1]}
        SearchData = {}
        SearchData['authorConfig'] = var.authorConfig
        SearchData['objectConfig'] = var.objectConfig

        with open(var.config_file,'wb') as file:    #如果没有会自动创建
            file.truncate()     #清空文件
            pickle.dump((Authority,SearchData),file,-1)
        logging.info('保存用户信息%s'%Authority)
        logging.info('保存查询信息%s'%SearchData)
        logging.info('写入配置文件成功')			


    def date_set(self):
        sender = self.sender()
        obj = sender.objectName()
        self.date_edit_name=obj
        # self.mycalendar.qdate.disconnect() #先解除绑定
        # self.mycalendar.qdate.connect(lambda :self.date_get(obj))
        rect = sender.rect()
        tl = sender.mapToGlobal(rect.topLeft())
        pos = [tl.x(),tl.y()]
        if self.mycalendar.mapToGlobal(self.mycalendar.rect().topRight()).x()>=800:
            # self.mycalendar.move(800-255,pos[1]+4)
            self.mycalendar.move(pos[0],pos[1]+20)
        else:
            self.mycalendar.move(pos[0],pos[1]+20)
        # self.mycalendar.hide()  #先关闭一次
        # self.mycalendar.cal.setSelectedDate(QDate.currentDate())
        # self.mycalendar.cal.showSelectedDate()
        # self.mycalendar.show()
        self.mycalendar.showCalendar()

    def date_get(self,text):
        if self.date_edit_name=='start_date2':
            self.start_date2.setText(text)
        elif self.date_edit_name=='end_date2':
            self.end_date2.setText(text)
        elif self.date_edit_name=='start_date1':
            self.start_date1.setText(text)
        elif self.date_edit_name=='end_date1':
            self.end_date1.setText(text)

    def eventFilter(self, QObject, QEvent):
        '''暂未使用'''
        if QEvent.type()==QEvent.FocusOut:
            logging.info(1)
        return False

    def renewSearchBugList(self):
        '''更新renewBugForms序列'''
        #先处理check
        temp_check= []
        list=self.checkdata
        if list ==[[], []]:
            temp_check = var.bugForms  #重置renewBugForms
        elif list[0]!=[] and list[1]!=[]:
            for bug in var.bugForms:
                if bug[2] in list[0] and bug[3] in list[1]:
                    temp_check.append(bug)
        elif list[0]!=[]:
            for bug in var.bugForms:
                if bug[2] in list[0]:
                    temp_check.append(bug)
        elif list[1]!=[]:
            for bug in var.bugForms:
                if bug[3] in list[1]:
                    temp_check.append(bug)
        #再处理date
		#处理思路：先帅选出更新日期，再筛选出创建日期
		#如果都为空
        temp_date = []
        temp_date2 = []
        if self.date==['','','','']:
            temp_date2 = var.bugForms
		
        else:
			#先帅选出更新日期
            if self.date[:2]==['','']:
                temp_date = var.bugForms
            elif self.date[0]=='':
                for bug in var.bugForms:
                    date = time.strptime(bug[5],'%Y/%m/%d %H:%M')
                    date = time.strftime('%Y-%m-%d',date)
                    if date<=self.date[1]:
                        temp_date.append(bug)
            elif self.date[1]=='':
                for bug in var.bugForms:
                    date = time.strptime(bug[5],'%Y/%m/%d %H:%M')
                    date = time.strftime('%Y-%m-%d',date)
                    if self.date[0]<=date:
                        temp_date.append(bug)
            else:
                if self.date[0]<=self.date[1]:
                    for bug in var.bugForms:
                        date = time.strptime(bug[5],'%Y/%m/%d %H:%M')
                        date = time.strftime('%Y-%m-%d',date)
                        if self.date[0]<=date<=self.date[1]:
                            temp_date.append(bug)
			
			#再筛选出创建日期
            if self.date[-2:]==['','']:
                temp_date2 = temp_date
            elif self.date[2]=='':
                for bug in temp_date:
                    date = time.strptime(bug[4],'%Y/%m/%d %H:%M')
                    date = time.strftime('%Y-%m-%d',date)
                    if date<=self.date[3]:
                        temp_date2.append(bug)
            elif self.date[3]=='':
                for bug in temp_date:
                    date = time.strptime(bug[4],'%Y/%m/%d %H:%M')
                    date = time.strftime('%Y-%m-%d',date)
                    if self.date[2]<=date:
                        temp_date2.append(bug)
            else:
                if self.date[2]<=self.date[3]:
                    for bug in temp_date:
                        date = time.strptime(bug[4],'%Y/%m/%d %H:%M')
                        date = time.strftime('%Y-%m-%d',date)
                        if self.date[2]<=date<=self.date[3]:
                            temp_date2.append(bug)
							
        #获取交集
        var.renewBugForms = [bug for bug in temp_check if bug in temp_date2]
        # var.renewBugForms=list(set(temp_check).intersection(set(temp_date)))
        self.updateList(self.keyworddata)

    #根据搜索弹出结果窗口
    def search(self, text):
        sender = self.sender()
        # print(sender.text())
        ts='*()+[]?\\'
        if text=='searchEdit':
            if self.searchEdit.text() and self.searchEdit.text()[-1] in ts:
                self.searchEdit.setText(self.searchEdit.text()[:-1])
                self.keyworddata = self.searchEdit.text()
                #self.searchEdit.undo()
            else:
                # self.searchText = self.searchEdit.text()
                # self.searchBug(self.searchEdit.text(), 'searchEdit')
                self.keyworddata = self.searchEdit.text()
                self.updateList(self.keyworddata) #更新列表
        elif text=='renew':
            self.flage_renew=True
            sender.setEnabled(False)   #先enabled该按钮
            self.widgetSet.hide()
            self.set.setEnabled(False)
            self.searchEdit.setEnabled(False)
            self.searchEdit.setPlaceholderText('Updating ...')
            self.clearSearch()
            self.widgetList.hide()
            self.searchEdit.repaint()
            self.setPostData()
        elif text=='check':
            statuses = []
            if self.checkNew.isChecked():
                statuses.append('New')
            if self.checkReOpen.isChecked():
                statuses.append('ReOpen')
            if self.checkDevfixed.isChecked():
                statuses.append('Devfixed')
            if self.checkDelayed.isChecked():
                statuses.append('Delayed')
            if self.checkClosed.isChecked():
                statuses.append('Closed')
            if self.checkRejected.isChecked():
                statuses.append('Rejected')
            priorities = []
            #建议、轻微、正常、严重、阻碍
            if self.check1.isChecked():
                priorities.append('建议')
            if self.check2.isChecked():
                priorities.append('轻微')
            if self.check3.isChecked():
                priorities.append('正常')
            if self.check4.isChecked():
                priorities.append('严重')
            if self.check5.isChecked():
                priorities.append('阻碍')

            self.checkdata = [statuses, priorities]
            self.renewSearchBugList()
        elif text=='date':
            self.date = [self.start_date1.text(),self.end_date1.text(),self.start_date2.text(),self.end_date2.text()]
            self.renewSearchBugList()


    def start_main(self):
        self.config_read()
        #打开登入窗口
        self.showLoginWindow(var.login_data)
        #检查是否自动登入
        if var.login_data and var.login_data[0]:
            self.loginButton.setEnabled(False)
            self.login_data=var.login_data
            self.thread_tr.login(self.login_data[1:3])

    def setPostData(self,*args):
        '''该函数先配置了postdata参数，然后进行查询获取bug
           参数来源于界面所设置的即变量config中的
           查到的bug由bug_From_xlsx接收'''
        '''设置查询参数'''
        logging.info('开始查询bug')
        author=[]
        object=[]
        var.searchDataPart1={}
        #检验数据的正确性
        try:
            #author参数
            author=list(var.authorConfig.values())
            var.authorConfigLen = len(author)
            #重置authorPHIDs[x]
            for i in range(var.authorConfigLen):
                var.searchDataPart1['authorPHIDs['+str(i)+']'] = author[i]
        except:
            logging.info('配置的PostData数据异常')
            var.authorConfigLen=0
            var.authorConfig={}
        #检验数据的正确性
        try:
            #object参数
            object=list(var.objectConfig.values())
            var.objectConfigLen = len(object)
            #重置projectPHIDs[x]
            for i in range(var.objectConfigLen):
                var.searchDataPart1['projectPHIDs['+str(i)+']'] = object[i]
        except:
            logging.info('配置的PostData数据异常')
            var.objectConfigLen=0
            var.objectConfig={}
        # print('--------------\n*searchDataPart1*：\n', var.searchDataPart1)
        '''查询bug'''
        #如果searchDataPart1为空，则不查询
        self.thread_tr.getData('postdata')

    def updateList(self,text):
        '''更新列表序列'''
        if not text:    #当为空时
            self.listnum.setText('Tasks: '+str(len(var.renewBugForms)))
            if self.checkdata==[[],[]] and self.date==['','','','']:
                self.widgetList.hide()
                return
        var.searchBugList=[]
        if var.renewBugForms!='o':
            var.searchBugList = self.fuzzyFinder(text, var.renewBugForms)
        '''更新列表界面'''
        header = ['status', 'code', 'title', 'create-time']
        self.lm = MyTableModel(var.searchBugList, header, self)
        self.list.setModel(self.lm)
        #显示列表数据量
        self.listnum.setText('Tasks: '+str(self.lm.rowCount(None)))
        # self.listnum.setObjectName('listnum')
        # self.listnum.setAlignment(Qt.AlignCenter)
        #QListView高度设置
        self.list.setColumnWidth(0, 20)
        self.list.setColumnWidth(1, 60)
        self.list.setColumnWidth(2, 630)
        self.list.setColumnWidth(3, 90)
        self.showSearchListWidget(len(var.searchBugList))
        # self.list.resize(self.list_resize[0]+20, self.list_resize[1])

    def updateQuery(self,list):
        '''addBtnCheck()后，最终数据到达该槽
           1.获取对应的PHID
           2.更新界面
        '''
        '''获取对应的PHID'''
        name=list[0]
        phid_=list[1]
        type_=list[2]
        if type_=='user':
            var.authorConfig[name] = phid_
            # print('*authorConfig*：', var.authorConfig)
        else:  #'Tag','Project'
            var.objectConfig[name] = phid_
            # print('*objectConfig*：', var.objectConfig)

        '''更新界面'''
        btn = QPushButton()
        btn.setText(name)
        btn.setStyleSheet("font: 75 9pt \"Arial\";""color: rgb(255, 95, 2);""background-color: rgba(0,0xff,0,100);")
        btn.setMaximumSize(300, 21)
        btn.clicked.connect(self.closeBtn)
        btn.setToolTip(name)
        if type_=='user':
            btn.setObjectName('authorEdit')
            self.hbox_a.addWidget(btn)
            self.authorBtnList.append(btn)
            self.auth_Combo.setFocus()
        else:       #'Tag','Project'
            btn.setObjectName('objectEdit')
            self.hbox_o.addWidget(btn)
            self.objectBtnList.append(btn)
            self.obj_Combo.setFocus()

class MyLineEdit(QLineEdit):
    clicked = pyqtSignal()
    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button()==Qt.LeftButton:
            self.clicked.emit()

class MyCalendar(QDialog):
    qdate = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        font = QFont()
        font.setFamily('宋体')
        font.setPointSize(8)
        self.setWindowFlags(Qt.FramelessWindowHint)  #去掉窗口顶部title栏
        self.setFixedSize(210,200)
        self.cal = QCalendarWidget(self)
        self.cal.setFixedSize(210,180)
        self.cal.setFont(font)
        clear = QPushButton('clear',self)
        clear.setObjectName('clear')
        clear.setGeometry(0,180,55,20)
        cancel = QPushButton('cancel',self)
        cancel.setObjectName('cancel')
        cancel.setGeometry(155,180,55,20)

        self.cal.setGridVisible(True)
        self.cal.setVerticalHeaderFormat(0)
        self.cal.setHorizontalHeaderFormat(2)
        self.cal.setSelectedDate(QDate.currentDate())
        self.cal.clicked[QDate].connect(self.sendDate)
        cancel.clicked.connect(self.sendDate)
        clear.clicked.connect(self.sendDate)

        self.hide()

    def sendDate(self, date):
        sender = self.sender()
        if sender.objectName()=='cancel':
            pass
        elif sender.objectName()=='clear':
            self.qdate.emit('')
        else:
            # print(type(date.toPyDate())) #<class 'datetime.date'>
            self.qdate.emit(str(date.toPyDate())) #toString()
        self.hide()

    def showCalendar(self):
        self.hide()  #先关闭一次
        self.cal.setSelectedDate(QDate.currentDate())
        self.cal.showSelectedDate()
        self.show()

class MyListModel(QAbstractListModel):
    '''构造出QListview的数据'''
    def __init__(self, datain, parent=None, *args): 
        """ datain: a list where each item is a row
        """
        QAbstractListModel.__init__(self, parent, *args) 
        self.listdata = datain
 
    def rowCount(self, parent=QModelIndex()): 
        return len(self.listdata) 
 
    def data(self, index, role): 
        if index.isValid() and role == Qt.DisplayRole:
            return QVariant(self.listdata[index.row()][0])
        elif role==Qt.DecorationRole:
            if self.listdata[index.row()][2]=='user':
                return QVariant(QIcon(':image/icons/User.png'))
            elif self.listdata[index.row()][2]=="Group":
                return QVariant(QIcon(':image/icons/Group.png'))
            elif self.listdata[index.row()][2]=="Project":
                return QVariant(QIcon(':image/icons/Project.png'))
            elif self.listdata[index.row()][2]=="Milestone":
                return QVariant(QIcon(':image/icons/Milestone.png'))
            elif self.listdata[index.row()][2]=="Tag":
                return QVariant(QIcon(':image/icons/Tag.png'))
        else:
            return QVariant()

class MyTableModel(QAbstractTableModel):
    def __init__(self, datain, headerdata, parent=None, *args):
        """datain:a list of lists
            headerdata:a list of strings"""
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain
        self.headerdata = headerdata
        
    def rowCount(self, parent):
        return len(self.arraydata)
        
    def columnCount(self, parent):
        if len(self.arraydata) > 0:
            #return len(self.arraydata[0])
            ##手动设置显示4列
            return 4
        return 0
        
    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role ==Qt.DisplayRole:
            if index.column()==1:
                return QVariant(self.arraydata[index.row()][0])
            elif index.column()==2:
                return QVariant(self.arraydata[index.row()][6])
            elif index.column()==3:
                return QVariant(self.arraydata[index.row()][4])
        elif role ==Qt.DecorationRole and index.column()==0:
            if self.arraydata[index.row()][2]=="Closed":
                return QVariant(QIcon(':image/icons/closed.png'))
            elif self.arraydata[index.row()][2]=="Devfixed":
                if self.arraydata[index.row()][3]=="阻碍":
                    return QVariant(QIcon(':image/icons/pink_Devfixed.png'))
                elif self.arraydata[index.row()][3]=="严重":
                    return QVariant(QIcon(':image/icons/red_Devfixed.png'))
                elif self.arraydata[index.row()][3]=="正常":
                    return QVariant(QIcon(':image/icons/orange_Devfixed.png'))
                elif self.arraydata[index.row()][3]=="轻微":
                    return QVariant(QIcon(':image/icons/yellow_Devfixed.png'))
                elif self.arraydata[index.row()][3]=="建议":
                    return QVariant(QIcon(':image/icons/sky_Devfixed.png'))
            elif self.arraydata[index.row()][2]=="Delayed":
                if self.arraydata[index.row()][3]=="阻碍":
                    return QVariant(QIcon(':image/icons/pink_Delayed.png'))
                elif self.arraydata[index.row()][3]=="严重":
                    return QVariant(QIcon(':image/icons/red_Delayed.png'))
                elif self.arraydata[index.row()][3]=="正常":
                    return QVariant(QIcon(':image/icons/orange_Delayed.png'))
                elif self.arraydata[index.row()][3]=="轻微":
                    return QVariant(QIcon(':image/icons/yellow_Delayed.png'))
                elif self.arraydata[index.row()][3]=="建议":
                    return QVariant(QIcon(':image/icons/sky_Delayed.png'))
            elif self.arraydata[index.row()][2]=="New":
                if self.arraydata[index.row()][3]=="阻碍":
                    return QVariant(QIcon(':image/icons/pink_New.png'))
                elif self.arraydata[index.row()][3]=="严重":
                    return QVariant(QIcon(':image/icons/red_New.png'))
                elif self.arraydata[index.row()][3]=="正常":
                    return QVariant(QIcon(':image/icons/orange_New.png'))
                elif self.arraydata[index.row()][3]=="轻微":
                    return QVariant(QIcon(':image/icons/yellow_New.png'))
                elif self.arraydata[index.row()][3]=="建议":
                    return QVariant(QIcon(':image/icons/sky_New.png'))
            elif self.arraydata[index.row()][2]=="Rejected":
                if self.arraydata[index.row()][3]=="阻碍":
                    return QVariant(QIcon(':image/icons/pink_Rejected.png'))
                elif self.arraydata[index.row()][3]=="严重":
                    return QVariant(QIcon(':image/icons/red_Rejected.png'))
                elif self.arraydata[index.row()][3]=="正常":
                    return QVariant(QIcon(':image/icons/orange_Rejected.png'))
                elif self.arraydata[index.row()][3]=="轻微":
                    return QVariant(QIcon(':image/icons/yellow_Rejected.png'))
                elif self.arraydata[index.row()][3]=="建议":
                    return QVariant(QIcon(':image/icons/sky_Rejected.png'))
            elif self.arraydata[index.row()][2]=="ReOpen":
                if self.arraydata[index.row()][3]=="阻碍":
                    return QVariant(QIcon(':image/icons/pink_New.png'))
                elif self.arraydata[index.row()][3]=="严重":
                    return QVariant(QIcon(':image/icons/red_New.png'))
                elif self.arraydata[index.row()][3]=="正常":
                    return QVariant(QIcon(':image/icons/orange_New.png'))
                elif self.arraydata[index.row()][3]=="轻微":
                    return QVariant(QIcon(':image/icons/yellow_New.png'))
                elif self.arraydata[index.row()][3]=="建议":
                    return QVariant(QIcon(':image/icons/sky_New.png'))
        elif role ==Qt.ForegroundRole and index.column()==1:
            return QColor(0, 0, 255)
        elif role ==Qt.FontRole and index.column()==1:
            font = QFont()
            font.setBold(True)
            return font
        elif role ==Qt.ForegroundRole and index.column()==2:
            return QColor(50, 50, 25)
        elif role ==Qt.ForegroundRole and index.column()==3:
            return QColor(70, 70, 70)
        elif role ==Qt.FontRole and index.column()==3:
            font = QFont()
            font.setPointSize(8)
            return font
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()
    
    #排序用
    def sort(self, Ncol, order):
        """Sort table by given column number."""
        #self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()
        #self.emit(SIGNAL("layoutChanged()"))

class DlgMain(QDialog):
    '''创建系统托盘'''
    relogin = pyqtSignal()

    def __init__(self, window):
        super().__init__()
        self.sw = window
        self.addSystemTray()
        
    def addSystemTray(self):
        #rstoreAction = QAction('还原', self, triggered=self.sw.show)
        rstoreAction = QAction('还原', self, triggered=self.sw.showNormal)
        reloginAction = QAction('重新登入',self,triggered=self.relogin)
        quitAction = QAction('退出', self, triggered=self.sw.deleteLater) 
        # quitAction = QAction('退出', self, triggered=self.logout)
		#close后deleter，这样会释放内存(qt是这样的)
        self.trayMenu = QMenu(self)#创建菜单
        self.trayMenu.addAction(rstoreAction)
        self.trayMenu.addAction(reloginAction)
        self.trayMenu.addSeparator()
        self.trayMenu.addAction(quitAction)
        self.trayIcon = QSystemTrayIcon()#创建系统托盘对象
        self.icon = QIcon(':image/icons/trayIcon.ico')#创建图标
        self.trayIcon.setIcon(self.icon)
        self.trayIcon.setContextMenu(self.trayMenu)#设置系统托盘菜单
        self.trayIcon.show()
        
    def relogin(self):
        # self.relogin.emit(self.sw.thread_tr.quit_tr)
        # var.people_List=[]    #重新登入时不清除
        # var.object_List=[]
        # var.milestones_List=[]

        var.rs=requests.Session() #清空数据
        username = var.login_data[2]
        password = ''
        auto = False
        self.sw.showLoginWindow([auto,password,username])


@register
def atexit():
    Authority = {'Auto':var.login_data[0],
                 'UserName':var.login_data[2],
                 'Password':var.login_data[1]}
    SearchData = {}
    SearchData['authorConfig'] = var.authorConfig
    SearchData['objectConfig'] = var.objectConfig

    with open(var.config_file,'wb') as file:    #如果没有会自动创建
        file.truncate()     #清空文件
        pickle.dump((Authority,SearchData),file,-1)
    logging.info(Authority)
    logging.info(SearchData)
    logging.info('Successful exit')

def loginSuccess():
    global dlG
    dlG = DlgMain(searchW)
    searchW.showSearchMain()
	
def logging_out(logFilename):
	'''Output log to file and console'''
	#Define a Handler and set a format while output to file
	logging.basicConfig(
	level = logging.INFO,  #大于此级别的都被输出
	format= '%(asctime)s %(filename)-20s: [%(levelname)s] %(message)s',  #定义格式
	datefmt = '%Y-%m-%d %A %H:%M:%S',   #时间格式
	filename = logFilename, #log文件名
	filemode = 'a'
	)

if __name__=="__main__":
    logging_out(var.log_file) #设置日志
    logging.info('\n\n')
    app = QApplication(sys.argv)
    app.setOrganizationName('Phabricator')
    app.setApplicationName('Ph')
    searchW = searchWindow()
    searchW.loginWindow.accepted.connect(loginSuccess)
    sys.exit(app.exec_())
