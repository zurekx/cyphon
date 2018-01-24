# -*- coding: utf-8 -*-
# Copyright 2017-2018 Dunbar Security Solutions, Inc.
#
# This file is part of Cyphon Engine.
#
# Cyphon Engine is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Cyphon Engine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cyphon Engine. If not, see <http://www.gnu.org/licenses/>.
"""
Customizes admin pages for |Requisitions| and |Parameters|.

==============================  ===============================================
Class                           Description
==============================  ===============================================
:class:`~ParameterAdmin`        Customizes admin pages for |Parameters|.
:class:`~ParameterInlineAdmin`  Customizes inline admin pages for |Parameters|.
:class:`~RequisitionAdmin`      Customize admin pages for |Requisitions|.
==============================  ===============================================

"""

# third party
from django.contrib import admin

# local
from .models import Requisition, Parameter


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    """Customizes admin pages for |Parameters|."""

    pass


class ParameterInlineAdmin(admin.TabularInline):
    """Customizes admin inline tables for |Parameters|."""

    model = Parameter
    show_change_link = True
    extra = 1


@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    """Customizes admin pages for |Requisitions|."""

    inlines = [ParameterInlineAdmin, ]
