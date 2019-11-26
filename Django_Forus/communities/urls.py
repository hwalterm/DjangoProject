from django.urls import path
from .views import communityHome,communityDetailView
urlpatterns = [

    path('home/', communityHome, name='community-Home'),
    path('<name>',communityDetailView, name = 'communityDetail')

]
