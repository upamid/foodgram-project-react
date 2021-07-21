from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField


from recipes.models import Recipe, Ingredient, IngredientAmount, Tag
from users.models import ConstUserRoles, CustomUser


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(default=ConstUserRoles.USER)

    class Meta:
        fields = (
            'first_name',
            'last_name',
            'username',
            'bio',
            'email',
            'role',
            'confirmation_code')
        model = CustomUser
        extra_kwargs = {
            'confirmation_code': {'write_only': True},
            'username': {'required': True},
            'email': {'required': True}}

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        

class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')

class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    # author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(read_only=True, many=True)
    image = Base64ImageField(
        max_length=None, use_url=True,
    )
    class Meta:
        # fields = (
        #     'id', 'tags', 'author', 'ingredients',
        #     'name', 'image', 'text', 'cooking_time'
        # )
        exclude = ('id', 'is_favorited', 'is_in_shopping_cart', 'author')
        model = Recipe
    # def get_ingredients(self, obj):
    #     query = IngredientAmount.objects.filter(recipe=obj)
    #     return [RecipeIngredientSerializer(i).data for i in query]
