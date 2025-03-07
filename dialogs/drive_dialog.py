import asyncio
import os
import shutil
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QGridLayout, QWidget
from PyQt5.QtCore import Qt , QThread, pyqtSignal

from ..core.tools import aGraeGISTools

class DiskUsageThread(QThread):
    """
    Thread to calculate disk usage and layer sizes asynchronously.
    """
    diskUsageCalculated = pyqtSignal(float, float, float)

    def __init__(self, token, idcampania, idexplotacion):
        super().__init__()
        self.token = token
        self.idcampania = idcampania
        self.idexplotacion = idexplotacion

    def run(self):
        endpoints = ['/app/lotes/', '/app/segm/', '/app/amb/', '/app/uf/']

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        layers_size = loop.run_until_complete(asyncio.gather(
            *[aGraeGISTools().get_layer_app_async(endpoint, {'idcampania': self.idcampania,
                                                            'idexplotacion': self.idexplotacion},
                                                 self.token) for endpoint in endpoints]))

        loop.close()

        layers_size_gb = 0
        for layer in layers_size:
            if layer:
                layers_size_gb += self.get_vector_layer_disk_size(layer)

        #total space is set to 1
        total_gb = 1.0
        # Calculate used and free space within the 1 GB limit
        used_gb = min(layers_size_gb / (1024.0 ** 3),total_gb)
        free_gb = total_gb-used_gb

        self.diskUsageCalculated.emit(total_gb, used_gb, free_gb)

    def get_vector_layer_disk_size(self, layer) -> float:
        file_path = layer.dataProvider().dataSourceUri()
        # return os.path.getsize(file_path) / (1024.0 ** 2) if file_path else 0.0
        return os.path.getsize(file_path) if file_path else 0.0


class DriveDialog(QDialog):
    def __init__(self, token:dict, idcampania:int,idexplotacion:int, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Espacio en Disco | Mapeo Integral | Usuario: {token['nif']}")
        self.token = token
        self.idcampania=idcampania
        self.idexplotacion=idexplotacion
        self.setFixedSize(350, 150)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        grid_layout = QGridLayout()

        # Labels
        self.total_label = QLabel(f"Total: 1.00 GB")
        self.used_label = QLabel(f"Usado: 0.00 GB")
        self.free_label = QLabel(f"Disponible: 0.00 GB")

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat(f"0.00%")
        # self.progress_bar.setOrientation(Qt.Vertical)
        # self.progress_bar.setTextVisible(True)
        # self.progress_bar.setTextDirection(QProgressBar.BottomToTop) 
        # self.progress_bar.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        # Progress bar

        # Add widgets to layout
        grid_layout.addWidget(self.total_label, 0, 0)
        grid_layout.addWidget(self.used_label, 1, 0)
        grid_layout.addWidget(self.free_label, 2, 0)
        layout.addLayout(grid_layout)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)
        self.calculate_disk_usage()


    def calculate_disk_usage(self):
        """
        Starts the disk usage calculation in a separate thread.
        """
        self.thread = DiskUsageThread(self.token, self.idcampania, self.idexplotacion)
        self.thread.diskUsageCalculated.connect(self.update_disk_usage_info)
        self.thread.start()
    def update_disk_usage_info(self, total_gb, used_gb, free_gb):
        """
        Updates the UI with the disk usage information.
        """

        self.total_gb = total_gb
        self.used_gb = used_gb
        self.free_gb = free_gb

        self.used_label.setText(f"Usado: {self.used_gb:.2f} GB")
        self.free_label.setText(f"Disponible: {self.free_gb:.2f} GB")


        percentage_used = (self.used_gb / self.total_gb) * 100 if self.total_gb > 0 else 0
        self.progress_bar.setValue(int(percentage_used))
        self.progress_bar.setFormat(f"{percentage_used:.1f}%")

    def get_vector_layer_disk_size(self, layer) -> float:
        file_path = layer.dataProvider().dataSourceUri()
        return os.path.getsize(file_path) / (1024.0 ** 3) if file_path else 0.0