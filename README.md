# Mapeo de Procesos - Documentación de la Aplicación

## Descripción General

Mapeo de Procesos es un plugin para QGIS desarrollado para facilitar el análisis y la gestión de datos geoespaciales relacionados con mapeos agrícolas. Esta herramienta, integrada en el entorno QGIS, permite a los usuarios interactuar con datos de mapeo, realizar análisis, generar reportes y gestionar información de usuarios y almacenamiento.

La aplicación se integra con un servicio web (no detallado en el código proporcionado) para la autenticación de usuarios y la gestión de datos.

## Funcionalidades Principales

1.  **Inicio de Sesión:**

    - Permite a los usuarios autenticarse con sus credenciales.
    - Una vez autenticado, el usuario puede acceder a las funcionalidades del plugin.
    - El plugin guarda un token de sesión para mantener la conexión.
    - El nombre de usuario se muestra en la barra de título de QGIS.

2.  **Gestión de Campañas y Explotaciones:**

    - Permite seleccionar una campaña agrícola específica.
    - Permite seleccionar una explotación dentro de la campaña seleccionada.
    - Los datos de campañas y explotaciones se obtienen del servicio web.
    - Los combos de selección se habilitan una vez que el usuario se ha logueado.

3.  **Carga de Capas:**

    - Permite cargar diferentes tipos de capas desde el servicio web:
      - Lotes
      - Segmentos
      - Ambientes Productivos
      - Unidades de Fertilización
    - Permite cargar capas WMS:
      - Recintos Parcelarios (Parcelas Catastro)
      - Mapa Satelital (PNOA Ortofoto)
    - Las capas se cargan en el proyecto QGIS actual.
    - El nombre de la capa cargada incluye la campaña y la explotación seleccionadas.

4.  **Herramientas de Mapeo de Procesos:**

    - **Gestión de Usuarios:** Permite gestionar usuarios asociados a una explotación.
    - **Cargar Lotes Asociados:** Carga la capa de lotes asociados a la explotación.
    - **Gestión de Almacenamiento:** Permite visualizar y gestionar el espacio de almacenamiento.
    - **Identificación:** Permite identificar elementos en la capa activa.
    - **Generar Reportes de Fertilización:** Permite generar reportes de fertilización en formato CSV.

5.  **Identificación de Elementos:**

    - Permite seleccionar una capa activa.
    - Permite identificar elementos en la capa activa.

6.  **Reportes:**
    - Genera reportes de fertilización en formato CSV.

## Requisitos de Instalación

1.  **aiohttp:** Esta librería es necesaria para realizar peticiones HTTP asíncronas al servicio web. Debe instalarse en el entorno de Python de QGIS.

    **Instalación de `aiohttp`:**

    - Abrir la consola de Python de QGIS (Plugins -> Consola de Python).
    - Ejecutar el siguiente comando:

      ```python
      import subprocess
      import sys

      python_executable = sys.executable
      subprocess.check_call([python_executable, "-m", "pip", "install", "aiohttp"])
      ```

      - Si no funciona, probar con:

      ```python
      import subprocess
      import sys

      python_executable = sys.executable
      subprocess.check_call([python_executable, "-m", "pip", "install", "--upgrade", "pip"])
      subprocess.check_call([python_executable, "-m", "pip", "install", "aiohttp"])
      ```

    - Reiniciar QGIS después de la instalación.

## Instalación del Plugin

1.  **Descargar el Plugin:** Descargar el plugin desde el repositorio correspondiente.
2.  **Copiar la Carpeta:** Copiar la carpeta `agrae_mapeo_procesos` en el directorio de plugins de QGIS. La ruta suele ser:
    - Windows: `C:\Users\<Usuario>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`
    - Linux: `/home/<usuario>/.local/share/QGIS/QGIS3/profiles/default/python/plugins`
    - macOS: `/Users/<usuario>/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins`
3.  **Activar el Plugin:** Abrir QGIS y ir a `Complementos -> Administrar e instalar complementos`. Buscar "Analiticas de Mapeo" y activarlo.

## Uso

1.  **Iniciar QGIS.**
2.  **Iniciar Sesión:** Hacer clic en el botón "Iniciar Sesión" en la barra de herramientas del plugin.
3.  **Seleccionar Campaña y Explotación:** Seleccionar la campaña y la explotación deseada en los combos desplegables.
4.  **Cargar Capas:** Utilizar los botones de la barra de herramientas para cargar las capas deseadas.
5.  **Utilizar las Herramientas:** Utilizar las herramientas de Business Intelligence y Mapeo de Procesos para realizar análisis y gestionar datos.
6.  **Identificar Elementos:** Seleccionar la capa activa y activar la herramienta de identificación.
7.  **Generar Reportes:** Utilizar la herramienta para generar reportes de fertilización en formato CSV.

## Estructura de Archivos

- `__init__.py`: Archivo principal del plugin. Contiene la lógica principal, la interfaz de usuario y la conexión con el servicio web.
- `db.py`: Módulo para la gestión de la conexión a la base de datos (no se detalla en el código proporcionado).
- `dialogs.py`: Módulo para la creación de diálogos (login, gestión de usuarios, etc.).
- `gui.py`: Módulo para la gestión de la interfaz gráfica.
- `core/`:
  - `tools.py`: Módulo con herramientas generales.
  - `identify.py`: Módulo para la herramienta de identificación.
  - `aGraeGISTools.py`: Módulo con herramientas GIS.

## Consideraciones

- El código proporcionado es una parte del plugin y no incluye la totalidad de la lógica de la aplicación.
- La interacción con el servicio web no está detallada en el código, pero se asume que existe y que se utiliza para la autenticación y la gestión de datos.
- La gestión de errores y excepciones no está completamente implementada en el código proporcionado.
- La documentación de las clases y métodos no está completa.

## Contacto

Para cualquier duda o consulta, contactar con el desarrollador.
