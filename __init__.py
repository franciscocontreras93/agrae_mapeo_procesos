#-----------------------------------------------------------
# Copyright (C) 2015 Martin Dobias
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

from PyQt5.QtWidgets import QAction, QMessageBox,QToolButton, QComboBox, QLabel, QMenu
from PyQt5.QtCore import QCoreApplication, QSize, Qt
from PyQt5.QtGui import QIcon

from qgis.core import QgsProject,QgsRasterLayer

from .db import connectionDriver
from .dialogs import aGraeDialogs
from .gui import aGraeGUI
from .core.tools import aGraeTools,aGraeGISTools
from .core.identify import selectTool


import asyncio
import aiohttp

def classFactory(iface):
    return AgraeAPP(iface)


class AgraeAPP:
    def __init__(self, iface):
        self.iface = iface
        self.tools = aGraeTools()
        self.menu = self.tr(u'&Mapeo Integral | aGrae')
        self.toolbar = self.iface.addToolBar(u'&Mapeo Integral | aGrae')
        self.toolbar.setObjectName(u'&Mapeo Integral | aGrae')
        

        self.actions = []
        self.bi_actions = []
        self.mb_actions = []
        
        self.logged = False
        self.idcampanias = None
        self.campania_data  = {}

        self.sessionToken = None

        self.identifyTool = None

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('&aGricultura de Precision | aGrae', message)
    
    def add_action(
        self,
        icon,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action
    
    def add_toolbutton(self,toolbutton,actions,icon):
        self.tools.settingsToolsButtons(toolbutton,actions,icon,True)
        # return toolbutton
        self.toolbar.addWidget(toolbutton)

    def initGui(self):
        self.comboCampanias = QComboBox()
        self.comboCampanias.adjustSize()
        self.comboCampanias.addItem('Seleccionar Campanias...',0)
        self.comboCampanias.currentIndexChanged.connect(self.fill_combo_exp)
        self.comboCampanias.setEnabled(False)
        self.comboExplotacion = QComboBox()
        self.comboExplotacion.adjustSize()
        self.comboExplotacion.addItem('Seleccionar Explotacion...',0)
        self.comboExplotacion.setEnabled(False)
        # self.comboExplotacion.resize(30,200)
        self.comboExplotacion.setMinimumWidth(300)
        
        label_title_app = QLabel('Analíticas de Mapeo | Mapeo Integral | aGrae')
        label_title_app.setStyleSheet("QLabel { background-color : red; color : white; font-weight: bold }")
        self.toolbar.addWidget(label_title_app)
        self.add_action(aGraeGUI().getIcon('login'),'Iniciar Sesion',self.login,add_to_menu=True,add_to_toolbar=True)
        
        self.toolbar.addWidget(self.comboCampanias)
        self.toolbar.addWidget(self.comboExplotacion)
        
        self.business_inteligence_tool = QToolButton()
        self.business_inteligence_tool.setToolTip('Analíticas de Mapeo | aGrae')
        self.bi_actions.append(self.tools.getAction(parent=self,text='Gestionar Usuarios',callback=lambda: aGraeDialogs().usersDialog(self.sessionToken,self.comboExplotacion.currentData(),self.comboExplotacion.currentText())))
        self.bi_actions.append(self.tools.getAction(parent=self,text='Gestionar Almacenamiento',callback=lambda: aGraeDialogs().diskSpaceDialog(self.sessionToken,self.comboCampanias.currentData(),self.comboExplotacion.currentData())))
        self.bi_actions.append(aGraeTools().getAction(parent=self,text='Identificacion',callback=self.activate_identify))
        # self.bi_actions.append(aGraeTools().getAction(parent=self,text='Generar Reportes',callback=self.activate_identify))
        #* GENERAR REPORTES DE FERTILIZACION EN CSV, REPORTES DE ANALITICA EN CSV LOS REPORTES DEBEN SER UN SUBMENU
        self.add_toolbutton(self.business_inteligence_tool,self.bi_actions,aGraeGUI().getIcon('BI'))
        
        self.manager_business_tool = QToolButton()
        self.manager_business_tool.setToolTip('Mapeo de Procesos | aGrae')
        # self.mb_actions.append(self.tools.getAction(parent=self,text='Generar Reporte Excel'))
        # self.mb_actions.append(self.tools.getAction(parent=self,text='Cargar Analisis de Laboratorio'))
        self.mb_actions.append(self.tools.getAction(parent=self,text='Cargar Lotes',callback=lambda: self.load_layer('/app/lotes/','Lotes',self.sessionToken,'lotes')))
        self.mb_actions.append(self.tools.getAction(parent=self,text='Cargar Segmentos',callback=lambda: self.load_layer('/app/segm/','Segmentos',self.sessionToken,'segmentos')))
        self.mb_actions.append(self.tools.getAction(parent=self,text='Cargar Ambientes Productivos',callback=lambda: self.load_layer('/app/amb/','Ambientes',self.sessionToken,'ambientes')))
        self.mb_actions.append(self.tools.getAction(parent=self,text='Cargar Unid. Fertilización',callback=lambda: self.load_layer('/app/uf/','Und. Fertilizacion',self.sessionToken,'ufs')))
        self.mb_actions.append(self.tools.getAction(parent=self,text='Cargar Recintos Parcelarios',callback=lambda: aGraeGISTools().load_wms_toc(self.sessionToken,'Parcelas Catastro','Recintos Parcelarios')))
        self.mb_actions.append(self.tools.getAction(parent=self,text='Cargar Mapa Satelital',callback=lambda: aGraeGISTools().load_wms_toc(self.sessionToken,'PNOA Ortofoto','Ortofoto PNOA')))
        # self.add_action(aGraeGUI().getIcon('BI'),'Cargar Capas',self.run,add_to_menu=True,add_to_toolbar=True)
        self.add_toolbutton(self.manager_business_tool,self.mb_actions,aGraeGUI().getIcon('GN'))


        return 
        

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&aGricultura de Precision | aGrae'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        return

    def login(self):
        if not self.sessionToken:
            aGraeDialogs().loginDialog(self.fill_combo_campanias)
            
            self.comboCampanias.setEnabled(True)
            self.comboExplotacion.setEnabled(True)
    
    def fill_combo_campanias(self,data:dict) -> None:
        self.sessionToken = data
        self.campania_data = self.tools.get_exp_ids(data)
        
        for k,v in self.campania_data.items():
            self.comboCampanias.addItem(v['name'],k)
            # print(k,v)
        
        pass

    def fill_combo_exp(self,index:int) -> None:
        for e in range(1,self.comboExplotacion.count()+1):
            self.comboExplotacion.removeItem(e)

        if index > 0:
            data = self.comboCampanias.currentData()
            for i,e in zip(self.campania_data[str(data)]['idexplotacion'],self.campania_data[str(data)]['name_exp']):
                self.comboExplotacion.addItem(e,i)
        return

    def load_layer(self,endpoint,nombre,token,style):
        if self.sessionToken:
            idcampania = self.comboCampanias.currentData()
            idexplotacion = self.comboExplotacion.currentData()
            QgsProject.instance().addMapLayer(aGraeGISTools().get_layer(endpoint,token,idcampania,idexplotacion,f'{self.comboCampanias.currentText()}-{self.comboExplotacion.currentText()}-{nombre}',style))


    def activate_identify(self):
        active_layer = self.iface.activeLayer()
        if active_layer is None:
            print("No hay capa activa seleccionada.")
            return
        if self.identifyTool is None:
            self.identifyTool = selectTool(active_layer,self.sessionToken) #Create the tool with the active layer.
        #iface.setActiveLayer(active_layer) #set the correct active layer to tool
        self.iface.mapCanvas().setMapTool(self.identifyTool)