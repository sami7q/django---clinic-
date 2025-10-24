from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.users_list, name='list'),
    path('create/', views.create_user, name='create'),
    path('<int:user_id>/edit/', views.edit_user, name='edit'),
    path('<int:user_id>/delete/', views.delete_user, name='delete'),
    path('<int:user_id>/delete/', views.delete_user, name='delete'),
    path('<int:user_id>/password/', views.change_password, name='change_password'),
]
