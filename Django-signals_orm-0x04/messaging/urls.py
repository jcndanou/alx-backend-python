from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('delete-account/', views.delete_user, name='delete_user'),
    path('inbox/', views.inbox_view, name='inbox'),
]