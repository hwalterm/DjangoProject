from django.urls import path, include
from django.conf.urls import url
from .views import (
    PostListView, PostDetailView, PostCreateView,PostDeleteView, PostUpdateView, home)
from . import views
urlpatterns = [

    path('', home, name ='blog-home'),
    path('post/<int:id>/', PostDetailView, name ='post-detail'),
    path('about/', views.about, name = 'blog-about'),
    path('post/new/',PostCreateView.as_view(success_url="/blog/"), name = 'post-create'),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name = 'post-delete'),
    path('post/<int:pk>/delete', PostUpdateView.as_view(), name = 'post-update'),
    path('post/reply/<int:uid>', views.replyPost, name='replyPost'),
    url(r'^reply_post/([\w\-]{36})?/?$', views.replyPost, name='replyPost'),

]