"""
URL configuration for productmeta_backend project.

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
from api.views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/get-sources/', get_sources),
    path('api/get-attributes/', get_attributes),
    path('api/push-mapping/', push_custom_mapping),
    path('api/get-constraint/', get_constraint),
    path('api/generate-results/', generate_results),
    path('api/generate-pic/', generate_pic),

    path('api/test_post/', test_post),
    path('api/test_get/', test_get)
]
