from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Tickers
    path('tickers/', views.ticker_list, name='ticker_list'),
    path('tickers/add/', views.ticker_create, name='ticker_create'),
    path('tickers/<int:pk>/', views.ticker_detail, name='ticker_detail'),
    path('tickers/<int:pk>/edit/', views.ticker_update, name='ticker_update'),
    path('tickers/<int:pk>/delete/', views.ticker_delete, name='ticker_delete'),

    # Positions
    path('positions/', views.position_list, name='position_list'),
    path('positions/add/', views.position_create, name='position_create'),
    path('positions/<int:pk>/', views.position_detail, name='position_detail'),
    path('positions/<int:pk>/edit/', views.position_update, name='position_update'),
    path('positions/<int:pk>/delete/', views.position_delete, name='position_delete'),

    # Dividends
    path('dividends/', views.dividend_list, name='dividend_list'),
    path('dividends/add/', views.dividend_create, name='dividend_create'),
    path('dividends/<int:pk>/edit/', views.dividend_update, name='dividend_update'),
    path('dividends/<int:pk>/delete/', views.dividend_delete, name='dividend_delete'),

    # Projections
    path('projections/', views.projection, name='projection'),
]
