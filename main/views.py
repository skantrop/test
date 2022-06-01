from django.db.models import Avg
import django_filters.rest_framework as filters
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework import viewsets, mixins
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .filters import ProductFilter, OrderFilter
from .models import Product, Review, Order, WishList
from .permissions import IsAuthororAdminPermission, DenyAll
from .serializers import (ProductListSerializer,
                          ProductDetailsSerializer, ReviewSerializer, OrderSerializer)


# 1.Список товаров, доступен всем пользователям
# @api_view(['GET'])
# def products_list(request):
#     queryset = Product.objects.all()
#     filtered_qs = ProductFilter(request.GET, queryset=queryset)
#     serializer = ProductListSerializer(filtered_qs.qs, many=True)
#     serializer_queryset = serializer.data
#     return Response(data=serializer_queryset, status=status.HTTP_200_OK)


# class ProductList(APIView):
#     def get(self, request):
#         queryset = Product.objects.all()
#         filtered_qs = ProductFilter(request.GET, queryset=queryset)
#         serializer = ProductListSerializer(filtered_qs.qs, many=True)
#         serializer_queryset = serializer.data
#         return Response(data=serializer_queryset, status=status.HTTP_200_OK)


# class ProductListView(ListAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductListSerializer
#     filter_backends = (filters.DjangoFilterBackend, )
#     filterset_class = ProductFilter
#
#
# # 2. Детали товаров, доступны всем
# class ProductDetailsView(RetrieveAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductDetailsSerializer
#
#
# # 3. Создание товаров, редактирование, удаление, доступно только админам
# class CreateProductView(CreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductDetailsSerializer
#     permission_classes = [IsAdminUser]
#
#
# class UpdateProductView(UpdateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductDetailsSerializer
#     permission_classes = [IsAdminUser]
#
#
# class DeleteProductView(DestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductDetailsSerializer
#     permission_classes = [IsAdminUser]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductDetailsSerializer
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_class = ProductFilter
    ordering_fields = ['title', 'price']


    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        elif self.action in ['create_review', 'like']:
            return [IsAuthenticated()]
        return []

    # api/v1/products/id/create_review/
    @action(detail=True, methods=['POST'])
    def create_review(self, request, pk):
        data = request.data.copy()
        data['product'] = pk
        serializer = ReviewSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)

    @action(detail=True, methods=['POST'])
    def like(self, request, pk):
        product = self.get_object()
        user = request.user
        like_obj, created = WishList.objects.get_or_create(product=product, user=user)

        if like_obj.is_liked:
            like_obj.is_liked = False
            like_obj.save()
            return Response('disliked')
        else:
            like_obj.is_liked = True
            like_obj.save()
            return Response('liked')


# 4. Создание отзывов, доступно только залогиненным пользователям
# class CreateReview(CreateAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_serializer_context(self):
#         return {'request': self.request}

class ReviewViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthororAdminPermission()]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_class = OrderFilter
    ordering_fields = ['total_sum', 'created_at']

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [IsAdminUser()]
        else:
            return [DenyAll()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset

#products/
# POST - create
# GET -list

# products/id/
# GET - retrieve
# PUT - update
# PATCH - partial_update
# DELETE - destroy

# 5. Листинг отзывов (внутри деталей продукта), доступен всем
# 6. Редактирование и удаление отзыва может делать только автор
# 7. Заказ может создать любой залогиненный пользователь
# 8. Список заказов: пользователь видит только свои заказы, админы видят все
# 9. Редактировать заказы может только админ

#TODO: Тесты
#TODO: Документация


