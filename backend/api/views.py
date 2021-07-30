from django.db.models import Avg, Max, Sum
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.contrib.auth.decorators import login_required 
import io
import reportlab
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, permissions, serializers, status, views,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination

from recipes.models import Recipe, Ingredient, Tag, ShoppingCart, Follow, Favorite, IngredientAmount
from users.models import CustomUser
from rest_framework import viewsets

from .filterset import RecipeFilter
from .utils import generate_confirmation_code, send_mail_to_user
from .viewset import CatGenViewSet
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorOrAdmin, IsSuperuser)
from .serializers import (
    RecipeSerializer,
    IngredientSerializer,
    UserSerializer,
    TagSerializer,
    ShoppingCartSerializer,
    FollowSerializer,
    FavoriteSerializer,
    ListRecipeSerializer
)

from rest_framework.serializers import ValidationError


BASE_USERNAME = 'User'


class RegisterView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        user = CustomUser.objects.filter(email=email)
        if len(user) > 0:
            confirmation_code = user[0].confirmation_code
        else:
            confirmation_code = generate_confirmation_code()
            max_id = CustomUser.objects.aggregate(Max('id'))['id__max'] + 1
            data = {
                'email': email,
                'confirmation_code': confirmation_code,
                'username': f'{BASE_USERNAME}{max_id}'}
            serializer = UserSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        send_mail_to_user(email, confirmation_code)
        return Response({'email': email})


class TokenView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def post(self, request):
        user = get_object_or_404(CustomUser, email=request.data.get('email'))
        if user.confirmation_code != request.data.get('confirmation_code'):
            response = {'confirmation_code': 'Неверный код для данного email'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        response = {'token': self.get_token(user)}
        return Response(response, status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    lookup_field = 'username'
    permission_classes = (permissions.IsAuthenticated, IsSuperuser | IsAdmin,)

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        methods=['get', 'patch'],
        url_path='me')
    def get_or_update_self(self, request):
        if request.method != 'GET':
            serializer = self.get_serializer(
                instance=request.user,
                data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(
                request.user,
                many=False)
            return Response(serializer.data)

class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrAdmin,)
    queryset = Recipe.objects.all()
    serializer_class = ListRecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def get_serializer_context(self):
        context = super(RecipeViewSet, self).get_serializer_context()
        context.update({"user_id": self.request.user.id})
        return context

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        methods=['get', ])
    def download_shopping_cart(self, request):
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
        pdfmetrics.registerFont(TTFont('FreeSans', settings.STATIC_ROOT+'/FreeSans.ttf'))
        textob = c.beginText()
        textob.setTextOrigin(inch, inch)
        textob.setFont("FreeSans", 14)

        user = request.user
        recipes_id = ShoppingCart.objects.filter(owner=user).values('item')
        ingredients_id = Recipe.objects.filter(id__in=recipes_id).values('ingredients')
        ingredients = Ingredient.objects.filter(id__in=ingredients_id)

        lines = []

        for ingredient in ingredients:
            amount = IngredientAmount.objects.filter(ingredient=ingredient, recipe__in=recipes_id).aggregate(total_amount=Sum('amount'))["total_amount"]

            lines.append(ingredient.name)
            lines.append(str(amount))
            lines.append(" ")
            lines.append(f'{ingredient.name} ({ingredient.measurement_unit}) – {str(amount)}')

        for line in lines:
            textob.textLine(line)

        c.drawText(textob)    
        c.showPage()
        c.save()
        buf.seek(0)

        return FileResponse(buf, as_attachment=True, filename='shop.pdf')
        
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['tags'] = [{'id': idx} for idx in data['tags']]
        serializer = RecipeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class IngredientViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrAdmin,)
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class TagViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrAdmin,)
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class ShoppingCartViewSet(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TagSerializer
    pagination_class = None
    def get(self, request, recipe_id):
        item = get_object_or_404(Recipe, pk=recipe_id)
        owner = self.request.user
        if ShoppingCart.objects.filter(item=item, owner=owner).exists():
            return Response(
                'Вы уже добавили в список покупок',
                status=status.HTTP_400_BAD_REQUEST)
        shopcart = ShoppingCart.objects.create(item=item, owner=owner)
        serializer = ShoppingCartSerializer(shopcart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, recipe_id):
        user = request.user
        item = get_object_or_404(Recipe, pk=recipe_id)
        follow = ShoppingCart.objects.get(item=item, owner=user)
        follow.delete()
        return Response('Удалено', status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FavoriteSerializer
    pagination_class = None
    def get(self, request, recipe_id):
        fav_item = get_object_or_404(Recipe, pk=recipe_id)
        fav_user = self.request.user
        if Favorite.objects.filter(fav_item=fav_item, fav_user=fav_user).exists():
            return Response(
                'Вы уже добавили в избранное',
                status=status.HTTP_400_BAD_REQUEST)
        favorite = Favorite.objects.create(fav_item=fav_item, fav_user=fav_user)
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, recipe_id):
        fav_user = request.user
        fav_item = get_object_or_404(Recipe, pk=recipe_id)
        follow = Favorite.objects.get(fav_item=fav_item, fav_user=fav_user)
        follow.delete()
        return Response('Удалено', status=status.HTTP_204_NO_CONTENT)


class SubscribeView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, user_id):
        user = request.user
        author = get_object_or_404(CustomUser, id=user_id)
        if Follow.objects.filter(user=user, author=author).exists():
            return Response(
                'Вы уже подписаны',
                status=status.HTTP_400_BAD_REQUEST)
        follow = Follow.objects.create(user=user, author=author)
        serializer = FollowSerializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    def delete(self, request, user_id):
        user = request.user
        author = get_object_or_404(CustomUser, id=user_id)
        follow = Follow.objects.get(user=user, author=author)
        follow.delete()
        return Response('Удалено', status=status.HTTP_204_NO_CONTENT)

class SubscribeListViewSet(viewsets.ModelViewSet, PageNumberPagination):
    permission_classes = (IsAuthorOrAdmin,)
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    def list(self, request, *args, **kwargs):
        user = self.request.user
        subscriptions = Follow.objects.filter(user=user)
        page = self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
        # return Response(serializer.data, status=status.HTTP_200_OK)
