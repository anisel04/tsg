from django.urls import path
from .views import register, home, login_user, profile, create_request
from django.shortcuts import render
from . import views

urlpatterns = [
    path('register/', register, name='register'),
    path('', views.home, name='home'),  # Главная страница
    path('login/', login_user, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/', profile, name='profile'),
    path('create_request/', create_request, name='create_request'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('payments/', views.my_payments, name='payments'),
    path('add-payment/', views.add_payment, name='add_payment'),
    path('create-request/', views.create_request, name='create_request'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('all-requests/', views.all_requests, name='all_requests'),
    path('send-notification/', views.send_notification, name='send_notification'),
    path('notifications/', views.notifications, name='notifications'),
    path('manage-debts/', views.manage_debts, name='manage_debts'),
    path('my-debts/', views.my_debts, name='my_debts'),
    path('noprav/', views.my_debts, name='noprav'),
    path('manage-payments/', views.manage_payments, name='manage_payments'),
    path('send-message/', views.send_message, name='send_message'),
    path('my-messages/', views.my_messages, name='my_messages'),
    path('get-user-requests/<int:user_id>/', views.get_user_requests, name='get_user_requests'),
    path('payment-report/', views.payment_report, name='payment_report'),
    path('request-report/', views.request_report, name='request_report'),
    path('debts-report/', views.debts_report, name='debts_report'),
]
