import os

from qgis.PyQt import  uic
from qgis.PyQt.QtCore import pyqtSignal, Qt, QDate, QSize, QSettings, QPoint
from qgis.PyQt.QtGui import QIcon, QContextMenuEvent, QAction
from qgis.PyQt.QtWidgets import QMenu,QMessageBox

from qgis.core import *
from qgis.utils import iface
from qgis.gui import QgsMapToolIdentify, QgsMapMouseEvent

from ..core.tools import aGraeTools
from ..dialogs.analitica_dialog import AnaliticaDialog


import asyncio
import aiohttp


class selectTool(QgsMapToolIdentify):
    featureSelected = pyqtSignal(QgsFeature)

    def __init__(self, layer: QgsMapLayer, sessionToken):
        super().__init__(iface.mapCanvas())
        self.sessionToken = sessionToken
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.layer = layer  # Store the layer, don't change it after initialization
        iface.setActiveLayer(self.layer)
        self.context_menu = self.create_context_menu()  # Create the context menu


    def active_changed(self, layer):
        if isinstance(layer, QgsVectorLayer) and layer.isSpatial():
            self.layer = layer

    def canvasPressEvent(self, event):
        # Check if it's a right-click
        if event.button() == Qt.RightButton:
            self.canvasRightClickEvent(event)
        else:
            # Check if the layer is valid before proceeding
            if self.layer and self.layer.isValid():
                results = self.identify(event.x(), event.y(), [self.layer], QgsMapToolIdentify.TopDownAll)
                if len(results) == 1:
                    feature = results[0].mFeature
            else:
                QMessageBox.warning(None, "Advertencia | Mapeo Integral", "La capa no es Valida.")

    def canvasRightClickEvent(self, event: QgsMapMouseEvent):
        """
        Handles right-click events on the map canvas.

        Args:
            event (QgsMapMouseEvent): The map mouse event.
        """
        # Check if the layer is valid before proceeding
        if self.layer and self.layer.isValid():
            results = self.identify(event.x(), event.y(), [self.layer], QgsMapToolIdentify.TopDownAll)

            if results:
                # If a feature is found, show the context menu
                feature = results[0].mFeature
                self.selected_feature = feature  # Store the selected feature

                # Fallback: Use globalX() and globalY() to create a QPoint
                global_x = event.globalX()
                global_y = event.globalY()
                global_pos = QPoint(global_x, global_y)

                # Show the context menu at the mouse position
                self.context_menu.exec(global_pos)
        else:
            print("Capa no valida.")

    def create_context_menu(self):
        """
        Creates the context menu for right-click actions.

        Returns:
            QMenu: The context menu.
        """
        menu = QMenu()

        # Example Action 1: Print Feature Attributes
        print_attributes_action = QAction("Analisis de Suelos del Lote", self)
        print_attributes_action.triggered.connect(self.run_my_async_task)
        menu.addAction(print_attributes_action)

        # Example Action 2: Show Feature ID
        show_feature_id_action = QAction("Mostrar ID", self)
        show_feature_id_action.triggered.connect(self.show_feature_id)
        menu.addAction(show_feature_id_action)

        # Add more actions here as needed...

        return menu

    async def get_data_analitica(self):
        """
        Prints the attributes of the selected feature to the console.
        """
        if hasattr(self, "selected_feature"):
            feature = self.selected_feature
            # try:
            headers = aGraeTools().get_OAuth_headers(self.sessionToken)
            params = {
                'iddata':  feature['iddata']
                }
            
            dataLote = { field.name(): feature[field.name()] for field in feature.fields()} 

            response = await aGraeTools().fetch_data_async('/api/app/data_analitica',method='GET',params=params,headers=headers)
            if response:
                # Show the AnaliticaDialog with the data
                print(response)
                dialog = AnaliticaDialog(dataLote,response,self.sessionToken['nif'])
                dialog.exec()
            else:
                QMessageBox.warning(None, "Advertencia | Mapeo Integral", "No se pudieron obtener los datos.")
            # except Exception as ex:
            #     print(ex)
            
        else:
            QMessageBox.warning(None, "Advertencia | Mapeo Integral", "Debe seleccionar un Lote")
            
    def show_feature_id(self):
        """
        Shows a message box with the ID of the selected feature.
        """
        if hasattr(self, "selected_feature"):
            feature_id = self.selected_feature.id()
            QMessageBox.information(None, "ID de la Feature", f"ID: {feature_id}")
        else:
            QMessageBox.warning(None, "Advertencia | Mapeo Integral", "Debe seleccionar un Lote")

    def deactivate(self):
        pass


    
            
        
    def run_my_async_task(self):
        asyncio.run(self.get_data_analitica())