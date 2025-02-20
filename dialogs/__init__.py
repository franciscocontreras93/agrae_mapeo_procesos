from .login_form import LoginForm

class aGraeDialogs:
    def loginDialog(self,func):
        dlg = LoginForm()
        dlg.sessionTokenSignal.connect(func)
        dlg.exec()