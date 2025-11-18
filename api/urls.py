from django.urls import path
from . import views

urlpatterns = [
    path('check-config/', views.check_config, name='check_config'),
    path('start-oauth/', views.start_oauth, name='start_oauth'),
    path('auth/token', views.exchange_token, name='exchange_token'),
    path('auth/token-account', views.exchange_token_account, name='exchange_token_account'),
    path('test/', views.test_connection, name='test_connection'),
    path('family/', views.get_family, name='get_family'),
    path('players/', views.get_players, name='get_players'),
    path('players/<str:player_id>/', views.get_player_detail, name='get_player_detail'),
    path('library/', views.get_library, name='get_library'),
    path('card/<str:card_id>/', views.get_card_detail, name='get_card_detail'),
]
