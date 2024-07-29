from django.urls import path

from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('genqr/', views.generate_qr),
    path('myapp/fetch_external_data/', views.fetch_external_data),
    path('fetch_external_data/', views.fetch_external_data, name='fetch_external_data'),
    path('fetch_inventory/', views.fetch_inventory, name='fetch_inventory'),
    path('item_page/', views.item_page, name='item_page'),
    path('base/', views.base, name='base'),
    path('items/', views.item_list, name='items'),

    # path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    # path('hf.html/', views.header_footer)
    # path('inventory/', views.inventory),
    # path('home/', views.home, name='home_url'),

]
