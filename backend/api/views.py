from django.db.models import Avg, Max
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, permissions, serializers, status, views,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from recipes.models import Recipe, Ingredient, Tag
from users.models import CustomUser
from rest_framework import viewsets

from .utils import generate_confirmation_code, send_mail_to_user
from .viewset import CatGenViewSet
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorOrAdmin, IsSuperuser)
from .serializers import RecipeSerializer, IngredientSerializer, UserSerializer, TagSerializer


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
    serializer_class = RecipeSerializer

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