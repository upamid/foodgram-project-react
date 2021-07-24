from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    TokenView,
    UsersViewSet,
    RecipeViewSet,
    IngredientViewSet,
    TagViewSet,
    ShoppingCartViewSet,
    )
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenObtainSlidingView,
    TokenRefreshView,
)


v1_router = DefaultRouter()
v1_router.register('users', UsersViewSet)
v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('tags', TagViewSet, basename='tag')
# v1_router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
#                    ShoppingCartViewSet,
#                    basename='shopping_cart')
# v1_router.register('categories', CategoryViewSet, basename='category')
# v1_router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
#                    basename='review')
# comments_url = r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments'
# v1_router.register(comments_url, CommentViewSet, basename='comments')

urlpatterns = [
    # path('users/', RegisterView.as_view()),
    # Djoser создаст набор необходимых эндпоинтов.
    # базовые, для управления пользователями в Django:
    path('', include('djoser.urls')),
    # JWT-эндпоинты, для управления JWT-токенами:
    path('auth/', include('djoser.urls.authtoken')),
    # path('auth/token/login/', TokenObtainSlidingView.as_view(), name='token_obtain_pair'),
    # path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('recipes/<int:recipe_id>/shopping_cart/', ShoppingCartViewSet.as_view(), name='shopping_cart'),
    # path('auth/token/login/', TokenView.as_view()),
    path('', include(v1_router.urls)),
    
]
