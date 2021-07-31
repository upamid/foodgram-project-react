from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Follow, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag, TagRecipe)
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from users.models import ConstUserRoles, CustomUser


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'first_name',
            'last_name',
            'username',
            'id',
            'email',)
        model = CustomUser
        extra_kwargs = {
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


class TagRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='tag.id')
    name = serializers.ReadOnlyField(source='tag.name')
    color = serializers.ReadOnlyField(source='tag.color')
    slug = serializers.ReadOnlyField(source='tag.slug')

    class Meta:
        model = TagRecipe
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
        )
    name = serializers.ReadOnlyField(source='ingredient.name')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ['id', 'name', 'measurement_unit', 'amount']


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='item.id')
    name = serializers.ReadOnlyField(source='item.name')
    image = Base64ImageField(read_only=True, source='item.image')
    cooking_time = serializers.ReadOnlyField(source='item.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ['id', 'name', 'image', 'cooking_time']


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='fav_item.id')
    name = serializers.ReadOnlyField(source='fav_item.name')
    image = Base64ImageField(read_only=True, source='fav_item.image')
    cooking_time = serializers.ReadOnlyField(source='fav_item.cooking_time')

    class Meta:
        model = Favorite
        fields = ['id', 'name', 'image', 'cooking_time']


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            )

    def get_is_subscribed(self, obj):
        author = obj.author
        user = obj.user
        if Follow.objects.filter(author=user, user=author).exists():
            return True
        return False

    def get_recipes(self, obj):
        author = obj.author
        recepts_follow = Recipe.objects.filter(author=author)
        return RecipeSerializer(recepts_follow, many=True).data

    def get_recipes_count(self, obj):
        author = obj.author
        count = Recipe.objects.filter(author=author).count()
        return count


class ListRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagRecipeSerializer(
        source='tagrecipe_set',
        many=True,
        required=False
        )
    ingredients = RecipeIngredientSerializer(
        source='ingredientamount_set',
        many=True,
        required=False
        )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        fav_user = self.context.get("user_id")
        fav_item = obj.id
        if Favorite.objects.filter(
            fav_user=fav_user,
            fav_item=fav_item
                ).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        owner = self.context.get("user_id")
        item = obj.id
        if ShoppingCart.objects.filter(owner=owner, item=item).exists():
            return True
        return False


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagRecipeSerializer(
        source='tagrecipe_set',
        many=True,
        required=False
        )
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='ingredientamount_set',
        many=True,
        required=False
        )
    image = Base64ImageField(
        max_length=None, use_url=True,
    )

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )
        model = Recipe

    def create(self, validated_data):
        tags = validated_data.pop('tagrecipe_set')
        ingredients = validated_data.pop('ingredientamount_set')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            current_tag = Tag.objects.get(id=tag.get('tag').get('id'))
            TagRecipe.objects.create(
                tag=current_tag, recipe=recipe)
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(
                id=ingredient.get('ingredient').get('id')
                )
            IngredientAmount.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=ingredient.get('amount')
                )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tagrecipe_set')
        ingredients = validated_data.pop('ingredientamount_set')
        Recipe.objects.filter(id=instance.id).update(**validated_data)
        recipe = Recipe.objects.get(id=instance.id)
        recipe.tags.remove()
        try:
            recipe_ingredients = IngredientAmount.objects.filter(
                recipe_id=instance.id
            )
            recipe_ingredients.delete()
        except recipe_ingredients.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            recipe_tags = TagRecipe.objects.filter(
                recipe_id=instance.id
            )
            recipe_tags.delete()
        except recipe_tags.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        for tag in tags:
            current_tag = Tag.objects.get(id=tag.get('tag').get('id'))
            TagRecipe.objects.create(
                tag=current_tag, recipe=recipe)
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(
                id=ingredient.get('ingredient').get('id')
                )
            IngredientAmount.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=ingredient.get('amount')
                )
        return recipe
