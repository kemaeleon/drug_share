from django.conf.urls import url
from hitlist import views
from django.views import debug

urlpatters = [
url(r'^home$', views.home, name='home'),
url(r'^compoundlist$', views.hit, name='hitlist'),
url(r'^map$', views.old, name='old'),
url(r'^compound_view', views.CompoundTableView.as_view(), name='compound_view'),
        ]
