import django_filters
from reviews.models import ShoppingCart, Favorite, Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.ChoiceFilter(
        method='filter',
        choices=[('1', 'Yes'), ('0', 'No')],
        label='Is Favorited'
    )
    is_in_shopping_cart = django_filters.ChoiceFilter(
        method='filter',
        choices=[('1', 'Yes'), ('0', 'No')],
        label='Is in Shopping Cart'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        label='Теги'
    )

    class Meta:
        model = Recipe
        fields = ['author']

    def filter(self, queryset, name, value):
        """Фильтр избраное и список покупок"""
        if value == '1':
            value = True
        elif value == '0':
            value = False
        else:
            return queryset

        if name == 'is_favorited':
            model = Favorite
        elif name == 'is_in_shopping_cart':
            model = ShoppingCart

        if not self.request.user.is_authenticated:
            return queryset

        result = model.objects.filter(
            user=self.request.user).values('recipe')
        if value:
            return queryset.filter(id__in=result)
        else:
            return queryset.exclude(id__in=result)
