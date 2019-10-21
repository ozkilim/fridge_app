from django.http import StreamingHttpResponse, request, response
from django.urls import path
from urllib3.util import url
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from foodshow.views import gen, VideoCamera

from . import views

app_name = 'foodshow'
urlpatterns = [
    path('landing', views.landing, name='landing'),
    path('', views.index, name='index'),
    path('sort_by_catagory', views.sort_by_catagory, name='sort_by_catagory'),

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),

    path('eaten', views.eaten, name='eaten'),
    path('custom_foods', views.custom_foods, name='custom_foods'),
    path('fridge_manager', views.fridge_manager, name='fridge_manager'),
    path('fridge_filler/<extracted_text>', views.fridge_filler, name='fridge_filler'),
    path('upload_page', views.upload_page, name='upload_page'),
    url('monitor/', lambda r: StreamingHttpResponse(gen(VideoCamera()),
                                                    content_type='multipart/x-mixed-replace; boundary=frame'),
        name='monitor')
]
