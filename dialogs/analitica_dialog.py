from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QGridLayout, QPushButton, QFileDialog, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')


class AnaliticaDialog(QDialog):
    canvas: FigureCanvas

    def __init__(self, dataLote: dict, dataAnalitica: list[dict], cif: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Analítica de Suelos | Mapeo Integral | Usuario: {cif}")
        self.dataLote: dict = dataLote
        self.dataAnalitica: list[dict] = dataAnalitica
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()
        # Create the bar plot
        self.figure = plt.figure(figsize=(10, 6))  # Adjust figure size as needed
        self.canvas = FigureCanvas(self.figure)

        mainLayout.addWidget(self.canvas)

        # Create the export button
        self.export_button = QPushButton("Exportar como PNG")
        self.export_button.clicked.connect(self.export_as_png)
        mainLayout.addWidget(self.export_button)

        self.setLayout(mainLayout)
        self.plot_data()

    def plot_data(self):
        ax = self.figure.add_subplot()
        # Data
        segmentos = [item['segmento'] for item in self.dataAnalitica]
        n_tipos = [item['n_tipo'] for item in self.dataAnalitica]
        p_tipos = [item['p_tipo'] for item in self.dataAnalitica]
        k_tipos = [item['k_tipo'] for item in self.dataAnalitica]
        carb_tipos = [item['carb_tipo'] for item in self.dataAnalitica]
        n_values = [item['n_value'] for item in self.dataAnalitica]
        p_values = [item['p_value'] for item in self.dataAnalitica]
        k_values = [item['k_value'] for item in self.dataAnalitica]
        carb_values = [item['carb_value'] for item in self.dataAnalitica]

        # New list of levels.
        levels = ["", "Muy bajo", "Bajo", "Medio", "Alto", "Muy Alto"]
        level_map = {
            "": 0,
            "Muy bajo": 1,
            "Muy Bajo": 1,
            "Bajo": 2,
            "Medio": 3,
            "Normal": 3,
            "Alto": 4,
            "Muy Alto": 5,
        }

        # New list of colors for levels
        level_colors = {
            "": "#FFFFFF",  # White
            "Muy bajo": "#FF6666",  # Red
            "Muy Bajo": "#FF6666",
            "Bajo": "#FFAB66",  # Orange
            "Medio": "#5EE25A",  # Green
            "Normal": "#5EE25A",
            "Alto": "#5AB8E2",  # Blue
            "Muy Alto": "#995AE2",  # Purple
        }

        # Width of bars
        width = 0.15
        group_width = 0.8

        # Define consistent positions for each category
        category_positions = {
            'N': -1.5 * width,
            'P': -0.5 * width,
            'K': 0.5 * width,
            'Carb': 1.5 * width
        }
        text_y_position = -0.3

        # Plot
        x = range(len(segmentos))
        for i, segmento in enumerate(segmentos):
            # Map values to levels.
            n_pos = level_map.get(n_tipos[i], 0)
            p_pos = level_map.get(p_tipos[i], 0)
            k_pos = level_map.get(k_tipos[i], 0)
            carb_pos = level_map.get(carb_tipos[i], 0)
            # Plot N
            if n_pos > 0:
                n_bar = ax.bar(i * group_width + category_positions['N'], n_pos, width,
                               color=level_colors[n_tipos[i]])
                ax.text(i * group_width + category_positions['N'], n_pos + 0.1, f"{(n_values[i]*100):.2f}%",
                        ha='center', va='bottom', fontsize=8, color='black')  # Change text position
                ax.text(i * group_width + category_positions['N'], text_y_position, "N", ha='center', va='top',
                        fontsize=10, color='black')
            # Plot P
            if p_pos > 0:
                ax.bar(i * group_width + category_positions['P'], p_pos, width,
                       color=level_colors[p_tipos[i]])
                ax.text(i * group_width + category_positions['P'], p_pos + 0.1, f"{p_values[i]:.2f} ppm",
                        ha='center', va='bottom', fontsize=8, color='black')  # Change text position
                ax.text(i * group_width + category_positions['P'], text_y_position, "P", ha='center', va='top',
                        fontsize=10, color='black')

            # Plot K
            if k_pos > 0:
                ax.bar(i * group_width + category_positions['K'], k_pos, width,
                       color=level_colors[k_tipos[i]])
                ax.text(i * group_width + category_positions['K'], k_pos + 0.1, f"{k_values[i]:.2f} ppm",
                        ha='center', va='bottom', fontsize=8, color='black')  # Change text position
                ax.text(i * group_width + category_positions['K'], text_y_position, "K", ha='center', va='top',
                        fontsize=10, color='black')

            # Plot Carb
            if carb_pos > 0:
                ax.bar(i * group_width + category_positions['Carb'], carb_pos, width,
                       color=level_colors[carb_tipos[i]])
                ax.text(i * group_width + category_positions['Carb'], carb_pos + 0.1, f"{carb_values[i]:.2f} ppm",
                        ha='center', va='bottom', fontsize=8, color='black')  # Change text position
                ax.text(i * group_width + category_positions['Carb'], text_y_position, "Carb", ha='center', va='top',
                        fontsize=10, color='black')

        # Customize plot
        segment_labels = [f'Segmento {seg}' for seg in segmentos]
        ax.set_xticks([i * group_width for i in x])
        ax.set_xticklabels(segment_labels)
        ax.tick_params(axis='x', which='major', pad=10)

        main_label = 'Niveles de Nitrogeno, Fosforo, Potasio y Carbonatos por Segmento.'
        sub_label = r"$\it{Nitrogeno\ mineral.\ Metodo\ iones\ selectivos\ NO3\ NH4\ Fosforo,\ Potasio,\ Calcio.\ Extraccion\ Melich-III}$"
        ax.set_xlabel(f'{main_label}\n{sub_label}')
        
        ax.set_ylabel('Nivel')
        ax.set_title(
            f'Lote:{self.dataLote["name"]}    Cultivo: {self.dataLote["cultivo"]}    Area: {self.dataLote["area_ha"]} Ha'.upper())
        # Customize the level list.
        ax.set_yticks(range(len(levels)))
        ax.set_yticklabels(levels)
        ax.set_ylim(-0.5, 6)

        plt.tight_layout()

        plt.draw()

    def export_as_png(self):
        """
        Saves the current plot as a PNG image file.
        """
        # Get a file path to save the image.
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar imagen", "", "PNG (*.png)")

        if file_path:
            # If the user selected a file path, save the plot.
            try:
                # Save the plot to the selected file path.
                self.canvas.figure.savefig(file_path, bbox_inches='tight')
                QMessageBox.information(self, "Guardar Imagen", f"La imagen fue guardada en: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al guardar la imagen: {e}")

    def closeEvent(self, event):
        """
        Override the QDialog closeEvent to close the Matplotlib figure.
        """
        plt.close(self.figure)  # Close the Matplotlib figure
        super().closeEvent(event)  # Call the parent class closeEvent

