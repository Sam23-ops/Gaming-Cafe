from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    path('', views.games_list_view, name='games_list'),
    path('<slug:slug>/', views.game_detail_view, name='game_detail'),
]
