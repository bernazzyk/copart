"""copart URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt

from copart import settings
from product import views


urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),

    url(r'^', admin.site.urls),

    url(r'^rosetta/', include('rosetta.urls')),

    url(r'^scrap_copart/', views.scrap_copart),
    url(r'^scrap_copart_all/', views.scrap_copart_all),
    url(r'^scrap_iaai/', views.scrap_iaai),
    url(r'^scrap_auction/', views.scrap_auction),

    url(r'^ajax_getimages/', csrf_exempt(views.ajax_getimages), name='ajax_getimages'),

    path('i18n/', include('django.conf.urls.i18n')),
    path('language/<language>/', views.switch_language),

    url(r'^test/', views.task_test),

    # url(r'^silk/', include('silk.urls', namespace='silk')),
    # url(r'^statuscheck/', include('celerybeat_status.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
