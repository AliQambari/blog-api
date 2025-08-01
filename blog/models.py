from django.db import models
from django.core.exceptions import ValidationError


# Category class: to create unique categories of the blog posts.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    # This is used for easy print
    def __str__(self):
        return self.name


# Post class: to create blog posts.
class Post(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField("Category")

    def clean(self):
        if self.pk and self.categories.count() > 6:
            raise ValidationError("At most 6 categories can be added to a post.")

    def __str__(self):
        return self.title
