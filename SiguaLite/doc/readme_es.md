# Sigua Lite
Plugin para añadir cartografía de los edificios de la Universidad de Alicante

Captura de pantalla:
![alt text](  https://github.com/josemamira/SiguaLitePlugin/raw/master/SiguaLite/doc/screenshot.png "Captura")
### Descripción
Aplicación standalone para ver e imprimir los edificios y plantas de la Universidad de Alicante  utilizando simbología avanzada. Se trata de una aplicación más de SIGUA [www.sigua.ua.es]

### Version
1.0

### Autor
José Manuel Mira Martínez

### Programación
Se trata de un proyecto programado en Python que utiliza
- Librería PyQgis
- Librería PyQt
- El interfaz de usuario (UI) ha sido diseñado con QtDesigner

### Especificaciones
-	Multiplataforma
-	Permite conectarse a la geodatabase de Sigua (en la versión Lite sólo a una versión reducida en SpatialLite
-	Edición de leyenda automática por actividades utilizando el esquema Sigua
-	Edición de leyenda automática por organización (departamentos o unidades administrativas)
-	Optimización de leyenda utilizando gama de colores basados en ColorBrewer
-	Controles para acercarse, alejarse, desplazarse y zoom a extensión
-	Etiquetado automático de estancias por código
-	Etiquetado automático de estancias por denominación
-   Impresión con salida en PDF y PNG
-	Selección automática de la orientación del papel
-	Impresión con centrado en edificio
-	Impresión con metadatos
-	Mapa con título, autor, organismo, logotipo, escala numérica y gráfica


### Requerimientos
Necesita tener instalado Qgis 2.18 o superior. Se ha testeado con otras versiones de Qgis (2.14) .

### Funcionamiento
Aplicación extremadamente sencilla de utilizar. Seguir estos pasos:
1. Seleccionar un edificio del combo desplegable y oprimir el botón "Cargar edificio"
2. Cambia la simbolización por usos o por organización
3. Opcionalmente selecciona un etiquetado de estancias por código Sigua o por denominación
4. Crear un PDF y un PNG del edificio. Previamente deberás indicar donde se guardarán los archivos de impresión
