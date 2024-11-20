from django.urls import include, path


urlpatterns = [
    path('', include('api.reviews.urls')),
    path('', include('api.users.urls')),
]
