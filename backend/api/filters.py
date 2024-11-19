import django_filters

from .models import Basket, Favorite, Recipe, Teg


class RecipeFilter(django_filters.FilterSet):
    # is_favorited = django_filters.BooleanFilter(
    #     method='filter', label='Is Favorited')
    # is_in_shopping_cart = django_filters.BooleanFilter(
    #     method='filter', label='is in shopping cart')
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
        queryset=Teg.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        # widget=django_filters.widgets.CSVWidget(),
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
            model = Basket

        if not self.request.user.is_authenticated:
            return queryset

        result = model.objects.filter(
            user=self.request.user).values('recipe')
        if value:
            return queryset.filter(id__in=result)
        else:
            return queryset.exclude(id__in=result)
