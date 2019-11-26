from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def communityHome(request):
    return HttpResponse('Community Home')
def communityDetailView(request,name):
    context = {'comName':name}
    template = 'communities/communitydetail.html'
    return render(request,template,context,)