import os # This is the home library of Python / allow you to work directly with Windows
import sys # sys Import specific funktions
from PyQt5.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton #import the modules from PyQt5
#from PyQt5.QtWidgets import QPushButton


# 1. Add the QGIS paths for the connection with Python  and the Qt components
qgis_path = r"C:\Program Files\QGIS 3.34.14" # variable that connects QGIS 
os.environ["PATH"] = rf"{qgis_path}\bin;{qgis_path}\apps\qgis-ltr\bin;{qgis_path}\apps\Qt5\bin;" + os.environ["PATH"] #environ connect windows and python
os.environ["QT_PLUGIN_PATH"] = rf"{qgis_path}\apps\Qt5\plugins" #


class DlgMain(QDialog): # Classes can inherit from another class, where we define a class. We create a new class Dlg Main class... All properties and methods
    def __init__(self): # this is the first Method THE CONSTRUCTOR/ self refers to the the instance of the objetct that has been created. 
        super().__init__()
        self.setWindowTitle("My GUI") # we can start ading widgets and properties / we need to call all those methods on the self instance
        self.resize(400, 400) # we change the size of the Window



        self.ledText = QLineEdit("My GUI", self) # we create a new Textbox
        self.ledText.move(40, 50) # Size of the Textbox

        self.btnUpdate = QPushButton("Update Window Title", self)
        self.btnUpdate.move(45,70)
        self.btnUpdate.clicked.connect(self.evt_btnUpdate_clicked) # create an event / when the button is clicked then we connect with a method.. right below 

    def evt_btnUpdate_clicked(self): # Here we define a method, the same as we create a function
        self.setWindowTitle(self.ledText.text())


if __name__ == "__main__": # Python module can be imported from another python program / import modules and 
    app = QApplication(sys.argv) # create application
    dlgMain = DlgMain()            #create main  GUI canvas
    dlgMain.show()              #show the GUI
    sys.exit(app.exec_())           #execute the application

