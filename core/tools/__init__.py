# c:\Users\Ing_G\AppData\Roaming\QGIS\QGIS3\profiles\AGRAE_LITE\python\plugins\aGrae_app\core\tools\__init__.py
import aiohttp
import asyncio
import json
import os
import requests
import tempfile

from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface
from qgis.core import *
from qgis.PyQt.QtCore import Qt, QVariant, QSettings, QSize, QDateTime, pyqtSignal


class aGraeTools():
    MuestreoEndSignal = pyqtSignal(bool)

    def __init__(self):
        self.instance = QgsProject.instance()
        self.plugin_name = 'aGrae Toolbox'
        self.endpoint_url = 'http://142.93.41.109:8000'
        # self.endpoint_url = 'http://127.0.0.1:8000'

    def settingsToolsButtons(self, toolbutton, actions=None, icon: QIcon = None, setMainIcon=False):
        """_summary_

        Args:
            toolbutton (QToolButton): QToolButton Widget
            actions (QAction, optional): Actions added to toolbutton menu, the default action must be in index 0 of list.

        """
        toolbutton.setMenu(QMenu())
        toolbutton.setPopupMode(QToolButton.MenuButtonPopup)
        toolbutton.setIconSize(QSize(15, 15))
        if actions:

            for i in range(len(actions)):
                toolbutton.menu().addAction(actions[i])

        if setMainIcon:
            toolbutton.setIcon(icon)
        else:
            toolbutton.setDefaultAction(actions[0])

    def getToolButton(self, actions=None, icon: QIcon = None, setMainIcon=False) -> QToolButton:
        toolButton = QToolButton()
        toolButton.setMenu(QMenu())
        toolButton.setPopupMode(QToolButton.MenuButtonPopup)
        toolButton.setIconSize(QSize(15, 15))
        if actions:

            for i in range(len(actions)):
                toolButton.menu().addAction(actions[i])

        if setMainIcon:
            toolButton.setIcon(icon)
        else:
            toolButton.setDefaultAction(actions[0])

        return toolButton

    def getAction(self, parent, text: str, icon=None, callback=None) -> QAction:
        action = QAction(text)
        if icon:
            action.setIcon(icon)
        if callback:
            action.triggered.connect(callback)

        return action

    def get_exp_ids(self, sessionToken: dict):
        url = f'{self.endpoint_url}/get_ids'
        params = {'nif': sessionToken['nif']}
        headers = {'Authorization': f'{sessionToken['token_type']} {sessionToken['access_token']}'}
        response = requests.get(url, params=params, headers=headers)
        return response.json()

    def get_OAuth_headers(self, sessionToken) -> dict:
        return {'Authorization': f'{sessionToken['token_type']} {sessionToken['access_token']}'}

    async def fetch_data(url, ):
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                return await response.json()

    # NEW: Asynchronous API Query Function
    async def fetch_data_async(self, endpoint, params=None, headers=None, method='GET', data=None) -> dict | None:
        """
        Asynchronously fetches data from an API endpoint using aiohttp.

        Args:
            endpoint (str): The API endpoint URL.
            params (dict, optional): Query parameters. Defaults to None.
            headers (dict, optional): HTTP headers. Defaults to None.
            method (str, optional): HTTP method (GET, POST, etc.). Defaults to 'GET'.
            data (dict, optional): Data to send for POST requests. Defaults to None.

        Returns:
            dict or None: The JSON response from the API if successful, None otherwise.
        """
        try:
            url = self.endpoint_url + endpoint
            async with aiohttp.ClientSession() as session:
                if method.upper() == 'GET':
                    async with session.get(url, params=params, headers=headers) as response:
                        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                        return await response.json()
                elif method.upper() == 'POST':
                    async with session.post(url, headers=headers, json=data) as response:
                        response.raise_for_status()
                        return await response.json()
                # Add other methods (PUT, DELETE, etc.) if needed...
                else:
                    QMessageBox.critical(None, "Error", f"Metodo HTTP invalido: {method}")
                    return None
        except aiohttp.ClientError as e:
            QMessageBox.critical(None, "Error", f"Error de conexion: {e}")
            return None
        except json.JSONDecodeError as e:
            QMessageBox.critical(None, "Error", f"Error al analizar la respuesta JSON: {e}")
            return None
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error inesperado: {e}")
            return None

    

class aGraeGISTools:
    def __init__(self):
        self.instance = QgsProject.instance()
        self.plugin_name = 'aGrae Toolbox'
        self.basemaps = {

            'Esri Satelite': {
                'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D',
                'options': 'crs=EPSG:3857&format&type=xyz&url=https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D&zmax=20&zmin=0'
            },
            'Google Satelite': {
                'url': 'https://mt1.google.com/vt/lyrs=s&x=%7Bx%7D&y=%7By%7D&z=%7Bz%7D',
                'options': 'type=xyz&zmin=0&zmax=20&url=https://mt1.google.com/vt/lyrs%3Ds%26x%3D{x}%26y%3D{y}%26z%3D{z}'
            },
            'PNOA Ortofoto': {
                'url': 'contextualWMSLegend=0&crs=EPSG:4326&dpiMode=7&featureCount=10&format=image/png&layers=OI.OrthoimageCoverage&styles',
                'options': 'url=https://www.ign.es/wms-inspire/pnoa-ma'
            },
            'Parcelas Catastro': {
                'url': 'contextualWMSLegend=1&crs=EPSG:4326&dpiMode=7&featureCount=10&format=image/png&layers=CP.CadastralParcel&styles',
                'options': 'url=http://ovc.catastro.meh.es/cartografia/INSPIRE/spadgcwms.aspx'
            }

        }

    def get_layer_app(self, endpoint: str, params: dict, sessionToken: dict, nameLayer: str) -> QgsVectorLayer:
        url = '{}{}'.format(aGraeTools().endpoint_url, endpoint)
        headers = aGraeTools().get_OAuth_headers(sessionToken)
        response = requests.get(url, params, headers=headers)

        if response.status_code == 200:
            geojson_data = response.json()

            with tempfile.NamedTemporaryFile(delete=False, suffix='.geojson', mode='w+') as temp_file:
                json.dump(geojson_data, temp_file)
                temp_file_path = temp_file.name

            layer = QgsVectorLayer(temp_file_path, nameLayer, "ogr")

            if layer.isValid():
                return layer
        else:
            QMessageBox.information(None, 'aGricultura de Precision | aGrae',
                                    'Ocurrio un error, reinicia sesion he intenta nuevamente'.format())

    async def get_layer_app_async(self, endpoint: str, params: dict, sessionToken: dict, nameLayer: str = 'layer',
                                  style: str = None) -> QgsVectorLayer:

        url = '{}{}'.format(aGraeTools().endpoint_url, endpoint)
        headers = aGraeTools().get_OAuth_headers(sessionToken)
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    geojson_data = await response.json()
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.geojson', mode='w+') as temp_file:
                        json.dump(geojson_data, temp_file)
                        temp_file_path = temp_file.name
                    layer = QgsVectorLayer(temp_file_path, nameLayer, "ogr")
                    if layer.isValid():
                        if style:
                            styleUri = os.path.join(os.path.dirname(__file__), 'styles/{}.qml'.format(style))
                            print(styleUri)
                            layer.loadNamedStyle(styleUri)
                        return layer
                    else:
                        QMessageBox.information(None, 'aGricultura de Precision | aGrae',
                                                'Ocurrio un error al cargar la capa, intentelo nuevamente'.format())
                else:
                    QMessageBox.information(None, 'aGricultura de Precision | aGrae',
                                            'Ocurrio un error, reinicia sesion he intenta nuevamente'.format())

    def get_layer(self, endpoint: str, sessionToken: dict, idcampania: int, idexplotacion: int, layername: str = 'layer',
                  style: str = None):
        layer = asyncio.run(
            self.get_layer_app_async(endpoint, {'idcampania': idcampania, 'idexplotacion': idexplotacion}, sessionToken,
                                     layername, style))
        return layer

    def get_layer_wms(self, basemap: str, layer_name: str):
        basemap = self.basemaps[basemap]
        url = basemap['url']
        options = basemap['options']
        urlWithParams = 'url={}&{}'.format(url, options)
        return QgsRasterLayer(urlWithParams, layer_name, 'wms')

    def load_wms_toc(self, sessionToken, basemap: QgsRasterLayer, layer_name: str):
        if sessionToken:
            raster_layer = self.get_layer_wms(basemap, layer_name)
            QgsProject.instance().addMapLayer(raster_layer)

            root = QgsProject.instance().layerTreeRoot()
            layer = root.findLayer(raster_layer.id())
            root.insertChildNode(-1, layer.clone())
            root.removeChildNode(layer)

    def load_layer(self, endpoint, nombre, token):
        if self.sessionToken:
            idcampania = self.comboCampanias.currentData()
            idexplotacion = self.comboExplotacion.currentData()
            QgsProject.instance().addMapLayer(
                self.get_layer(endpoint, token, idcampania, idexplotacion,
                               f'{self.comboCampanias.currentText()}-{self.comboExplotacion.currentText()}-{nombre}'))
