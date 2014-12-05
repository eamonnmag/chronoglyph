from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'ChronoGlyph_Web.views.analytics', name='home'),
    url(r'^analysis$', 'ChronoGlyph_Web.views.create_analysis', name='run_analysis'),
    url(r'^delete_analysis/(.+)$', 'ChronoGlyph_Web.views.delete_analysis', name='run_analysis'),
    url(r'^get_file$', 'ChronoGlyph_Web.views.get_analysis_file', name='run_analysis'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^datasets$', 'ChronoGlyph_Web.views.datasets', name='home'),
    url(r'^admin/', include(admin.site.urls)),
)
