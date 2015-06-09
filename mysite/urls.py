from django.conf.urls import patterns, include, url
from django.conf import settings 
from django.conf.urls.static import static  
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^product_test/', include('product_test.urls', namespace = 'product_test')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'product_test/login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page':'/accounts/login'}),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
