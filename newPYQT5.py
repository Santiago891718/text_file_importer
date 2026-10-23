import sys # sys Import specific funktions
from PyQt5.QtWidgets import QApplication, QWidget #Give us Access to PyQt5 Import different tools

app = QApplication (sys.argv) # (sys.argv is a Parameter) (app is a variable) with this we create the application

dlgMain = QWidget() #Main canvas (you can Change the Name of this) we create the canvas
dlgMain.setWindowTitle("My GUI") 
dlgMain.show() #Show the GUI

sys.exit(app.exec_()) #execute the application    -    in case there is a problem it will be pass to system 