

from django.shortcuts import render, redirect
from .forms import CreatePage
from blog.models import Post
from .models import Problems
from django.http import HttpResponse
from blog.forms import CreatePost
from django.contrib import messages




def ProblemView(request, id):
    problem = Problems.objects.get(pk=id)
    template = 'ProblemPages/home.html'
    form = CreatePost(initial={'author': request.user,
                               'page': problem
                               })
    context = {'posts': problem.post_set.all().order_by('-date_posted'),
               'form': form,
               'problemtitle': 'Sub Problems',
               'problem':problem,
               'problemlist': problem.get_children(),
               'problemancestors': problem.get_ancestors(),
               'solved':problem.solved


               }
    if request.method == 'POST':
        post_form=post_form=CreatePost(request.POST)

        if post_form.is_valid():
            post_form.save()
            messages.success(request, 'Page Created')
            context = {'posts': problem.post_set.all().order_by('-date_posted'),
                       'form': form,
                       'problemlist': problem.get_children(),
                       'problemancestors': problem.get_ancestors(),
                       'problem': problem,

                       }

        return render(request, template, context)

    return render(request, template, context)

# def home(request):
#     context = {
#         'posts': Post.objects.all()
#     }
#     return render(request, 'blog/home.html', context)

def CreatePageView(request, id):
    problem = Problems.objects.get(pk=id)
    template = 'ProblemPages/createpage.html'
    form = CreatePage(initial={'parent': problem,
                               'admins': request.user
                               })
    context = {
               'form': form,
               'problemlist': problem.get_children(),

               }
    if request.method == 'POST':
        post_form = CreatePage(request.POST)

        if post_form.is_valid():
            post_form.save()
            messages.success(request, 'post successful')
            return redirect("ProblemView", id)
        else:
            messages.error(request, "Something went wrong. Please verify this problem hasn't already been created and try again")
            return render(request, template, context)
    return render(request, template, context)