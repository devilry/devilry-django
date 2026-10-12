from django.db import models
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from django_cradmin.demo.cradmin_javascript_demos import demo_serializers
from django_cradmin.demo.cradmin_javascript_demos.models import FictionalFigure


class FictionalFigurePagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = "page_size"


class FictionalFigureViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = demo_serializers.FictionalFigureSerializer
    pagination_class = FictionalFigurePagination

    def get_queryset(self):
        # WARNING: In a real world use case, you will often want to restrict permissions,
        #          instead of giving anyone access to everything!
        queryset = FictionalFigure.objects.all()
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(models.Q(name__icontains=search) | models.Q(about__icontains=search))
        if "is_godlike" in self.request.query_params:
            is_godlike = self.request.query_params.get("is_godlike") == "true"
            if is_godlike:
                queryset = queryset.filter(is_godlike=is_godlike)

        if "rating" in self.request.query_params:
            try:
                rating = int(self.request.query_params.get("rating"))
            except ValueError:
                rating = 0
            queryset = queryset.filter(rating__gte=rating)

        # time.sleep(2)
        return queryset


class MoveSerializer(serializers.Serializer):
    """
    Serializer for :class:`.FictionalFigureMoveView`.
    """

    moving_object_id = serializers.IntegerField(required=True)
    move_before_object_id = serializers.IntegerField(required=True, allow_null=True)


class FictionalFigureMoveView(GenericAPIView):
    def get_serializer_class(self):
        return demo_serializers.FictionalFigureSerializer

    def get_queryset(self):
        return FictionalFigure.objects.all()

    def __get_fictionalfigure_object(self, pk):
        if pk is None:
            return None
        return self.get_queryset().get(pk=pk)

    def __set_sortindex(self, moving_object, move_before_object):
        """
        HINT: You can save having to implement sort by using the
        sortable models. Refer to sortable.rst in the docs for more info.
        """
        fictional_figures = FictionalFigure.objects.order_by("sort_index", "name")
        index = 0
        for fictional_figure in fictional_figures:
            if fictional_figure == moving_object:
                continue
            if fictional_figure == move_before_object:
                moving_object.sort_index = index
                moving_object.save()
                index += 1
            fictional_figure.sort_index = index
            fictional_figure.save()
            index += 1
        if move_before_object is None:
            moving_object.sort_index = index
            moving_object.save()

    def post(self, request, **kwargs):
        serializer = MoveSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        moving_object = self.__get_fictionalfigure_object(pk=serializer.validated_data["moving_object_id"])
        move_before_object = self.__get_fictionalfigure_object(pk=serializer.validated_data["move_before_object_id"])
        self.__set_sortindex(moving_object=moving_object, move_before_object=move_before_object)
        return Response(serializer.data)
