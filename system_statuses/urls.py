from django.urls import path
from .views import status, status_table


urlpatterns = [
    path('', status, name='status'),
    path('table', status_table, name="status_table"),
]
