# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SiguaLite
                                 A QGIS plugin
 Tool for load building floor from University of Alicante
                              -------------------
        begin                : 2018-06-21
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Jose Manuel Mira Martinez
        email                : josema.mira@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from PyQt4.QtXml import QDomDocument
import colorbrewer
import time
from PyQt4.QtSql import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from sigua_lite_dialog import SiguaLiteDialog
import os.path
import sys

class SiguaLite:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SiguaLite_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Sigua Lite')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SiguaLite')
        self.toolbar.setObjectName(u'SiguaLite')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SiguaLite', message)


    def add_action(
        self,
        icon_path,
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

        # Create the dialog (after translation) and keep reference
        self.dlg = SiguaLiteDialog()

        icon = QIcon(icon_path)
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

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SiguaLite/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Edificios Universidad de Alicante'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Sigua Lite'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    # borrar todas las capas
    def deleteAllLayers(self):
        QgsMapLayerRegistry.instance().removeAllMapLayers()
        canvas = iface.mapCanvas()
        canvas.refresh()

    # get file path. Thanks Nathan W (https://gis.stackexchange.com/questions/130027/getting-a-plugin-path-using-python-in-qgis)
    def resolve(self,name, basepath=None):
        if not basepath:
            basepath = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(basepath, name)


    def run(self):
        """Run method that performs all the real work"""

        canvas = iface.mapCanvas()
        canvas.refresh()

        db = QSqlDatabase.addDatabase('QSQLITE')
        pathDB = self.resolve('sigua.sqlite')
        #db.setDatabaseName('/home/jose/.qgis2/python/plugins/SiguaPlugin/sigua.sqlite')
        db.setDatabaseName(pathDB)
        sql="select cod_zona || cod_edificio ||'PB'||' - ' || txt_edificio ||' (PLANTA BAJA)' as zzee from edificios WHERE pb=1  UNION select cod_zona || cod_edificio ||'P1'||' - ' || txt_edificio ||' (PLANTA 1)'  as zzee from edificios WHERE p1=1 UNION select cod_zona || cod_edificio ||'P2'||' - ' || txt_edificio ||' (PLANTA 2)' as zzee from edificios WHERE p2=1  UNION select cod_zona || cod_edificio ||'P3'||' - ' || txt_edificio ||' (PLANTA 3)' as zzee from edificios WHERE p3=1 UNION select cod_zona || cod_edificio ||'P4'||' - ' || txt_edificio ||' (PLANTA 4)' as zzee from edificios WHERE p4=1  UNION select cod_zona || cod_edificio ||'PS'||' - ' || txt_edificio ||' (PLANTA SOTANO)' as zzee from edificios WHERE ps=1 ORDER BY 1"


        if (db.open()==False):
            QMessageBox.critical(None, "Database Error", db.lastError().text())

        ok = db.open()
        if ok:
            sql = "select cod_zona || cod_edificio ||'PB'||' - ' || txt_edificio ||' (PLANTA BAJA)' as zzee from edificios WHERE pb=1  UNION select cod_zona || cod_edificio ||'P1'||' - ' || txt_edificio ||' (PLANTA 1)'  as zzee from edificios WHERE p1=1 UNION select cod_zona || cod_edificio ||'P2'||' - ' || txt_edificio ||' (PLANTA 2)' as zzee from edificios WHERE p2=1  UNION select cod_zona || cod_edificio ||'P3'||' - ' || txt_edificio ||' (PLANTA 3)' as zzee from edificios WHERE p3=1 UNION select cod_zona || cod_edificio ||'P4'||' - ' || txt_edificio ||' (PLANTA 4)' as zzee from edificios WHERE p4=1  UNION select cod_zona || cod_edificio ||'PS'||' - ' || txt_edificio ||' (PLANTA SOTANO)' as zzee from edificios WHERE ps=1 ORDER BY 1"
            query = db.exec_(sql)
            while query.next():
                zzeetxt = unicode(query.value(0))
                self.dlg.comboBoxEdificio.addItem(zzeetxt)

            db.close()
            self.dlg.show()
            # Acciones para botones
            self.dlg.aceptarButton.clicked.connect(self.cargaEdificio)
            #self.dlg.cerrarButton.clicked.connect(self.dlg.close)
            self.dlg.dlgFileButton.clicked.connect(self.OpenBrowse)
            self.dlg.temaButton.setEnabled(False)
            self.dlg.tema2Button.setEnabled(False)
            self.dlg.labelButton.setEnabled(False)
            self.dlg.denoButton.setEnabled(False)
            self.dlg.mapaPlantillaButton.setEnabled(False)
            self.dlg.dlgFileButton.setEnabled(False)
            self.dlg.lineEditDirectory.setEnabled(False)


    # función para cargar el edificio
    def cargaEdificio(self):
        # borra todas las capas
        self.deleteAllLayers()
        self.borrarRegistro()
        iface.mapCanvas().refresh()

        # asignamos variables a las selecciones de los combos
        varZZEEPP = self.dlg.comboBoxEdificio.currentText()[:6]
        varPlanta = varZZEEPP[4:6]
        planta = ("sig"+ varPlanta).lower()
        print varPlanta
        varTocZZEEPP = 'E' + varZZEEPP

        # SpatiaLite
        uri = QgsDataSourceURI()
        uri.setDatabase(self.resolve('sigua.sqlite'))
        schema = ''
        sql="(SELECT e.gid, e.codigo,e.coddpto,d.txt_dpto_sigua,e.actividad,a.txt_actividad,a.activresum,e.denominaci,e.observacio,e.GEOMETRY FROM "+planta+" e, actividades a, departamentossigua d WHERE e.actividad = a.codactividad AND e.coddpto = d.cod_dpto_sigua AND e.codigo LIKE '"+varZZEEPP+"%')"
        geom_column = 'geometry'
        uri.setDataSource(schema, sql, geom_column)
        vLayer = QgsVectorLayer(uri.uri(), varTocZZEEPP, "spatialite")

        # Set metadata
        vLayer.setShortName(varTocZZEEPP)
        vLayer.setTitle(u"Planta de edificio " + varTocZZEEPP )
        vLayer.setAbstract(u"Edificio procedente del Sistema de Información Geográfica de la Universidad de Alicante (SIGUA)")

        # Add layer to TOC
        QgsMapLayerRegistry.instance().addMapLayer(vLayer)

        # show layer to QgsMapLayerRegistry
        QgsMapLayerRegistry.instance().addMapLayer(vLayer) # añade capa al registro

        c1 = QgsMapCanvasLayer(vLayer)
        layers = [c1]
        iface.mapCanvas().setLayerSet(layers)
        iface.mapCanvas().zoomToFullExtent()
        iface.mapCanvas().show()

        # Zoom a capa
        canvas = iface.mapCanvas()
        extent = vLayer.extent()
        canvas.setExtent(extent)
        canvas.refresh()

        #activar botones

        self.dlg.temaButton.setEnabled(True)
        self.dlg.temaButton.clicked.connect(self.tematico)
        self.dlg.tema2Button.setEnabled(True)
        self.dlg.tema2Button.clicked.connect(self.tematico2)
        self.dlg.labelButton.setEnabled(True)
        self.dlg.labelButton.clicked.connect(self.labelCodigo)
        self.dlg.denoButton.setEnabled(True)
        self.dlg.denoButton.clicked.connect(self.labelDeno)
        self.dlg.mapaPlantillaButton.setEnabled(True)
        self.dlg.mapaPlantillaButton.clicked.connect(self.mapaPlantillaPdf)
        self.dlg.dlgFileButton.setEnabled(True)
        self.dlg.lineEditDirectory.setEnabled(True)


    # crea un mapa temático de usos
    def tematico(self):
        layer = iface.activeLayer()
        usos = {
            u"Administración": ("#b3cde3", u"Administración"),
            "Despacho": ("#fbb4ae", "Despacho"),
            "Docencia": ("#ccebc5", "Docencia"),
            "Laboratorio": ("#decbe4", "Laboratorio"),
            "Salas": ("#fed9a6", "Salas"),
            "Muros": ("#808080", "Muros"),
            "": ("white", "Resto")}
        categorias = []
        for estancia, (color, label) in usos.items():
            sym = QgsSymbolV2.defaultSymbol(layer.geometryType())
            sym.setColor(QColor(color))
            category = QgsRendererCategoryV2(estancia, sym, label)
            categorias.append(category)

            field = "activresum"
            index = layer.fieldNameIndex("activresum")
            # comprueba que existe el campo activresum
            if (index == -1):
                QMessageBox.critical(None, "Field error", "No existe el campo activresum. Seleccione la capa adecuada")
                break

            renderer = QgsCategorizedSymbolRendererV2(field, categorias)
            layer.setRendererV2(renderer)
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            layer.triggerRepaint()
            layer.setName(layer.name()[:7] + u' (uso)')
            # actualizar metadatos
            layer.setTitle(u"Planta de edificio " + layer.name() + u' (uso)')
            layer.setAbstract(u"Edificio procedente del Sistema de Informacion Geografica de la Universidad de Alicante (SIGUA)")


    # crea un temático de unidades/dptos
    def tematico2(self):
        layer = iface.activeLayer()
        # array de dptos
        idx = layer.fieldNameIndex('txt_dpto_sigua')
        dptosArr = layer.uniqueValues( idx )
        total = len(dptosArr)
        if total < 3:
            coloresArr = colorbrewer.Set3[3]
        elif total <= 12:
            coloresArr = colorbrewer.Set3[total]
        else:
            exceso = total - 12
            if exceso < 3:
                coloresArr = colorbrewer.Set3[12] + colorbrewer.Paired[3]
            else:
                coloresArr = colorbrewer.Set3[12] + colorbrewer.Paired[exceso]

        print coloresArr
        dptoDic = {}
        for i in range(0, len(dptosArr)):
            if  dptosArr[i] == u"GESTIÓN DE ESPACIOS":
                dptoDic[dptosArr[i]] = ("white", dptosArr[i])
            else:
                dptoDic[dptosArr[i]] = (coloresArr[i], dptosArr[i])

        #print dptoDic
        categories = []
        for estancia, (color, label) in dptoDic.items():
            sym = QgsSymbolV2.defaultSymbol(layer.geometryType())
            sym.setColor(QColor(color))
            category = QgsRendererCategoryV2(estancia, sym, label)
            categories.append(category)

        field = "txt_dpto_sigua"
        renderer = QgsCategorizedSymbolRendererV2(field, categories)
        layer.setRendererV2(renderer)
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        layer.triggerRepaint()
        layer.setName(layer.name()[:7] + u" (organización)" )
        # actualizar metadatos
        layer.setTitle(u"Planta de edificio " + layer.name() + u" (organización)")
        layer.setAbstract(u"Edificio procedente del Sistema de Información Geográfica de la Universidad de Alicante (SIGUA)")

    def labelDeno(self):
        layer = iface.activeLayer()
        palyr = QgsPalLayerSettings()
        palyr.readFromLayer(layer)
        palyr.enabled = True
        palyr.bufferDraw = True
        palyr.bufferColor = QColor("white")
        palyr.bufferSize = 1
        palyr.scaleVisibility = True
        palyr.scaleMax = 2000
        palyr.isExpression = False
        palyr.fieldName = 'denominaci'
        palyr.size = 15
        palyr.textColor = QColor("black")
        palyr.drawLabels = True
        palyr.wrapChar = ' '
        palyr.placement = QgsPalLayerSettings.OverPoint
        palyr.setDataDefinedProperty(QgsPalLayerSettings.Size, True, True, '7', '')
        palyr.writeToLayer(layer)
        iface.mapCanvas().refresh()


    def labelCodigo(self):
        layer = iface.activeLayer()
        palyr = QgsPalLayerSettings()
        palyr.readFromLayer(layer)
        palyr.enabled = True
        palyr.bufferDraw = True
        palyr.bufferColor = QColor("white")
        palyr.bufferSize = 1
        palyr.scaleVisibility = True
        palyr.scaleMax = 2000
        palyr.isExpression = True
        palyr.fieldName =  'if( "codigo" NOT LIKE \'%000\', right(  "codigo" ,3),"")'
        palyr.size = 15
        palyr.textColor = QColor("black")
        palyr.drawLabels = True
        palyr.fitInPolygonOnly = True  #solo dibuja las label que caben dentro del poligono
        palyr.placement = QgsPalLayerSettings.OverPoint
        palyr.setDataDefinedProperty(QgsPalLayerSettings.Size, True, True, '7', '')
        palyr.writeToLayer(layer)
        iface.mapCanvas().refresh()

    def OpenBrowse(self):
        from os.path import expanduser
        self.settings = QSettings()
        home = expanduser("~") # obtiene el /home o el c:\User
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(None, self.tr('Save to directory'), home,options)
        if directory:
            #QMessageBox.information(self.iface.mainWindow(), "Resultado", directory)
            self.dlg.lineEditDirectory.setText(self.settings.value('rootDir', directory))
        else:
            QMessageBox.information(self.iface.mainWindow(), "Resultado", "Error. NO hay directorio")

    def borrarRegistro(self):
        registryLayers = QgsMapLayerRegistry.instance().mapLayers().keys()
        legendLayers = [ layer.id() for layer in iface.legendInterface().layers() ]
        QgsMapLayerRegistry.instance().removeMapLayers( registryLayers )
        QgsMapLayerRegistry.instance().removeMapLayers( legendLayers )

    def mapaPlantillaPdf2(self):
        directory = self.dlg.lineEditDirectory.text()
        if not directory:
            QMessageBox.information(self.iface.mainWindow(), "Mensaje", u"Indica el directorio para guardar los archivos")
        else:
            registry = QgsMapLayerRegistry.instance()

            # Add layer to map render
            myMapRenderer = QgsMapRenderer()
            #myMapRenderer.setLayerSet(layerName)
            layer = iface.activeLayer()
            lst = [layer.id()]
            myMapRenderer.setLayerSet(lst)
            myMapRenderer.setProjectionsEnabled(False)

            # Load template
            layer = iface.activeLayer()
            canvas = iface.mapCanvas()
            canvas.refresh()
            extent = layer.extent()
            #canvas = QgsMapCanvas()
            ms = canvas.mapSettings()
            myComposition = QgsComposition(ms)

            # uso plantilla
            import platform
            if (extent.width() > extent.height()):
                tipo = 'h'
                if platform.system() == 'Linux':
                    myFile = os.path.join(os.path.dirname(__file__), 'template_h.qpt')
                if platform.system() == 'Windows':
                    myFile = os.path.join(os.path.dirname(__file__), 'template_hw.qpt')

            else:
                # plantilla vertical
                tipo = 'v'
                if platform.system() == 'Linux':
                    myFile = os.path.join(os.path.dirname(__file__), 'template_v.qpt')
                if platform.system() == 'Windows':
                    myFile = os.path.join(os.path.dirname(__file__), 'template_vw.qpt')
            myTemplateFile = file(myFile, 'rt')
            myTemplateContent = myTemplateFile.read()
            myTemplateFile.close()
            myDocument = QDomDocument()
            myDocument.setContent(myTemplateContent)
            myComposition.loadFromTemplate(myDocument)

            # Sustituir textos
            substitution_map = {'TITULO': u'TEMÁTICO','EDIFICIO':self.dlg.comboBoxEdificio.currentText(),'FECHA': time.strftime("%d/%m/%Y") ,'AUTOR': u'José Manuel Mira','ORGANISMO': 'Universidad de Alicante'}
            myComposition.loadFromTemplate(myDocument, substitution_map)

            # Zoom a capa
            myMap = myComposition.getComposerMapById(0)
            myExtent = iface.activeLayer().extent()
            myMap.setNewExtent(myExtent)

            # Save image
            salidaPNG = os.path.join(directory, "mapa_" + layer.name() + "_" + time.strftime("%Y%m%d%H%M%S") + ".png")
            myImage = myComposition.printPageAsRaster(0)
            myImage.save(salidaPNG)

            # export PDF
            salidaPDF = os.path.join(directory, "mapa_" + layer.name() + "_" + time.strftime("%Y%m%d%H%M%S") + ".pdf")
            myComposition.exportAsPDF(salidaPDF)

            QMessageBox.information(self.iface.mainWindow(), "Resultado", "Los mapas, " + salidaPNG + " y "+ salidaPDF+ " han sido creados exitosamente.")


    # Función para generar un mapa a partir de plantillas
    def mapaPlantillaPdf(self):
        if QgsMapLayerRegistry.instance().count() == 0:
            # detiene el script si el registro está vacio
            return None


        # definir directorio para guardar pdf y png
        directory = self.dlg.lineEditDirectory.text()
        if not directory:
            QMessageBox.critical(QWidget(), "ERROR", u"Indica el directorio para guardar los archivos")
        else:
            registry = QgsMapLayerRegistry.instance()
            layers = QgsMapLayerRegistry.instance().mapLayers()
            for name, layer in layers.iteritems():
                print name, layer.type()

            # Add layer to map render
            myMapRenderer = QgsMapRenderer()
            lst = [layer.id()]
            myMapRenderer.setLayerSet(lst)
            myMapRenderer.setProjectionsEnabled(False)

            iface.mapCanvas().refresh()
            extent = layer.extent()
            ms = iface.mapCanvas().mapSettings()
            myComposition = QgsComposition(ms)

            # uso plantilla
            # NOTA: La referencia a las imágenes SVG en las templates hacen referencia a URL, no a rutas locales relativas o absolutas
            import platform
            if (extent.width() > extent.height()):
                tipo = 'h'
                if platform.system() == 'Linux':
                    myFile = os.path.join(os.path.dirname(__file__), 'templates/template_h.qpt')
                if platform.system() == 'Windows':
                    myFile = os.path.join(os.path.dirname(__file__), 'templates/template_h.qpt')
                if platform.system() == 'Darwin':
                    myFile = os.path.join(os.path.dirname(__file__), 'templates/template_h.qpt')
            else:
                # plantilla vertical
                tipo = 'v'
                if platform.system() == 'Linux':
                    myFile = os.path.join(os.path.dirname(__file__), 'templates/template_v.qpt')
                if platform.system() == 'Windows':
                    myFile = os.path.join(os.path.dirname(__file__), 'templates/template_v.qpt')
                if platform.system() == 'Darwin':
                    myFile = os.path.join(os.path.dirname(__file__), 'templates/template_v.qpt')

            myTemplateFile = file(myFile, 'rt')
            myTemplateContent = myTemplateFile.read()
            myTemplateFile.close()
            myDocument = QDomDocument()
            myDocument.setContent(myTemplateContent)
            myComposition.loadFromTemplate(myDocument)

            # Sustituir textos
            substitution_map = {'TITULO': u'TEMÁTICO','EDIFICIO':self.dlg.comboBoxEdificio.currentText(),'FECHA': time.strftime("%d/%m/%Y") ,'AUTOR': u'José Manuel Mira','ORGANISMO': 'Universidad de Alicante'}
            #self.setAttribute(Qt.WA_DeleteOnClose) #para evitar warnings en time
            myComposition.loadFromTemplate(myDocument, substitution_map)

            # Definir extensión mapa y ajustar composición
            myMap = myComposition.getComposerMapById(0)
            extent = layer.extent()
            print "oldExtent:"
            print extent.xMinimum ()
            print extent.yMinimum ()
            print extent.xMaximum ()
            print extent.yMaximum ()
            rW = extent.width()
            rH = extent.height()
            print "rW: " + str(rW)
            print "rH: " + str(rH)

            if (tipo == 'v'):
                # recalcular extent
                print "es vertical"
                pH = 255 #alto en mm del recuadro del mapa
                pW =(rW*pH)/rH
                print "pW es: " + str(pW)
                # caso para edificios verticales muy largos (ej: derecho)
                # 200 son los mm del ancho del recuadro del mapa
                if (pW < 200):
                    # recalcular xMax
                    print "caso 1"
                    xMin = extent.xMinimum()
                    print "xMin es "+ str(xMin)
                    yMin = extent.yMinimum()
                    yMax = extent.yMaximum()
                    dXp = 200 - pW
                    print "dXp es " + str(dXp)
                    newXmax = ((rH*(pW+dXp))/pH) + extent.xMinimum()
                    print "newXmax es " + str(newXmax)
                    # centrar mapa
                    deltaX = (newXmax - extent.xMaximum())/2
                    print "deltaX es: "+ str(deltaX)
                    newExtent = QgsRectangle(xMin - deltaX,yMin,newXmax - deltaX,yMax)
                    #newExtent = QgsRectangle(xMin,yMin,newXmax,yMax)
                    print "newExtent:"
                    print str(newExtent.xMinimum ())
                    print newExtent.yMinimum ()
                    print newExtent.xMaximum ()
                    print newExtent.yMaximum ()
                    myMap.setNewExtent(newExtent)

                # caso para edificios verticales muy anchos (ej: 0005PB, EPS III -0014)
                else:
                    # recalcular Ymin
                    print "caso 2"
                    xMin = extent.xMinimum()
                    xMax = extent.xMaximum()
                    yMax = extent.yMaximum()
                    dYp = 255 -pH
                    newYmin = extent.yMinimum() - ((rW*(pH+dYp))/pW)
                    newExtent = QgsRectangle(xMin,newYmin,xMax,yMax)
                    myMap.setNewExtent(newExtent)

            if (tipo == 'h'):
                print "mapa horizontal"
                myExtent = layer.extent()
                myMap.setNewExtent(myExtent)

                pW=235
                pH = (pW*rH)/rW
                # caso 1: Edificios muy alargados
                if (pH < 203):
                    newRH = (203*rW)/pW
                    xMin = extent.xMinimum()
                    xMax = extent.xMaximum()
                    yMin = extent.yMinimum()
                    yMax = extent.yMaximum()

                    deltaY = (newRH-rH)/2 #(yMax - newYmin)/2
                    print "deltaY: "+ str(deltaY)
                    newExtent = QgsRectangle(xMin, yMin - deltaY, xMax, yMax + deltaY)
                    myMap.setNewExtent(newExtent)

                # caso 2: edificios alargados, pero casi cuadrados.
                else:
                    pH= 203
                    xMin = extent.xMinimum()
                    xMax = extent.xMaximum()
                    yMin = extent.yMinimum()
                    yMax = extent.yMaximum()
                    newRW = (235*rH)/pH
                    newXmax = xMin+newRW
                    print "newXmax: " + str(newXmax)
                    deltaX = (newRW - rW)/2
                    print "deltaX: "+ str(deltaX)
                    newExtent = QgsRectangle(xMin - deltaX, yMin, newXmax - deltaX, yMax)
                    myMap.setNewExtent(newExtent)



            # Save image
            salidaPNG = os.path.join(directory, "mapa_" + layer.name() + "_" + time.strftime("%Y%m%d%H%M%S") + ".png")
            myImage = myComposition.printPageAsRaster(0)
            myImage.save(salidaPNG)

            # export PDF
            salidaPDF = os.path.join(directory, "mapa_" + layer.name() + "_" + time.strftime("%Y%m%d%H%M%S") + ".pdf")
            myComposition.exportAsPDF(salidaPDF)

            QMessageBox.information(QWidget(), "Resultado", "Los mapas, " + salidaPNG + " y "+ salidaPDF+ " han sido creados exitosamente.")
            # Elimina la capa del registro ( y del canvas)
            QgsMapLayerRegistry.instance().removeMapLayers( [layer.id()] )
            # Desactivar botones
            self.dlg.temaButton.setEnabled(False)
            self.dlg.tema2Button.setEnabled(False)
            self.dlg.labelButton.setEnabled(False)
            self.dlg.denoButton.setEnabled(False)
            self.dlg.mapaPlantillaButton.setEnabled(False)
