import django_filters
from .models import Recipe, Favorite, Basket, Teg


class RecipeFilter(django_filters.FilterSet):
    # author = django_filters.CharFilter(
    #     field_name='author__username', lookup_expr='iexact')
    is_favorited = django_filters.BooleanFilter(
        method='filter', label='Is Favorited')
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter', label='is in shopping cart')
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Teg.objects.all(),
        field_name='tags',
        to_field_name='id',
        widget=django_filters.widgets.CSVWidget(),
        label='Теги'
    )

    class Meta:
        model = Recipe
        fields = ['author']

    def filter(self, queryset, name, value):
        """Фильтр избраное и список покупок"""
        if name == 'is_favorited':
            model = Favorite
        elif name == 'is_in_shopping_cart':
            model = Basket

        result = model.objects.filter(
            user=self.request.user).values('recipe')
        if value:
            return queryset.filter(id__in=result)
        else:
            return queryset.exclude(id__in=result)
