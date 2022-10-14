import sys
from MainGUI import Ui_MainWindow
from PyQt5 import QtWidgets
from Database import Create_Database

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Create_Database()
    mainGUI = Ui_MainWindow()
    mainGUI.show()
    sys.exit(app.exec())