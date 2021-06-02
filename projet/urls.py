"""projet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LoginView, logout_then_login
from communitymanager import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('communitymanager/', include('communitymanager.urls')),
    path('connexion/', LoginView.as_view(template_name='registration/login.html'), name="login"),
    path('deconnexion/', logout_then_login, name="logout"),
    path('signup/', views.signup, name='signup'),
    path('', views.communautes, name='global_home'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
