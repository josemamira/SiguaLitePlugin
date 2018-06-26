# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SiguaLite
                                 A QGIS plugin
 Tool for view floor of university of Alicante building
                             -------------------
        begin                : 2018-06-26
        copyright            : (C) 2018 by Jose Manuel Mira Martinez
        email                : josema.mira@ua.es
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SiguaLite class from file SiguaLite.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .sigua_lite import SiguaLite
    return SiguaLite(iface)
