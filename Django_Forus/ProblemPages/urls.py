from django.urls import path
from .views import ProblemView, CreatePageView
urlpatterns = [

    path('main/<int:id>/', ProblemView, name ='problem-page'),
    path('create/<int:id>/', CreatePageView, name ='problem-create-page'),
]
