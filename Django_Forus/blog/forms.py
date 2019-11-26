from django import forms
from .models import Post
from .models import Comment
from django_comments.forms import CommentForm


class CreatePost(forms.ModelForm):

    class Meta:
        model = Post
        fields =['title','content','author','page']
        widgets = {'author': forms.HiddenInput(),
                   'page' :forms.HiddenInput(),
                   'content' : forms.Textarea(attrs={'rows':4})
                   }
    # def form_valid(self, form):
    #     form.instance.author= self.request.user.id
    #     return super().form_valid(form)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
class postcomment(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content','Post','created_by', 'author', 'page','content']
        # widgets = {'author': forms.HiddenInput(),
        #            'page': forms.HiddenInput(),
        #            'content': forms.Textarea(attrs={'rows': 4})
        #            }
