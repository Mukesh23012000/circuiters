"""
URL configuration for circuiters project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from apps import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name="index"),
    path('login',views.login,name="login"),
    path('logout',views.logout,name='logout'),
    path('signup',views.signup,name="signup"),
    path('index',views.index),
    path('info',views.info),
    path('admin',views.admin,name="admin"),
    path('contactmessages/<int:length>',views.cmsg),
    path('user/<int:id>/<int:length>', views.urec),
    path('adminusers/<int:length>',views.adminusers),
    path('useroders/<int:id>/<int:length>',views.useroders),
    path('accept/<int:id>/<int:uid>',views.accept),
    path('received/<int:id>/<int:uid>',views.received),
    path('reject/<int:id>/<int:uid>',views.reject),
    path('returned/<int:id>/<int:uid>',views.returned),
    path('com/<int:id>/<int:uid>',views.com),
    path('uedit/<int:id>',views.uedit),
    path('confirm/<str:mail>/<str:msg>',views.confirm),
]
