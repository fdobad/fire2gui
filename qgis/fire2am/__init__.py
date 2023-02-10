# -*- coding: utf-8 -*-
"""
/***************************************************************************
 fire2amClass
                                 A QGIS plugin
 Simulate a forest fires under different weather and fire model scenarios
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-02-07
        copyright            : (C) 2023 by fdobadvel (gui) & fire2a team
        email                : fire2a@fire2a.com
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
    """Load fire2amClass class from file fire2amClass.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .fire2am import fire2amClass
    return fire2amClass(iface)
