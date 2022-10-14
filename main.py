import sys
from MainGUI import Ui_MainWindow
from PyQt5 import QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainGUI = Ui_MainWindow()
    mainGUI.show()
    sys.exit(app.exec())