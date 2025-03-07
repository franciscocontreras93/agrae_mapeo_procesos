import os
from PyQt5.QtGui import QIcon, QPixmap

class aGraeGUI:
    def __init__(self):
        self.icons = {
         'BI' : QIcon(os.path.join(os.path.dirname(__file__), r'icons\BI.svg')),
         'GN' : QIcon(os.path.join(os.path.dirname(__file__), r'icons\GN.svg')),
         'login' : QIcon(os.path.join(os.path.dirname(__file__), r'icons\login.svg')),
         'logo' : QPixmap(os.path.join(os.path.dirname(__file__), r'icons\logo.png')),
         'save' : QIcon(os.path.join(os.path.dirname(__file__), r'icons\save.svg')),
         'trash' : QIcon(os.path.join(os.path.dirname(__file__), r'icons\trash.svg')),
         'user' : QIcon(os.path.join(os.path.dirname(__file__), r'icons\user.svg')),
         
         

        }
        return
    
    
    
    def getIcon(self,icon:str):
        return self.icons[icon]