from django.http import StreamingHttpResponse, request, response
from django.urls import path, include
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from foodshow.views import LiveVideoFaceDetect, ImageFaceDetect
from . import views

app_name = 'foodshow'
urlpatterns = [
    path('how-it-works', views.landing, name='landing'),
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


    path('fullfoodshow', views.fullfoodshow, name='fullfoodshow'),
    path('pushsettings', views.pushsettings, name='pushsettings'),
    path('toggle/', views.toggle, name='toggle'),
    url('^', include('django.contrib.auth.urls')),
    path('shopping', views.shopping, name='shopping'),
    path('seed', views.seed, name='seed'),
    # path('scan_in_progress', views.scan_in_progress, name='scan_in_progress'),


    url(r'^face-detect/image/$', ImageFaceDetect.as_view(), name='image'),
    url(r'^face-detect/video/$', LiveVideoFaceDetect.as_view(), name='live_video'),


    # url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    # url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    # url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     auth_views.password_reset_confirm, name='password_reset_confirm'),
    # url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),

]
