from django.urls import path
from .views import home #results

urlpatterns = [
    path('', home, name='home'),
    # path('pump_results/', results, name='pump_results'),
]
