"""mgr_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    path('main/', views.main, name='main'),
    path('news/', views.index, name='news'),
    path('about/', views.index, name='about'),
    path('howto/', views.index, name='howto'),
    path('contact/', views.index, name='contact'),
    path('export_csv/', views.export_csv, name='export_csv'),
    
    path('req/<int:num>', views.req, name='req'),
    path('req/new_checkout/', views.new_checkout, name='new_checkout'),
    path('req/clear_checkout/', views.clear_checkout, name='clear_checkout'),
    path('req/increase_limit/', views.increase_limit, name='increase_limit'),
    path('req/reduce_limit/', views.reduce_limit, name='reduce_limit'),
    
    path('details/<int:num>', views.details, name='details'),
    path('details/set_details/', views.set_details, name='set_details'),
    
    path('403/', views.forbidden, name='403'),
]
