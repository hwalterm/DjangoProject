from django.db import models
from django.conf import settings
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User
from ipware.ip import get_ip
from blog.utils.utility_funcs import gen_uuid, wsi_confidence

class NamedModel(models.Model):
    class Meta:
        abstract = True

    def getName(self):
        return self.__class__.__name__
from ProblemPages.models import Problems


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    page = models.ForeignKey(Problems, on_delete = models.CASCADE, default = 1)

    def __str__(self):
        return self.title


    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('post-detail', args=[str(self.id)])


# class post_comment(MPTTModel,Comment):
#     Post = models.ForeignKey(Post,on_delete = models.CASCADE)
#     parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
#     class MPTTMeta:
#         # comments on one level will be ordered by date of creation
#         order_insertion_by = ['submit_date']
#     class Meta:
#         ordering = ['tree_id', 'lft']


class Comment(MPTTModel, NamedModel):
    Post = models.ForeignKey(Post, on_delete=models.CASCADE)
    uid = models.UUIDField(max_length=8, primary_key=True, default=gen_uuid, editable=False)
    content = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='+')
    created_on = models.DateTimeField(auto_now_add=True, auto_now=False)
    modified_on = models.DateTimeField(auto_now_add=False, auto_now=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE)
    _upvotes = models.IntegerField(blank=True, default=0)
    _downvotes = models.IntegerField(blank=True, default=0)
    wsi = models.FloatField(blank=True, default=0) # Wilson score interval
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=150, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)
        Post.upvotes = property(lambda self: self._upvotes, Comment._voteSetterWrapper('_upvotes'))
        Post.downvotes = property(lambda self: self._downvotes, Comment._voteSetterWrapper('_downvotes'))

    class MPTTMetta:
        order_insertion_by = ['created_on']

    def __str__(self):
        return self.content[:70]

    @staticmethod
    def _voteSetterWrapper(attr):
        def voteSetter(self, value):
            setattr(self, attr, max(0, value))
            self.wsi = wsi_confidence(self._upvotes, self._downvotes)
        return voteSetter

    @property
    def score(self):
        return self.upvotes - self.downvotes

    def getReplies(self, excluded=()):
        """:param excluded: exclude all posts with these uids and their descendants"""
        replies = Comment.objects.filter(parent=self.uid).exclude(uid__in=excluded)
        for reply in replies:
            replies |= reply.getReplies(excluded=excluded)
        return replies

    def getSortedReplies(self, limit=50, by_wsi=True, excluded=()):
        """
        :param limit: number of replies to return
        :param by_wsi: sort replies by wsi score or by creation date
        :param excluded: uids or excluded replies
        """
        excluded = list(excluded)
        order_field = '-wsi' if by_wsi else 'created_on'
        replies = list(self.getReplies(excluded=excluded).order_by(order_field)[:limit])
        self._getCommentsWithChildren(replies)
        sorted_replies = []
        for p in replies:
            sorted_replies.append(p)
            sorted_replies += p.getChildrenList()
        return sorted_replies

    def _getCommentsWithChildren(self, replies):
        for p in list(replies):
            if not hasattr(p, 'included_children'):
                p.included_children = []
            if p.parent != self:
                if p.parent not in replies:
                    # add missing parents
                    current_p = p
                    while True:
                        current_p.parent._addToIncludedChildren(current_p)
                        current_p = current_p.parent
                        if current_p in (replies + [self]):
                            break
                    if current_p in replies:
                        replies[replies.index(current_p)] = current_p
                else:
                    p.parent = replies[replies.index(p.parent)]
                    p.parent._addToIncludedChildren(p)
                replies.remove(p)

    def _addToIncludedChildren(self, post):
        if not hasattr(self, 'included_children'):
            self.included_children = [post]
        else:
            self.included_children.append(post)

    def getChildrenList(self):
        children = []
        for p in self.included_children:
            children.append(p)
            if p.included_children:
                children += p.getChildrenList()
        return children

    def setMeta(self, request):
        """update comment ip_address & user_agent attributes"""
        ip = get_ip(request)
        if ip is not None:
            self.ip_address = ip
        ua = request.META.get('HTTP_USER_AGENT', '')
        if ua:
            self.user_agent = ua
