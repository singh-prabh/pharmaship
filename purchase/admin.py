# -*- coding: utf-8; -*-
#
# (c) 2013 Association DSM, http://devmaretique.com
#
# This file is part of Pharmaship.
#
# Pharmaship is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# any later version.
#
# Pharmaship is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pharmaship.  If not, see <http://www.gnu.org/licenses/>.
#
# ======================================================================
# Filename:    purchase/admin.py
# Description: Admin view configuration.
# ======================================================================

__author__ = "Matthieu Morin"
__copyright__ = "Copyright 2013, Association DSM"
__license__ = "GPL"
__version__ = "0.1"

import models
from django.contrib import admin

class RequisitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'reference', 'port_of_delivery', 'requested_date', 'item_type')
    ordering = ('date_of_creation',)
    

    class Meta:
        ordering = ('date_of_creation', )


admin.site.register(models.Requisition, RequisitionAdmin)
admin.site.register(models.Item)