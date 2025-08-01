from django.urls import path
from . import views

urlpatterns = [
    path("posts/", views.blog_posts, name='blog_posts'),
    path("categories/", views.categories, name="categories"),
    # DELETING OR UPDATING A POST USING ITS ID.
    path("posts/<int:post_id>/", views.post_router, name="update_or_delete_posts"),
    # DELETING OR UPDATING A CATEGORY.
    path(
        "categories/<int:category_id>/",
        views.category_router,
        name="update_or_delete_categories",
    ),
]
