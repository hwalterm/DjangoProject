from django.shortcuts import render, redirect
from .models import Post, Comment
from django.views.generic import (
    ListView, DetailView,
    CreateView, UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from blog.forms import CreatePost, CommentForm, postcomment
from django.contrib import messages
from ProblemPages.models import Problems
#from django_comments.forms import CommentForm
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from meta.views import Meta
from djeddit.utils.utility_funcs import is_authenticated


def home(request):
    form = CreatePost(initial={'author': request.user})
    context = {'posts': Post.objects.all().order_by('-date_posted'),
               'form': form,
               'problemlist': Problems.objects.get(name="Home").get_children(),
               'problemtitle': 'Open Problems'
               }
    if request.method == 'POST':
        post_form=CreatePost(request.POST)

        if post_form.is_valid():
            post_form.save()
            messages.success(request, 'post successful')
            context = {'posts': Post.objects.all().order_by('-date_posted'),
                       'form': CreatePost(initial={'author': request.user}),
                       'problemlist': Problems.objects.get(name="Home").get_children(),

                       }
            return render(request, 'blog/home.html', context)

    return render(request, 'blog/home.html', context)
# def home(request):
#     context = {
#         'posts': Post.objects.all()
#     }
#     return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']




def PostDetailView(request, id):
    post = Post.objects.get(pk=id)
    threads = Comment.objects.filter(Post = id)
    description = ''
    meta = Meta(
                    title='',
                    use_title_tag=True,
                    description=description,
                )
    #thread.views += 1
    #thread.save()
    context = {'threads':threads, 'nodes':threads, 'post':post}
    return render(request, 'blog/post_detail.html', context)

# def PostDetailView(request, id):
#     context = {'object':Post.objects.get(pk=id),
#                'post':Post.objects.get(pk=id)}
#     if request.method == 'POST':
#         commentform = CommentForm(request.POST)
#
#         if commentform.is_valid():
#             commentform.save()
#             messages.success(request, 'post successful')
#             return render(request, 'blog/post_details.html', context)
#         messages.error(request, 'sometin went wrong')
#     return render(request, 'blog/post_details.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})


def replyPost(request, post):
    if request.method == 'POST':
        post_form=postcomment(request.POST)

        if post_form.is_valid():
            post_form.save()
            messages.success(request, 'post successful')


    else:
        post_form = postcomment
    context = {'post': post,
                'form': post_form,
                'problemlist': Problems.objects.get(name="Home").get_children(),
               }
    return render(request, 'blog/post_reply_form.html', context)


def replyComment(request, post_uid=''):
    try:
        repliedComment = Comment.objects.get(id=post_uid)
        thread = repliedComment.post
    except (Post.DoesNotExist):
        raise Http404
    repliedUser = repliedComment.created_by.username if repliedComment.created_by else 'guest'
    if request.method == 'POST':
        commentForm = CommentForm(request.POST)
        if commentForm.is_valid():
            comment = commentForm.save(commit=False)
            comment.parent = None
            comment.Post = repliedComment
            comment.setMeta(request)

            if is_authenticated(request):
                comment.created_by = request.user
            comment.save()
            repliedComment.children.add(comment)
        return HttpResponseRedirect(thread.relativeUrl)
    else:
        postForm = CommentForm()
        postForm.fields['content'].label = ''
        context = dict(postForm=postForm, thread_id=thread.id, post_uid=post_uid, repliedUser=repliedUser)
        return render(request, 'djeddit/reply_form.html', context)