# Sigua Lite
This Qgis plugin provide functionality to load vector layer building from University of Alicante (UA)

Screenshot:
![alt text](  https://github.com/josemamira/SiguaLitePlugin/raw/master/SiguaLite/doc/screenshot.png "Captura")
### Futher information
SIGUA is an Geographic Information System to management spaces in University of Alicante. Website: SIGUA [www.sigua.ua.es]

### Version
1.0

### Author
José Manuel Mira Martínez

### Especifications
  - Get a legend ready to print. Two options are provider: landuse or departments 
  - Get labels from room code 
  - Print to PDF file using predefined templates with automatic align (horizontal/vertical) 
  - It connect to Sigua geodatabase. Lite version only work with local spatialite database.
  - Automatic label from local names or room id code.
  - Automatic colors from ColorBrewer palette.
  - Load metadata to output map: title, author, icon, scale
  - Based in Qgis templates
  
### Requeriments
Qgis 2.X.
No tested with Qgis 3.X

### Note
For security reason the database (65 mb) only has building geometries. Not personal data included

### How to use
Very easy. Follow this steps:
1. Select building floor from combo form, and clic in "OK" button
2. Change legend using land use or staff organitation.
3. (Optional) Select a type of label: room id or local name denomination. 
4. Print to file in PDF and PNG format.

