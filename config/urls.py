"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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

from main import views

from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/sign',  views.SignHandler().handle),
    
    path('api/account', views.AccountHandler().handle),
    
    path('api/upload', views.UploadHandler().handle),
    
    path('api/notice', views.NoticeHandler().handle),
    
    path('api/news', views.NewsHandler().handle),
    
    path('api/paper', views.PaperHandler().handle),
    
    path('api/config', views.ConfigHandler().handle),
    
    path('api/etc', views.ProfileHandler().handle),
    
    path('api/wf_graduatedesign', views.GraduateDesignHandler().handle),
    
] 

# + static("/", document_root="./z_dist")
