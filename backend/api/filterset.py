from django.db.models import Q
from django_filters import rest_framework
import django_filters

from recipes.models import Recipe, Tag, Favorite, ShoppingCart


class RecipeFilter(rest_framework.FilterSet):

    tags = django_filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        # method='filter_tags',
        to_field_name='slug',
        queryset=Tag.objects.all()
        )

    is_favorited = django_filters.BooleanFilter(
        field_name="is_favorited",
        method='filter_is_favorited',
    )

    is_in_shopping_cart = django_filters.BooleanFilter(
        field_name="is_in_shopping_cart",
        method='filter_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'is_favorited']

    def filter_is_favorited(self, queryset, name, tags):
        user = self.request.user
        fav_recipes = Favorite.objects.filter(fav_user=user).values('fav_item')
        return queryset.filter(id__in=fav_recipes)

    def filter_is_in_shopping_cart(self, queryset, name, tags):
        user = self.request.user
        fav_recipes = ShoppingCart.objects.filter(owner=user).values('item')
        return queryset.filter(id__in=fav_recipes)