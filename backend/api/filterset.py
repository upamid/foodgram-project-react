from django.db.models import Q
from django_filters import rest_framework

from recipes.models import Recipe

class RecipeFilter(rest_framework.FilterSet):

    tags = rest_framework.CharFilter(field_name="tags__slug", method='filter_tags')


    class Meta:
        model = Recipe
        fields = ['tags']

    def filter_tags(self, queryset, name, tags):
        queries = [Q(tags__slug=tag) for tag in tags]
        query = queries.pop()
        for item in queries:
            query |= item
        return queryset.filter(query)
        # return queryset.filter(tags__slug__contains=tags.split(','))