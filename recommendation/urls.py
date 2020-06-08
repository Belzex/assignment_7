from django.urls import path
from .views import home, recommendation, error

urlpatterns = [path('', home),
               path('recommendations.html', recommendation),
               path('error.html', error)]