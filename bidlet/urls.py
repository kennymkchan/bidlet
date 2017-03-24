from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    url(r'^secondary/', TemplateView.as_view(template_name='secondary.html')),
    # url(r'^listings/', TemplateView.as_view(template_name='listings.html')),
    # url(r'^property/', TemplateView.as_view(template_name='property.html')),
    url(r'^api/', include('api.urls')),
]
