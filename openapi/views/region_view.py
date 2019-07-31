# -*- coding: utf-8 -*-
# creater by: barnett
import logging
from console.services.region_services import region_services
from console.services.region_services import RegionExistException
from openapi.views.base import ListAPIView
from openapi.views.base import BaseOpenAPIView
from rest_framework import status
from rest_framework.response import Response
from drf_yasg import openapi
from www.utils.crypt import make_uuid
from drf_yasg.utils import swagger_auto_schema
from openapi.serializer.region_serializer import RegionInfoSerializer
from openapi.serializer.base_serializer import FailSerializer
logger = logging.getLogger("default")


class ListRegionInfo(ListAPIView):
    view_perms = ["regions"]

    @swagger_auto_schema(
        responses={200: RegionInfoSerializer(many=True)}, tags=['openapi-region'], operation_description="获取全部数据中心列表")
    def get(self, request):
        queryset = region_services.get_all_regions()
        serializer = RegionInfoSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="添加数据中心",
        request_body=openapi.Schema(
            title="AddRegionRequest",
            type=openapi.TYPE_OBJECT,
            required=['region_name', 'region_alias', 'url', 'wsurl', 'httpdomain', 'tcpdomain'],
            properties={
                'region_name': openapi.Schema(type=openapi.TYPE_STRING),
                'region_alias': openapi.Schema(type=openapi.TYPE_STRING),
                'url': openapi.Schema(type=openapi.TYPE_STRING),
                'token': openapi.Schema(type=openapi.TYPE_STRING),
                'wsurl': openapi.Schema(type=openapi.TYPE_STRING),
                'httpdomain': openapi.Schema(type=openapi.TYPE_STRING),
                'tcpdomain': openapi.Schema(type=openapi.TYPE_STRING),
                'scope': openapi.Schema(type=openapi.TYPE_STRING),
                'ssl_ca_cert': openapi.Schema(type=openapi.TYPE_STRING),
                'cert_file': openapi.Schema(type=openapi.TYPE_STRING),
                'key_file': openapi.Schema(type=openapi.TYPE_STRING),
                'status': openapi.Schema(type=openapi.TYPE_INTEGER),
                'desc': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            status.HTTP_201_CREATED: RegionInfoSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: None,
            status.HTTP_400_BAD_REQUEST: FailSerializer(),
        },
        security=[],
        tags=['openapi-region'],
    )
    def post(self, request):
        try:
            serializer = RegionInfoSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            region_data = serializer.data
            region_data["region_id"] = make_uuid()
            region = region_services.add_region(region_data)
            if region:
                return Response(region, status=status.HTTP_201_CREATED)
            else:
                return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except RegionExistException as e:
            return Response({"msg": e.message}, status=status.HTTP_400_BAD_REQUEST)


class RegionInfo(BaseOpenAPIView):
    @swagger_auto_schema(
        operation_description="获取指定数据中心数据",
        responses={200: RegionInfoSerializer()},
        tags=['openapi-region'],
    )
    def get(self, request, region_id):
        queryset = region_services.get_region_by_region_id(region_id)
        serializer = RegionInfoSerializer(queryset)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="更新指定数据中心元数据",
        request_body=openapi.Schema(
            title="UpdateRegionRequest",
            type=openapi.TYPE_OBJECT,
            properties={
                'region_alias': openapi.Schema(type=openapi.TYPE_STRING),
                'url': openapi.Schema(type=openapi.TYPE_STRING),
                'token': openapi.Schema(type=openapi.TYPE_STRING),
                'wsurl': openapi.Schema(type=openapi.TYPE_STRING),
                'httpdomain': openapi.Schema(type=openapi.TYPE_STRING),
                'tcpdomain': openapi.Schema(type=openapi.TYPE_STRING),
                'scope': openapi.Schema(type=openapi.TYPE_STRING),
                'ssl_ca_cert': openapi.Schema(type=openapi.TYPE_STRING),
                'cert_file': openapi.Schema(type=openapi.TYPE_STRING),
                'key_file': openapi.Schema(type=openapi.TYPE_STRING),
                'desc': openapi.Schema(type=openapi.TYPE_STRING),
                'status': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
        responses={
            200: RegionInfoSerializer(),
            400: FailSerializer()
        },
        tags=['openapi-region'],
    )
    def put(self, request, region_id):
        serializer = RegionInfoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        region_data = serializer.data
        if not region_id:
            return Response({"msg": "RegionID不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        if not region_services.get_region_by_region_id(region_id):
            return Response({"msg": "修改的数据中心不存在"}, status=status.HTTP_400_BAD_REQUEST)
        new_region = region_services.update_region(region_data)
        return Response(new_region)