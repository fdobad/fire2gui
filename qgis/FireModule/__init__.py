# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FireClass
                                 A QGIS plugin
 FireDescription
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-01-14
        copyright            : (C) 2023 by fdo bad vel
        email                : fernandobadilla@gmail.com
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
    """Load FireClass class from file FireClass.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .FireModule import FireClass
    return FireClass(iface)