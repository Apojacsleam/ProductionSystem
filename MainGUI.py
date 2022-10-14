from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QStringListModel
from Database import Query, Get_Name, Get_No, Delete_Feature, Delete_Individual, Delete_Rule
from Inference import Get_Konwledge_Network, Inference_Result
from Database import Reset_Database, Create_Database, Add_Feature, Add_Rule, Add_Individual
from PyQt5.QtWidgets import QMessageBox, QInputDialog


class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        Create_Database()
        self.__setupUi(self)
        self.__ComprehensiveDatabase__ = set()
        self.__AddData()
        self.startBtn_3.clicked.connect(self.__AddFeature)
        self.startBtn_4.clicked.connect(self.__dropFeature)
        self.startBtn_5.clicked.connect(self.__chooseComprehensive)
        self.startBtn_6.clicked.connect(self.__AddIndividual)
        self.startBtn_7.clicked.connect(self.__dropIndividual)
        self.startBtn_8.clicked.connect(self.__dropComprehensive)
        self.startBtn_10.clicked.connect(self.__dropRule)
        self.startBtn_11.clicked.connect(self.__AddRule)
        self.startBtn_12.clicked.connect(self.__ConditionInference)
        self.startBtn_13.clicked.connect(self.__Reset)

    def __AddData(self):
        self.__FeatureData__ = list(Query('''SELECT FeatureName FROM Feature''')['FeatureName'])
        self.__IndividualData__ = list(Query('''SELECT IndividualName FROM Individual''')['IndividualName'])
        self.__KonwledgeNetwork__ = Get_Konwledge_Network()
        self.__ComprehensiveSorted__ = list(self.__ComprehensiveDatabase__)
        self.__ComprehensiveSorted__.sort()
        self.__ComprehensiveData__ = list(Get_Name('Feature', x) for x in self.__ComprehensiveSorted__)
        self.__RuleData__ = Query("SELECT * FROM Rule;")
        self.__RuleStringList__ = []
        for i in range(len(self.__RuleData__)):
            RuleNameString = self.__RuleData__['RuleNo'][i] + ': '
            RuleNameString += '&'.join(
                [Get_Name('Feature', x) for x in self.__RuleData__['Condition'][i].split('&')])
            RuleNameString += '->'
            if self.__RuleData__['Result'][i][0] == 'I':
                RuleNameString += Get_Name('Individual', self.__RuleData__['Result'][i])
            else:
                RuleNameString += Get_Name('Feature', self.__RuleData__['Result'][i])
            self.__RuleStringList__.append(RuleNameString)
        Featureslm = QStringListModel()
        Featureslm.setStringList(self.__FeatureData__)
        self.listView.setModel(Featureslm)
        Individualslm = QStringListModel()
        Individualslm.setStringList(self.__IndividualData__)
        self.listView_2.setModel(Individualslm)
        Ruleslm = QStringListModel()
        Ruleslm.setStringList(self.__RuleStringList__)
        self.listView_4.setModel(Ruleslm)
        ComprehensiveDatabaseslm = QStringListModel()
        ComprehensiveDatabaseslm.setStringList(self.__ComprehensiveData__)
        self.listView_3.setModel(ComprehensiveDatabaseslm)

    def __Reset(self):
        Reset_Database()
        self.__ComprehensiveDatabase__ = set()
        self.__AddData()

    def __AddFeature(self):
        InputResult, SuccessfulInput = QInputDialog.getText(self, "增加事实", "请输入您想要增加的事实")
        if SuccessfulInput:
            QueryFeature = list(
                Query(f"SELECT FeatureNo, FeatureName FROM Feature WHERE FeatureName = '{InputResult}';")[
                    'FeatureName'])
            QueryIndividual = list(
                Query(f"SELECT IndividualNo, IndividualName FROM Individual WHERE IndividualName = '{InputResult}';")[
                    'IndividualName'])
            if len(QueryFeature) != 0:
                QMessageBox.critical(self, "增加事实失败", "增加事实失败！事实库中已有同名的事实！")
            elif len(QueryIndividual) != 0:
                QMessageBox.critical(self, "增加事实失败", "增加事实失败！事实不能与结果同名！")
            else:
                QMessageBox.information(self, "增加事实成功", "增加事实成功！")
                Add_Feature(InputResult)
                self.__AddData()

    def __dropFeature(self):
        try:
            dropFeatureName = self.listView.selectionModel().selectedIndexes()[0].data()
            dropFeatureNo = Get_No('Feature', dropFeatureName)
            Delete_Feature(dropFeatureNo)
            self.__ComprehensiveDatabase__.discard(dropFeatureNo)
            self.__AddData()
        except:
            print('Function __dropFeature Error')

    def __AddIndividual(self):
        InputResult, SuccessfulInput = QInputDialog.getText(self, "增加结果", "请输入您想要增加的结果")
        if SuccessfulInput:
            QueryFeature = list(
                Query(f"SELECT FeatureNo, FeatureName FROM Feature WHERE FeatureName = '{InputResult}';")[
                    'FeatureName'])
            QueryIndividual = list(
                Query(f"SELECT IndividualNo, IndividualName FROM Individual WHERE IndividualName = '{InputResult}';")[
                    'IndividualName'])
            if len(QueryIndividual) != 0:
                QMessageBox.critical(self, "增加结果失败", "增加结果失败！结果库中已有同名的结果！")
            elif len(QueryFeature) != 0:
                QMessageBox.critical(self, "增加结果失败", "增加结果失败！结果不能与事实同名！")
            else:
                QMessageBox.information(self, "增加结果成功", "增加结果成功！")
                Add_Individual(InputResult)
                self.__AddData()

    def __dropIndividual(self):
        try:
            dropIndividualName = self.listView_2.selectionModel().selectedIndexes()[0].data()
            Delete_Individual(Get_No('Individual', dropIndividualName))
            self.__AddData()
        except:
            print('Function __dropIndividual error!')

    def __AddRule(self):
        try:
            if len(self.__ComprehensiveSorted__) == 0:
                QMessageBox.critical(self, "增加规则失败", "增加规则失败！综合数据库中没有事实！")
            else:
                ConditionName = '&'.join(self.__ComprehensiveSorted__)
                QueryCondition = Query(f"SELECT Condition FROM Rule WHERE Condition = '{ConditionName}';")
                if len(QueryCondition) != 0:
                    QMessageBox.critical(self, "增加规则失败", "增加规则失败！规则数据库中已有相同前提的规则！")
                else:
                    ConditionStr = "、".join(self.__ComprehensiveData__)
                    InputResult, SuccessfulInput = QInputDialog.getText(self, "增加规则",
                                                                        "您想要增加规则的条件是：" + ConditionStr + "\n请输入您所增加规则的结果")
                    if SuccessfulInput:
                        QueryRule = []
                        QueryFeature = list(
                            Query(f"SELECT FeatureNo FROM Feature WHERE FeatureName = '{InputResult}';")['FeatureNo'])
                        QueryIndividual = list(
                            Query(f"SELECT IndividualNo FROM Individual WHERE IndividualName = '{InputResult}';")[
                                'IndividualNo'])
                        QueryRule.extend(QueryFeature)
                        QueryRule.extend(QueryIndividual)
                        if len(QueryRule) == 0:
                            QMessageBox.critical(self, "增加规则失败",
                                                 "增加规则失败！事实数据库和结果数据库中均没有与结论同名的项！")
                        else:
                            Add_Rule(ConditionName, QueryRule[0])
                            self.__AddData()
        except:
            pass

    def __dropRule(self):
        try:
            Delete_Rule(self.listView_4.selectionModel().selectedIndexes()[0].data().split(": ")[0])
            self.__AddData()
        except:
            print('Function __dropRule error!')

    def __chooseComprehensive(self):
        try:
            FeatureName = self.listView.selectionModel().selectedIndexes()[0].data()
            FeatureNo = Get_No('Feature', FeatureName)
            self.__ComprehensiveDatabase__.add(FeatureNo)
            self.__AddData()
        except:
            print('Function __chooseComprehensive error!')

    def __dropComprehensive(self):
        try:
            FeatureName = self.listView_3.selectionModel().selectedIndexes()[0].data()
            FeatureNo = Get_No('Feature', FeatureName)
            self.__ComprehensiveDatabase__.remove(FeatureNo)
            self.__AddData()
        except:
            print('Function __dropComprehensive error!')

    def __ConditionInference(self):
        try:
            self.textEdit.clear()
            ResultList = Inference_Result(self.__ComprehensiveSorted__, self.__KonwledgeNetwork__)
            self.textEdit.setText(ResultList[0])
            for i in range(1, len(ResultList)):
                self.textEdit.append(ResultList[i])
        except:
            print('Function __ConditionInference error!')

    def __setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1350, 760)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.listView = QtWidgets.QListView(self.centralwidget)
        self.listView.setGeometry(QtCore.QRect(30, 170, 201, 321))
        self.listView.setStyleSheet("font: 16pt \"宋体\";")
        self.listView.setObjectName("listView")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(90, 130, 81, 31))
        font = QtGui.QFont()
        font.setFamily("华文中宋")
        font.setPointSize(20)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_6.setFont(font)
        self.label_6.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_6.setStyleSheet("font: 20pt \"华文中宋\";")
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.startBtn_3 = QtWidgets.QPushButton(self.centralwidget)
        self.startBtn_3.setGeometry(QtCore.QRect(30, 500, 91, 41))
        self.startBtn_3.setStyleSheet("font: 16pt \"楷体\";")
        self.startBtn_3.setObjectName("startBtn_3")
        self.startBtn_4 = QtWidgets.QPushButton(self.centralwidget)
        self.startBtn_4.setGeometry(QtCore.QRect(130, 500, 101, 41))
        self.startBtn_4.setStyleSheet("font: 16pt \"楷体\";")
        self.startBtn_4.setObjectName("startBtn_4")
        self.startBtn_5 = QtWidgets.QPushButton(self.centralwidget)
        self.startBtn_5.setGeometry(QtCore.QRect(30, 550, 201, 41))
        self.startBtn_5.setStyleSheet("font: 16pt \"楷体\";")
        self.startBtn_5.setObjectName("startBtn_5")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(320, 130, 91, 31))
        font = QtGui.QFont()
        font.setFamily("华文中宋")
        font.setPointSize(20)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_7.setFont(font)
        self.label_7.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_7.setStyleSheet("font: 20pt \"华文中宋\";")
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.startBtn_10 = QtWidgets.QPushButton(self.centralwidget)
        self.startBtn_10.setGeometry(QtCore.QRect(930, 500, 201, 41))
        self.startBtn_10.setStyleSheet("font: 16pt \"楷体\";")
        self.startBtn_10.setObjectName("startBtn_10")
        self.listView_4 = QtWidgets.QListView(self.centralwidget)
        self.listView_4.setGeometry(QtCore.QRect(720, 170, 411, 321))
        self.listView_4.setStyleSheet("font: 12pt \"宋体\";")
        self.listView_4.setObjectName("listView_4")
        self.startBtn_11 = QtWidgets.QPushButton(self.centralwidget)
        self.startBtn_11.setGeometry(QtCore.QRect(720, 500, 201, 41))
        self.startBtn_11.setStyleSheet("font: 16pt \"楷体\";")
        self.startBtn_11.setObjectName("startBtn_11")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(790, 130, 261, 31))
        font = QtGui.QFont()
        font.setFamily("华文中宋")
        font.setPointSize(20)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_9.setFont(font)
        self.label_9.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_9.setStyleSheet("font: 20pt \"华文中宋\";")
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.startBtn_12 = QtWidgets.QPushButton(self.centralwidget)
        self.startBtn_12.setGeometry(QtCore.QRect(1160, 170, 151, 121))
        self.startBtn_12.setStyleSheet("font: 30pt \"华文隶书\";")
        self.startBtn_12.setObjectName("startBtn_12")
        self.splitter_2 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_2.setGeometry(QtCore.QRect(240, 50, 880, 40))
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.label_2 = QtWidgets.QLabel(self.splitter_2)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_2.setStyleSheet("font: 16pt \"Times New Roman\";")
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(240, 0, 880, 40))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.label = QtWidgets.QLabel(self.splitter)
        font = QtGui.QFont()
        font.setFamily("华文中宋")
        font.setPointSize(30)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setStyleSheet("font: 30pt \"华文中宋\";")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(1160, 310, 151, 31))
        font = QtGui.QFont()
        font.setFamily("华文中宋")
        font.setPointSize(20)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_11.setFont(font)
        self.label_11.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_11.setStyleSheet("font: 20pt \"华文中宋\";")
        self.label_11.setAlignment(QtCore.Qt.AlignCenter)
        self.label_11.setObjectName("label_11")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(1140, 350, 201, 191))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.textEdit.setFont(font)
        self.textEdit.setObjectName("textEdit")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(420, 600, 491, 81))
        self.label_3.setText("")
        self.label_3.setPixmap(QtGui.QPixmap("logo.png"))
        self.label_3.setScaledContents(True)
        self.label_3.setObjectName("label_3")
        self.listView_2 = QtWidgets.QListView(self.centralwidget)
        self.listView_2.setGeometry(QtCore.QRect(260, 170, 201, 321))
        self.listView_2.setStyleSheet("font: 16pt \"宋体\";")
        self.listView_2.setObjectName("listView_2")
        self.startBtn_6 = QtWidgets.QPushButton(self.centralwidget)
        self.startBtn_6.setGeometry(QtCore.QRect(260, 500, 91, 41))
        self.startBtn_6.setStyleSheet("font: 16pt \"楷体\";")
        self.startBtn_6.setObjectName("startBtn_6")
        self.startBtn_7 = QtWidgets.QPushButton(self.centralwidget)
        self.startBtn_7.setGeometry(QtCore.QRect(360, 500, 101, 41))
        self.startBtn_7.setStyleSheet("font: 16pt \"楷体\";")
        self.startBtn_7.setObjectName("startBtn_7")
        self.startBtn_8 = QtWidgets.QPushButton(self.centralwidget)
        self.startBtn_8.setGeometry(QtCore.QRect(490, 500, 201, 41))
        self.startBtn_8.setStyleSheet("font: 16pt \"楷体\";")
        self.startBtn_8.setObjectName("startBtn_8")
        self.listView_3 = QtWidgets.QListView(self.centralwidget)
        self.listView_3.setGeometry(QtCore.QRect(490, 170, 201, 321))
        self.listView_3.setStyleSheet("font: 16pt \"宋体\";")
        self.listView_3.setObjectName("listView_3")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(520, 130, 141, 31))
        font = QtGui.QFont()
        font.setFamily("华文中宋")
        font.setPointSize(20)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_8.setFont(font)
        self.label_8.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_8.setStyleSheet("font: 20pt \"华文中宋\";")
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.startBtn_13 = QtWidgets.QPushButton(self.centralwidget)
        self.startBtn_13.setGeometry(QtCore.QRect(1140, 550, 201, 141))
        self.startBtn_13.setStyleSheet("font: 20pt \"华文隶书\";")
        self.startBtn_13.setObjectName("startBtn_13")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(30, 600, 351, 192))
        self.textBrowser.setObjectName("textBrowser")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(550, 710, 281, 16))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1350, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.__retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def __retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "基于知识图谱表示的植物类型产生式推理系统"))
        self.label_6.setText(_translate("MainWindow", "事实库"))
        self.startBtn_3.setText(_translate("MainWindow", "增加"))
        self.startBtn_4.setText(_translate("MainWindow", "删除"))
        self.startBtn_5.setText(_translate("MainWindow", "选入综合数据库"))
        self.label_7.setText(_translate("MainWindow", "结果库"))
        self.startBtn_10.setText(_translate("MainWindow", "删除"))
        self.startBtn_11.setText(_translate("MainWindow", "增加"))
        self.label_9.setText(_translate("MainWindow", "规则库"))
        self.startBtn_12.setText(_translate("MainWindow", "推理"))
        self.label_2.setText(_translate("MainWindow", "学号：20002527      姓名：刘浩然      班级：计金(双)200班"))
        self.label.setText(_translate("MainWindow", "基于知识图谱表示的植物类型产生式推理系统"))
        self.label_11.setText(_translate("MainWindow", "推理结果"))
        self.startBtn_6.setText(_translate("MainWindow", "增加"))
        self.startBtn_7.setText(_translate("MainWindow", "删除"))
        self.startBtn_8.setText(_translate("MainWindow", "删除"))
        self.label_8.setText(_translate("MainWindow", "综合数据库"))
        self.startBtn_13.setText(_translate("MainWindow", "恢复初始数据"))
        self.textBrowser.setHtml(_translate("MainWindow",
                                            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                            "p, li { white-space: pre-wrap; }\n"
                                            "</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:600; font-style:normal;\">\n"
                                            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">请注意：</p>\n"
                                            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">1.开始推理前，请把推理所需的条件选入综合数据库中。</p>\n"
                                            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">2.添加规则时，所需的条件和结果都必须在对应数据库中。</p>\n"
                                            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">3.删除事实和结果时，综合数据库和规则库中的对应数据也会删除。</p>\n"
                                            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">4.程序无反应时，请点击回复初始数据按钮。</p>\n"
                                            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">5.本程序只用于人工智能课程学习。</p></body></html>"))
        self.label_4.setText(_translate("MainWindow", "(C) 2022 Haoran Liu. All rights reserved."))
