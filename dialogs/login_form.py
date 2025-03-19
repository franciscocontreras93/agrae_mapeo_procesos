import requests
import os

from typing import List

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import Qt,pyqtSignal, QSettings, QVariant,QSize
from qgis.PyQt.QtGui import QPixmap,QImage
from qgis.gui import QgsPasswordLineEdit

from ..db import connectionDriver
from ..gui import aGraeGUI
from ..core.tools import aGraeTools


import asyncio
import aiohttp


class LoginForm(QDialog):
    idsExplotacionesSignal = pyqtSignal(dict)
    sessionTokenSignal = pyqtSignal(dict)
    def __init__(self):
        super().__init__()

        self.initUI()
    def initUI(self):
        self.setWindowTitle('Mapeo Integral | Inicio de Sesion')
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setAlignment(Qt.AlignVCenter)
        self.mainLayout.setSpacing(50);
        self.mainLayout.setContentsMargins(25, 50, 25, 50)
        logo = aGraeGUI().getIcon('logo')
        logo = logo.scaled(200, 200, Qt.KeepAspectRatio)
        self.logo = QLabel(self)
        self.logo.setPixmap(logo)
        self.logo.setScaledContents(True)
        self.line_user = QLineEdit()
        self.line_user.setPlaceholderText('Usuario')
        self.line_user.setStyleSheet("""
        QLineEdit {
            width: 13em;
            padding: 0.75em;
            border: 0;
            box-sizing: border-box;
            font-size: 1.5em;
            }
        """)
        self.line_password = QgsPasswordLineEdit()
        self.line_password.setPlaceholderText('Contraseña')
        self.line_password.setStyleSheet("""
        QLineEdit {
            width: 13em;
            padding: 0.75em;
            border: 0;
            box-sizing: border-box;
            font-size: 1.5em;
            }
        """)

        self.btn_login = QPushButton('Iniciar Sesion')
        self.btn_login.setMinimumSize(100,50)
        self.btn_login.setAccessibleName('btn_login')
        self.btn_login.clicked.connect(self.login)
        self.btn_login.setStyleSheet("""
                           QPushButton { color:#c5e7c2; 
                                     background-color: #01b032; 
                                     border: 5px solid #fff; 
                                     border-radius: 8px;
                                     padding: 1px 5px;
                                     font-weight: bold;
                                     font-size: 1.5em;
                                     }
                            QPushButton:hover {  
                                     background-color: #188f1c; 
                                     }
                            QPushButton:pressed {  
                                     border: 4px solid #a0d69e; 
                                     }
                           """)
        # self.mainLayout.addWidget(QLabel('Inicio de Sesion en la Aplicacion'))
        self.mainLayout.addWidget(self.logo)
        self.mainLayout.addWidget(self.line_user)
        self.mainLayout.addWidget(self.line_password)
        self.mainLayout.addWidget(self.btn_login)

        self.setLayout(self.mainLayout)
        # self.setStyleSheet();

    def login(self):
        user = self.line_user.text()
        password = self.line_password.text()
        # print(user,password)
        if user != '' and password != '':
            response = requests.post(f"{aGraeTools().endpoint_url}/token?username={user}&password={password}")
            token_data = response.json()
            if response.status_code == 200:
                token_data['nif'] = user
                self.sessionTokenSignal.emit(token_data)
                QMessageBox.information(self, 'Mapeo Integral | aGrae', 'Sesion Iniciada.'.format())
                self.close()
                
                # headers = {'Authorization': '{} {}'.format(token_data['token_type'],token_data['access_token'])}
                # response = requests.get(f"{aGraeTools().endpoint_url}/get_ids/?nif={user_nif}",headers=headers)
                # data = response.json()
                # if data:
                #     self.idsExplotacionesSignal.emit(data)
                

                
                
           
    
