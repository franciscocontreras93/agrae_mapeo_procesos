from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt 

from .users_dialog import UsersDialog
from .login_form import LoginForm
from .drive_dialog import DriveDialog
from .analitica_dialog import AnaliticaDialog


class aGraeDialogs:
    def loginDialog(self,func):
        dlg = LoginForm()
        dlg.sessionTokenSignal.connect(func)
        dlg.exec()
    
    def usersDialog(self,token,idexplotacion,nameExp):
        if idexplotacion:
            dlg = UsersDialog(token,idexplotacion,nameExp)
            dlg.exec()

    def diskSpaceDialog(self,sessionToken,idcampania,idexplotacion):
        if sessionToken:
            dlg = DriveDialog(sessionToken,idcampania,idexplotacion)
            dlg.exec()

    def analiticaDialog(self,data):
        dlg = AnaliticaDialog(data)
        dlg.exec() 