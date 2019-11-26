from django.db import models
from ProblemPages.models import Problems
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User
from ProblemPages.models import Problems

class community(MPTTModel):
    name = models.CharField(max_length = 50, unique = True)
    parent=TreeForeignKey('self', on_delete = models.CASCADE, null=True, blank = True, related_name = 'children')
    date_posted = models.DateTimeField(default=timezone.now)
    community_admins = models.ManyToManyField(User,related_name='community_admins_set')
    community_members = models.ManyToManyField(User,related_name='community_members_set')
    related_issues = models.ManyToManyField(Problems)
    description = models.CharField(max_length = 100, unique = False, null=True)

    class MPTTMeta:
        order_insertion_by = ['date_posted']

    def __str__(self):
        return self.name
