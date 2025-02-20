import os
from PyQt5.QtGui import QIcon, QPixmap

class aGraeGUI:
    def __init__(self):
        self.icons = {
         'logo' : QPixmap(os.path.join(os.path.dirname(__file__), r'icons\logo.png')),
         'login' : QIcon(os.path.join(os.path.dirname(__file__), r'icons\login.svg')),
         'BI' : QIcon(os.path.join(os.path.dirname(__file__), r'icons\BI.svg')),
         'GN' : QIcon(os.path.join(os.path.dirname(__file__), r'icons\GN.svg')),
         
         

        }
        return
    
    
    
    def getIcon(self,icon:str):
        return self.icons[icon]