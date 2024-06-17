from django.urls import path

from . import views

urlpatterns = [
    path('home/', views.home, name='home_url'),
    path('genqr/', views.generate_qr),
    path('fetch_external_data/', views.fetch_external_data),
    path('inventory/', views.inventory),
    path('fetch_inventory/', views.fetch_inventory, name='fetch_inventory'),
    path('item_page/', views.item_page, name='item_page'),

]
