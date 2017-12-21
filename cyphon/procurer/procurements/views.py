# -*- coding: utf-8 -*-
# Copyright 2017 Dunbar Security Solutions, Inc.
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

"""

# third party
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route

# local
from alerts.models import Alert
from cyphon.tasks import procure_order
from procurer.supplychains.exceptions import SupplyChainError
from procurer.supplyorders.models import SupplyOrder
from procurer.supplyorders.serializers import SupplyOrderSerializer
from .models import Procurement
from .serializers import ProcurementSerializer#, ProcurementProcessSerializer


class ProcurementViewSet(viewsets.ReadOnlyModelViewSet):
    """REST API views for Procurements."""

    queryset = Procurement.objects.all()
    serializer_class = ProcurementSerializer

    @staticmethod
    def _get_alert(request):
        """

        """
        user = request.user
        alert_id = request.query_params.get('id') or request.data.get('id')
        return Alert.objects.filter_by_user(user)\
                            .filter(pk=int(alert_id))\
                            .first()

    def _get_serialized_queryset(self, queryset):
        """

        """
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    @list_route(methods=['get', 'post'], url_path='by-alert')
    def filtered_by_alert(self, request, *args, **kwargs):
        """Get |Distilleries| that are associated with |Alerts|.

        Parameters
        ----------
        request : :class:`rest_framework.request.Request`
            A Django REST framework HTTP `Request`_ object.

        Returns
        -------
        :class:`rest_framework.response.Response`
            A Django REST framework HTTP `Response`_ object containing
            a list of JSON serialized |Distilleries| associated with
            |Alerts|.

        """
        alert = self._get_alert(request)
        if alert:
            filtered_qs = self.filter_queryset(self.get_queryset())
            filtered_by_user = Procurement.objects.filter_by_user(
                user=request.user,
                queryset=filtered_qs
            )
            filtered_qs = Procurement.objects.filter_by_alert(
                alert=alert,
                user=request.user,
                queryset=filtered_by_user
            )
        else:
            filtered_qs = Procurement.objects.none()

        return self._get_serialized_queryset(filtered_qs)

    @detail_route(methods=['post'], url_path='process')
    def process(self, request, *args, **kwargs):
        """Get |Distilleries| that are associated with |Alerts|.

        Parameters
        ----------
        request : :class:`rest_framework.request.Request`
            A Django REST framework HTTP `Request`_ object.

        Returns
        -------
        :class:`rest_framework.response.Response`
            A Django REST framework HTTP `Response`_ object containing
            a list of JSON serialized |Distilleries| associated with
            |Alerts|.

        """
        procurement = self.get_object()

        try:
            procurement.validate(request.data)
            supplyorder = SupplyOrder.objects.create(
                procurement=procurement,
                alert=None,
                user=request.user,
                input_data=request.data
            )
            supplyorder.process()
            serializer = SupplyOrderSerializer(supplyorder)
            return Response(serializer.data)

        except SupplyChainError as error:
            return Response(
                vars(error),
                status=status.HTTP_400_BAD_REQUEST
            )

    @detail_route(methods=['get', 'post'], url_path='process-alert')
    def process_alert(self, request, *args, **kwargs):
        """Get |Distilleries| that are associated with |Alerts|.

        Parameters
        ----------
        request : :class:`rest_framework.request.Request`
            A Django REST framework HTTP `Request`_ object.

        Returns
        -------
        :class:`rest_framework.response.Response`
            A Django REST framework HTTP `Response`_ object containing
            a list of JSON serialized |Distilleries| associated with
            |Alerts|.

        """
        procurement = self.get_object()
        alert = self._get_alert(request)

        try:
            supplyorder = SupplyOrder.objects.create(
                procurement=procurement,
                alert=alert,
                user=request.user
            )
            supplyorder.use_alert_data()
            supplyorder.process()
            serializer = SupplyOrderSerializer(supplyorder)
            return Response(serializer.data)

        except SupplyChainError as error:
            return Response(
                vars(error),
                status=status.HTTP_400_BAD_REQUEST
            )
