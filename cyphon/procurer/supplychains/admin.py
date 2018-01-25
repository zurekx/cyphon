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
Customizes admin pages for |SupplyChains|, |SupplyLinks|, and |FieldCouplings|.

==================================  =========================================
Class                               Description
==================================  =========================================
:class:`~FieldCouplingAdmin`        Creates admin pages for |FieldCouplings|.
:class:`~FieldCouplingInlineAdmin`  Inline admin pages for |FieldCouplings|.
:class:`~SupplyChainAdmin`          Creates admin pages for |SupplyChains|.
:class:`~SupplyLinkAdmin`           Creates admin pages for |SupplyLinks|.
:class:`~SupplyLinkInlineAdmin`     Inline admin pages for |SupplyLinks|.
==================================  =========================================

"""

# third party
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

# local
from cyphon.admin import EditLinkMixin
from .models import FieldCoupling, SupplyChain, SupplyLink


@admin.register(FieldCoupling)
class FieldCouplingAdmin(admin.ModelAdmin):
    """Customizes admin pages for FieldCouplings."""

    list_display = [
        'id',
        'supply_link',
        'parameter',
        'field_name',
    ]
    list_display_links = ['id', 'supply_link']
    fields = [
        'parameter',
        'field_name',
    ]


class FieldCouplingInlineAdmin(admin.TabularInline):
    """Customizes admin inline tables for FieldCouplings."""

    model = FieldCoupling
    show_change_link = True
    extra = 1


@admin.register(SupplyLink)
class SupplyLinkAdmin(admin.ModelAdmin):
    """Customizes admin pages for SupplyLinks."""

    inlines = [FieldCouplingInlineAdmin, ]
    list_display = [
        'id',
        'name',
        'supply_chain',
        'requisition',
        'position',
        'wait_time',
        'time_unit',
    ]
    list_display_links = ['id', 'name', ]
    fieldsets = (
        (None, {
            'description': _(''),
            'fields': (
                'name',
                'requisition',
                'supply_chain',
                'position',
            )
        }),
        (_('Wait Time'), {
            'description': _(''),
            'fields': (
                ('wait_time', 'time_unit', ),
            )
        }),
    )
    save_as = True


class SupplyLinkInlineAdmin(admin.TabularInline, EditLinkMixin):
    """Customizes admin inline tables for FieldCouplings."""

    model = SupplyLink
    readonly_fields = ('edit_link', )
    show_change_link = True
    extra = 1


@admin.register(SupplyChain)
class SupplyChainAdmin(admin.ModelAdmin):
    """Customizes admin pages for SupplyChains."""

    list_display = [
        'id',
        'name',
    ]
    list_display_links = ['id', 'name', ]
    fields = [
        'name',
    ]
    inlines = [SupplyLinkInlineAdmin, ]
