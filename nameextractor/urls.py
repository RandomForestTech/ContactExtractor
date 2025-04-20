from django.urls import path
from django.contrib.auth import views as auth_views
from nameextractor import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.upload_view, name='upload'),
    path('filter_people/', views.filter_people_view, name='filter_people'),

]