import aiohttp
import asyncio
import csv
import json
import openpyxl
import requests

from PyQt5.QtWidgets import (QFileDialog, QWidget, QTreeWidget, QTreeWidgetItem,
                             QPushButton, QHBoxLayout, QGridLayout, QDialog,
                             QCheckBox, QMessageBox, QLineEdit, QInputDialog,
                             QFormLayout, QLabel, QTabWidget, QTextEdit, QVBoxLayout)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QDateTime

from ..core.tools import aGraeTools  # Import aGraeTools
from ..gui import aGraeGUI



class UserUpdateThread(QThread):
    """
    Thread to update the user's status (active/inactive) in the API asynchronously.
    """
    updateFinished = pyqtSignal(int, str)

    def __init__(self, token, user_id, is_active):
        super().__init__()
        self.token = token
        self.user_id = user_id
        self.is_active = is_active

    def run(self):
        headers = aGraeTools().get_OAuth_headers(self.token)
        try:
            response = requests.put(
                f"{aGraeTools().endpoint_url}/api/user_app/update_status/?nif={self.user_id}&status={self.is_active}",
                headers=headers
            )
            self.updateFinished.emit(response.status_code, self.user_id)
        except requests.exceptions.RequestException as e:
            self.updateFinished.emit(500, self.user_id)  # Simulate an error

class UserDeleteThread(QThread):
    """
    Thread to delete a user from the API asynchronously.
    """
    deleteFinished = pyqtSignal(int, str)

    def __init__(self, token, user_id):
        super().__init__()
        self.token = token
        self.user_id = user_id

    def run(self):
        headers = aGraeTools().get_OAuth_headers(self.token)
        try:
            response = requests.delete(
                f"{aGraeTools().endpoint_url}/api/user_app/delete/?nif={self.user_id}",
                headers=headers
            )
            self.deleteFinished.emit(response.status_code, self.user_id)
        except requests.exceptions.RequestException as e:
            self.deleteFinished.emit(500, self.user_id)  # Simulate an error

class LogsLoadThread(QThread):
    """
    Thread to load logs from the API asynchronously.
    """
    logsLoaded = pyqtSignal(list)

    def __init__(self, token, idexplotacion):
        super().__init__()
        self.token = token
        self.idexplotacion = idexplotacion

    def run(self):
        headers = aGraeTools().get_OAuth_headers(self.token)
        try:
            response = requests.get(
                f"{aGraeTools().endpoint_url}/api/user_access_logs?username={self.token['nif']}",
                headers=headers
            )
            if response.status_code == 200:
                print(response.json())
                self.logsLoaded.emit(response.json())
            else:
                 self.logsLoaded.emit([])
        except requests.exceptions.RequestException as e:
            self.logsLoaded.emit([])

class IconButton(QPushButton):
    """
    A custom QPushButton that displays an icon and optional text.

    Args:
        icon_path (str or QIcon): The path to the icon file or a QIcon object.
        text (str, optional): The text to display on the button. Defaults to None.
        icon_size (QSize or tuple, optional): The size of the icon. Defaults to QSize(16, 16).
        parent (QWidget, optional): The parent widget. Defaults to None.
    """

    def __init__(self, icon_path, text=None, icon_size=QSize(16, 16), parent=None):
        super().__init__(parent)

        if isinstance(icon_path, str):
            icon = QIcon(icon_path)
        elif isinstance(icon_path, QIcon):
            icon = icon_path
        else:
            raise TypeError("icon_path must be a string or a QIcon object")

        self.setIcon(icon)
        self.setIconSize(icon_size)

        self.setFlat(True)
        self.setMaximumWidth(30)

        if text:
            self.setToolTip(text)

    def set_icon_size(self, size: QSize):
        self.setIconSize(size)


class AddUserDialog(QDialog):
    """
    Dialog to add a new user.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Nuevo Usuario")
        self.layout = QFormLayout(self)
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addRow("Usuario:", self.username_input)
        self.layout.addRow("Contraseña:", self.password_input)
        self.add_button = QPushButton("Agregar", self)
        self.add_button.clicked.connect(self.accept)
        self.layout.addWidget(self.add_button)

    def get_user_data(self):
        return self.username_input.text(), self.password_input.text()


class UsersDialog(QDialog):
    def __init__(self, token, idexplotacion,nameExp):
        super().__init__()
        self.setWindowTitle(f"Gestion de Usuarios | Mapeo Integral | Usuario: {token['nif']} ")
        self.token = token
        self.idexplotacion = idexplotacion
        self.nameExp = nameExp
        self.log_messages = []
        self.logs = []  # Clear existing logs
        self.initUI()
        self.setFixedSize(600, 400)
        asyncio.run(self.fill_tree())
        self.load_logs()

    def initUI(self):
        main_layout = QVBoxLayout()

        main_layout.addWidget(QLabel(f'Explotacion: {self.nameExp}'))

        self.tab_widget = QTabWidget()

        # --- Users Tab ---
        self.users_tab = QWidget()
        self.users_layout = QGridLayout(self.users_tab)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Usuario", "Activo", "Acciones"])
        self.tree.setColumnCount(3)
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 50)
        self.tree.setColumnWidth(2, 100)
        self.tree.setIconSize(QSize(13, 13))
        # allow edit text
        self.tree.setEditTriggers(QTreeWidget.DoubleClicked | QTreeWidget.EditKeyPressed)
        self.tree.itemChanged.connect(self.item_changed)

        # Add Label Count
        self.users_count_label = QLabel('Usuarios Disponibles: ')
        # Add button
        self.add_user_button = QPushButton("Agregar Usuario")
        self.add_user_button.clicked.connect(self.add_user)
        self.add_user_button.setMaximumWidth(100)

        self.users_layout.addWidget(self.users_count_label, 0, 0)
        self.users_layout.addWidget(self.add_user_button, 0, 1)
        self.users_layout.addWidget(self.tree, 1, 0, 1, 0)
        
        self.tab_widget.addTab(self.users_tab, "Usuarios")

        # --- Logs Tab ---
        self.logs_tab = QWidget()
        self.logs_layout = QVBoxLayout(self.logs_tab)

        self.action_export_csv = aGraeTools().getAction(self, 'Exportar a CSV',callback= lambda: self.export_logs('csv'))
        self.action_export_excel = aGraeTools().getAction(self, 'Exportar a XLSX',callback=lambda: self.export_logs('excel'))
        self.action_export_json = aGraeTools().getAction(self, 'Exportar a JSON',callback=lambda: self.export_logs('json'))
        
        self.export_buttons = aGraeTools().getToolButton([self.action_export_csv,self.action_export_excel,self.action_export_json])
        self.export_buttons.setText('Exportar Logs')
        
        

        self.logs_layout.addWidget(self.export_buttons)

        self.logs_text_edit = QTextEdit()
        self.logs_text_edit.setReadOnly(True)
        self.logs_layout.addWidget(self.logs_text_edit)
        self.tab_widget.addTab(self.logs_tab, "Logs")

        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

    def add_log(self, message):
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_messages.append(log_entry)
        self.logs_text_edit.append(log_entry)

    async def fill_tree(self):
        headers = aGraeTools().get_OAuth_headers(self.token)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        f"{aGraeTools().endpoint_url}/api/users_app/?idexplotacion={self.idexplotacion}",
                        headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # self.add_log(f"Usuarios cargados exitosamente: {len(data)}.")
                        self.users_count_label.setText(f'Usuarios Disponibles: {len(data)} / 10')
                        for user in data:
                            await self.add_user_to_tree(user)
                    else:
                        # self.add_log(f"Error al cargar usuarios. Código: {response.status}. Reinicia sesión e intenta nuevamente.")
                        QMessageBox.information(self, 'Mapeo Integral | aGrae',
                                                f'Ocurrio un error al cargar los usuarios, codigo: {response.status}, reinicia sesion he intenta nuevamente')
        except aiohttp.ClientError as e:
            # self.add_log(f"Error de conexión: {str(e)}")
            QMessageBox.critical(self, "Error", f"Ocurrio un error de conexion. {str(e)}")
        except Exception as e:
            # self.add_log(f"Error inesperado: {str(e)}")
            QMessageBox.critical(self, "Error", f"Ocurrio un error inesperado. {str(e)}")

    async def add_user_to_tree(self, user):
        item = QTreeWidgetItem(self.tree)
        item.setText(0, user['cif'])
        item.setFlags(item.flags() | Qt.ItemIsEditable)  # Make item editable

        # Checkbox for Active/Inactive
        checkbox = QCheckBox()
        checkbox.setChecked(user['user_exist'])
        checkbox.stateChanged.connect(
            lambda state, item=item, user_id=user['cif']: self.user_active_changed(state, item, user_id))

        # Widget to hold buttons
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Actions

        action_edit = aGraeTools().getAction(self, 'Guardar cambios', aGraeGUI().getIcon('save'),
                                             callback=lambda _, item=item, user_data=user: self.edit_item(item,
                                                                                                           user_data))

        # Buttons

        button_edit = IconButton(aGraeGUI().getIcon('save'), 'Guardar Cambios')
        button_edit.clicked.connect(
            lambda _, item=item, user_data=user: self.edit_item(item, user_data))
        button_delete = IconButton(aGraeGUI().getIcon('trash'), 'Eliminar Usuario')
        button_delete.clicked.connect(lambda _, item=item, user_id=user['cif']: self.delete_item(item, user_id))

        layout.addWidget(button_edit)
        layout.addWidget(button_delete)
        widget.setLayout(layout)

        # Add to the tree
        if user['cif'] == self.token['nif']:
            item.setTextAlignment(0, Qt.AlignLeft | Qt.AlignVCenter)
            item.setIcon(0, aGraeGUI().getIcon('user'))
            button_delete.setEnabled(False)

        self.tree.setItemWidget(item, 1, checkbox)
        self.tree.setItemWidget(item, 2, widget)
        self.tree.addTopLevelItem(item)

    def item_changed(self, item, column):
        if column == 0:
            new_text = item.text(0)
            # self.add_log(f"Item text changed to: {new_text}")
            print(f"Item text changed to: {new_text}")
            # here you can add code for change the text in the API

    def add_user(self):
        dialog = AddUserDialog(self)
        if dialog.exec_():
            username, password = dialog.get_user_data()
            if username and password:
                self.create_user_in_api(username, password)
            else:
                # self.add_log("Error: No se completo la informacion de usuario")
                QMessageBox.warning(self, "Advertencia", "Por favor, completa todos los campos.")

    def create_user_in_api(self, username, password):
        headers = aGraeTools().get_OAuth_headers(self.token)
        try:
            response = requests.post(f"{aGraeTools().endpoint_url}/api/user_app/create/",
                                     headers=headers,
                                     data={'nif': username, 'password': password, 'idexplotacion': self.idexplotacion})
            if response.status_code == 201:
                user = response.json()
                # self.add_log(f"Usuario {username} creado exitosamente.")
                asyncio.run(self.add_user_to_tree(user))
                QMessageBox.information(self, "Exito", "Usuario creado exitosamente.")
            else:
                # self.add_log(f"Error al crear el usuario {username}. Código: {response.status_code}")
                QMessageBox.warning(self, "Error", f"No se pudo crear el usuario. ({response.status_code})")
        except requests.exceptions.RequestException as e:
            # self.add_log(f"Error de conexión al crear el usuario {username}: {str(e)}")
            QMessageBox.critical(self, "Error", f"Ocurrio un error de conexion. {str(e)}")

    def user_active_changed(self, state, item, user_id):
        """Called when the checkbox state is changed."""
        is_active = state == Qt.Checked
        # self.add_log(f"Usuario {item.text(0)} activo cambio a: {is_active}")
        print(f"User {item.text(0)} active state changed to: {is_active}")

        self.update_thread = UserUpdateThread(self.token, user_id, is_active)
        self.update_thread.updateFinished.connect(self.on_user_updated)
        self.update_thread.start()

    def on_user_updated(self, status_code, user_id):
        """Handles the response from the user update API call."""
        if status_code == 200:
            # self.add_log(f"Usuario {user_id} actualizado correctamente.")
            QMessageBox.information(self, 'Mapeo Integral | aGrae', 'Usuario actualizado correctamente'.format())
        else:
            # self.add_log(f"Error al actualizar el usuario {user_id}. Código: {status_code}")
            QMessageBox.information(self, 'Mapeo Integral | aGrae',
                                    'Ocurrio un error al modificar el estado del usuario, intentelo nuevamente'.format())

    def edit_item(self, item, user_data):
        """Called when the Edit button is clicked."""
        # self.add_log(f"Edit action triggered for: {item.text(0)}, data: {user_data}")
        print(f"Edit action triggered for: {item.text(0)}, data: {user_data}")
        # Add your code to open a dialog to edit user data here

    def delete_item(self, item, user_id):
        """Called when the Delete button is clicked."""
        # self.add_log(f"Delete action triggered for: {item.text(0)}")
        print(f"Delete action triggered for: {item.text(0)}")
        self.delete_thread = UserDeleteThread(self.token, user_id)
        self.delete_thread.deleteFinished.connect(lambda code, id: self.on_user_deleted(code, id, item))
        self.delete_thread.start()

    def on_user_deleted(self, status_code, user_id, item):
        """Handles the response from the user delete API call."""
        if status_code == 200:
            # self.add_log(f"Usuario {user_id} eliminado correctamente.")
            QMessageBox.information(self, 'Mapeo Integral | aGrae', 'Usuario eliminado correctamente'.format())
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                root = self.tree.invisibleRootItem()
                root.removeChild(item)
        else:
            # self.add_log(f"Error al eliminar el usuario {user_id}. Código: {status_code}")
            QMessageBox.information(self, 'Mapeo Integral | aGrae',
                                    'Ocurrio un error al eliminar el usuario, intentelo nuevamente'.format())

    def load_logs(self):
        self.logs_load_thread = LogsLoadThread(self.token, self.idexplotacion)
        self.logs_load_thread.logsLoaded.connect(self.on_logs_loaded)
        self.logs_load_thread.start()

    def on_logs_loaded(self, logs):
        """Handles the response from the logs load API call."""
        if logs:
            sorted_logs = sorted(logs, key=lambda x: x['login_time'], reverse=True)
            self.logs = []  # Clear existing logs

            for log in sorted_logs:
                try:
                    timestamp = log['login_time']
                    # Extract only up to seconds and adjust to local time
                    datetime_obj = QDateTime.fromString(timestamp, Qt.ISODateWithMs)
                    datetime_obj.setTimeSpec(Qt.UTC)
                    datetime_obj = datetime_obj.toLocalTime()
                    formatted_timestamp = datetime_obj.toString("yyyy-MM-dd hh:mm:ss")
                    message = f"Inicio de Sesion Exitoso. Usuario: {log['username']} ip: {log['ip_address']}"
                    self.logs.append({
                        'timestamp': formatted_timestamp,
                        'message': message
                    })
                    message_to_edit = f"[{formatted_timestamp}] {message}\n"
                    self.logs_text_edit.append(message_to_edit)
                except Exception as e:
                    self.add_log(f"Error al procesar un log: {str(e)}")

        else:
             self.logs_text_edit.append('error loading logs')

    def export_logs_csv(self):
        """Exports the logs to a CSV file."""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Exportar Logs a CSV", "", "CSV Files (*.csv)"
        )
        if file_name:
            try:
                with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['timestamp', 'message']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for log_entry in self.logs:
                        writer.writerow(log_entry)
                QMessageBox.information(self, 'Éxito', 'Logs exportados a CSV correctamente.')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error al exportar a CSV: {e}')

    def export_logs_excel(self):
        """Exports the logs to an Excel file."""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Exportar Logs a Excel", "", "Excel Files (*.xlsx)"
        )
        if file_name:
            try:
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                sheet.append(['timestamp', 'message'])  # Header row
                for log_entry in self.logs:
                    sheet.append([log_entry['timestamp'], log_entry['message']])
                workbook.save(file_name)
                QMessageBox.information(self, 'Éxito', 'Logs exportados a Excel correctamente.')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error al exportar a Excel: {e}')

    def export_logs_json(self):
        """Exports the logs to a JSON file."""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Exportar Logs a JSON", "", "JSON Files (*.json)"
        )
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as jsonfile:
                    json.dump(self.logs, jsonfile, ensure_ascii=False, indent=4)
                QMessageBox.information(self, 'Éxito', 'Logs exportados a JSON correctamente.')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error al exportar a JSON: {e}')


    def export_logs(self,format:str):
        if format == 'csv':
            self.export_logs_csv()
        elif format == 'excel':
            self.export_logs_excel()
        elif format == 'json':
            self.export_logs_json()