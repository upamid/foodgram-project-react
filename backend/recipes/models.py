from django.db import models

from users.models import CustomUser

class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        blank=False,
        max_length=200,
        help_text='Укажите название ингредиента'
    )
    color = models.CharField(verbose_name=(u'Color'), max_length=7,
                         help_text=(u'HEX color, as #RRGGBB'))
    slug = models.SlugField(max_length=50, unique=True)

class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        blank=False,
        max_length=200,
        help_text='Укажите название ингредиента'
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        blank=False,
        max_length=200,
        help_text='Укажите единицу измерения'
    )

class Recipe(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='recipe',
        verbose_name='Теги',
    )
    author = models.ForeignKey(
        CustomUser,
        blank=False,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=True,
        through='IngredientAmount',
        related_name='recipe',
        verbose_name='Ингредиенты',
    )
    is_favorited = models.BooleanField(
        blank=False
    )
    is_in_shopping_cart = models.BooleanField(
        blank=False
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        blank=False,
        help_text='Напишите название рецепта'
    )
    image = models.ImageField(
        upload_to='image/', 
        null=False
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        blank=False,
        help_text='Добавьте сюда описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        blank=False,
        help_text='Укажите Время приготовления в минутах',
    )
    is_favorited = models.BooleanField(
        default=False,
        blank=False,
    )
    is_in_shopping_cart = models.BooleanField(
        default=False,
        blank=False,
    )
    class Meta:
        verbose_name_plural = 'Рецепты'
        ordering = ['id']

class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, 
        on_delete=models.CASCADE,
        blank=False
    )
    recipe = models.ForeignKey(
        Recipe, 
        on_delete=models.CASCADE,
        blank=False
    )
    amount = models.PositiveSmallIntegerField(
        blank=False
    )