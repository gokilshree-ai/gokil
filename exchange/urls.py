from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('marketplace/', views.marketplace_view, name='marketplace'),
    path('add-skill/', views.add_skill_view, name='add_skill'),
    path('book/<int:skill_id>/', views.book_session_view, name='book_session'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('skill/edit/<int:skill_id>/', views.edit_skill_view, name='edit_skill'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('booking/confirm/<int:booking_id>/', views.confirm_booking_view, name='confirm_booking'),
    path('booking/decline/<int:booking_id>/', views.decline_booking_view, name='decline_booking'),
]
