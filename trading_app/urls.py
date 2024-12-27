from django.urls import path
from .views import (home, create_order, orders_list, backtest_view, user_login, user_logout, user_register)

urlpatterns = [
    path('', user_login, name='login'), # 루트("")를 로그인 페이지로 연결
    path('create_order/', create_order, name='create_order'),
    path('orders_list/', orders_list, name='orders_list'),
    path('backtest/', backtest_view, name='backtest'),
    path('register/', user_register, name='register'),
    path('logout/', user_logout, name='logout'),
    path('home/', home, name='home'),
]
