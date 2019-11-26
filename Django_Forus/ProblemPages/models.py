from django.db import models

from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User
class Problems(MPTTModel):
    name = models.CharField(max_length = 50, unique = True)
    parent=TreeForeignKey('self', on_delete = models.CASCADE, null=True, blank = True, related_name = 'children')
    date_posted = models.DateTimeField(default=timezone.now)
    page_admins = models.ManyToManyField(User)
    description = models.CharField(max_length = 100, unique = False, null=True)
    solved = models.BooleanField(default = False)
    class MPTTMeta:
        order_insertion_by = ['date_posted']

    def __str__(self):
        return self.name

# Create your models here.
