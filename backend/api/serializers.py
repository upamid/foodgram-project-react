from rest_framework import serializers
from rest_framework.serializers import ValidationError
from drf_extra_fields.fields import Base64ImageField


from recipes.models import Recipe, Ingredient, IngredientAmount, Tag, TagRecipe, ShoppingCart
from users.models import ConstUserRoles, CustomUser


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'first_name',
            'last_name',
            'username',
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
    id =  serializers.IntegerField(source='tag.id')
    name =  serializers.ReadOnlyField(source = 'tag.name')
    color =  serializers.ReadOnlyField(source = 'tag.color')
    slug =  serializers.ReadOnlyField(source = 'tag.slug')
    class Meta:
        model = TagRecipe
        fields = ('id', 'name', 'color', 'slug')       


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id =  serializers.IntegerField(source='ingredient.id')
    measurement_unit =  serializers.ReadOnlyField(source = 'ingredient.measurement_unit')
    name =  serializers.ReadOnlyField(source = 'ingredient.name')
    amount = serializers.IntegerField()
    class Meta:
        model = IngredientAmount
        fields = [  'id', 'name','measurement_unit', 'amount',]

class ShoppingCartSerializer(serializers.ModelSerializer):
    id =  serializers.IntegerField(source='item.id')
    name =  serializers.ReadOnlyField(source = 'item.name')
    image =  Base64ImageField(read_only=True, source = 'item.image')
    cooking_time = serializers.ReadOnlyField(source = 'item.cooking_time')
    class Meta:
        model = ShoppingCart
        fields = [  'id', 'name','image', 'cooking_time',]

class RecipeSerializer(serializers.ModelSerializer):
    tags = TagRecipeSerializer(source='tagrecipe_set', many=True, required=False)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(source = 'ingredientamount_set', many=True, required=False)
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
        # if validated_data.get('tagrecipe_set', None)!=10:
        #         raise ValidationError(['AAAAAAAAAAAAAAAA{}'.format(validated_data)])
        tags = validated_data.pop('tagrecipe_set')
        ingredients = validated_data.pop('ingredientamount_set')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            current_tag = Tag.objects.get(id=tag.get('tag').get('id'))
            TagRecipe.objects.create(
                tag=current_tag, recipe=recipe)
        # recipe.tags.add(*tags)
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(id=ingredient.get('ingredient').get('id'))
            IngredientAmount.objects.create(
                ingredient=current_ingredient, recipe=recipe, amount=ingredient.get('amount'))
        return recipe 