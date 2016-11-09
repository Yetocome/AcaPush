"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from mysite.views import commit_comment
from mysite.views import fetch_comments
from mysite.views import login
from mysite.views import fetch_news
from mysite.views import fetch_notice
from mysite.views import fetch_news
from mysite.views import search

urlpatterns = [
	 url(r'^admin/$', admin.site.urls),
	 url(r'^comments/commit/(\d{8})/(\d{13})$', commit_comment, name='commit_comment'), #upload the comments to the server
         url(r'^comments/(\d{8})/$', fetch_comments, name='fetch_comments'), #return the news of different academy
         url(r'^login/$',login,name='login'),
	 url(r'^news/(\d{2})/(\d{8})/$', fetch_news, name='fetch_news'), #return the news of different academy before the date(00 or 00000000 will return all)
	 url(r'^notice/(\d{2})/(\d{8})/$', fetch_notice, name='fetch_notice'), #return the notice of different academy before the date(00 or 00000000 will return all)	   
	 url(r'^search_news/(\w{1,15})/(\d{2})/(\d{8})/$', search_news, name='search_news'), #search the news or notice with keyword（w{1,15}) (00 or 00000000 will return all academy and date news)
         url(r'^search_notice/(\w{1,15})/(\d{2})/(\d{8})/$', search_notice, name='search_notice'),
]

