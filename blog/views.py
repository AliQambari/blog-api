from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, Category
import json
from django.views.decorators.csrf import csrf_exempt


# -------------------CREATING BLOG POSTS----------------------
@csrf_exempt
def create_blog_post(request):
    if request.method != "POST":
        return JsonResponse({"error": "Bad Request"}, status=405)

    # Manual authentication as requested
    api_key = request.headers.get("Auth-API-KEY")
    if api_key != "aqaq1212":
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Getting the data that is given by the user.
    title = data.get("title")
    text = data.get("text")
    category_ids = data.get("categories", [])

    if not title or not text:
        return JsonResponse({"error": "Title and text are required"}, status=400)

    if len(category_ids) > 6:
        return JsonResponse(
            {"error": "At most 6 categories can be added to a post."}, status=400
        )

    categories = Category.objects.filter(id__in=category_ids)
    if categories.count() != len(category_ids):
        return JsonResponse({"error": "Some category IDs are invalid"}, status=400)

    # Creating a post
    post = Post(title=title, text=text)
    post.save()
    post.categories.set(categories)

    return JsonResponse({"message": "Post created.", "post_id": post.id}, status=201)


# -----------------LISTING BLOG POST------------------------


def list_blog_posts(request):

    posts = Post.objects.all().order_by("-updated_at")
    page = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 5)

    try:
        page_size = int(page_size)
    except ValueError:
        page_size = 5

    paginator = Paginator(posts, page_size)

    try:
        posts_page = paginator.page(page)
    except PageNotAnInteger:
        posts_page = paginator.page(1)
    except EmptyPage:
        posts_page = paginator.page(paginator.num_pages)

    list_of_available_posts = []
    for post in posts_page:
        list_of_available_posts.append(
            {
                "id": post.id,
                "title": post.title,
                "text": post.text,
                "created_at": post.created_at.isoformat(),
                "updated_at": post.updated_at.isoformat(),
                "categories": [category.name for category in post.categories.all()],
            }
        )

    response = {
        "count": paginator.count,
        "num_pages": paginator.num_pages,
        "current_page": posts_page.number,
        "posts": list_of_available_posts,
    }
    return JsonResponse(response)


# ------- Handeling the same view for Fetching blog posts or posting a new content -------
@csrf_exempt
def blog_posts(request):
    if request.method == "GET":
        return list_blog_posts(request)
    elif request.method == "POST":
        return create_blog_post(request)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


# -------------------------UPDATING BLOG POSTS---------------------------
# UPDATE USES only PATCH method.


@csrf_exempt
def patch_post(request, post_id):
    if request.method != "PATCH":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    api_key = request.headers.get("Auth-API-KEY")
    if api_key != "aqaq1212":
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    title = data.get("title")
    text = data.get("text")
    category_ids = data.get("categories")

    if title:
        post.title = title
    if text:
        post.text = text
    if category_ids is not None:
        if len(category_ids) > 6:
            return JsonResponse({"error": "At most 6 categories allowed"}, status=400)
        categories = Category.objects.filter(id__in=category_ids)
        if categories.count() != len(category_ids):
            return JsonResponse({"error": "Some category IDs are invalid"}, status=400)
        post.categories.set(categories)

    post.save()

    return JsonResponse({"message": "Post updated successfully"})


# -------------------------DELETING BLOG POSTS---------------------------
@csrf_exempt
def delete_post(request, post_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    api_key = request.headers.get("Auth-API-KEY")
    if api_key != "aqaq1212":
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        post = Post.objects.get(id=post_id)
        post.delete()
        return JsonResponse({"message": "Post deleted"})
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)


# -------Handeling the same view for updating blog posts or deleting them------


@csrf_exempt
def post_router(request, post_id):
    if request.method == "PATCH":
        return patch_post(request, post_id)
    elif request.method == "DELETE":
        return delete_post(request, post_id)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


# ------------------------creating categories-------------------------


@csrf_exempt
def categories(request):
    if request.method == "GET":
        categories = Category.objects.all()
        data = [{"id": category.id, "name": category.name} for category in categories]
        return JsonResponse({"categories": data})

    elif request.method == "POST":
        api_key = request.headers.get("Auth-API-KEY")
        if api_key != "aqaq1212":
            return JsonResponse({"error": "Unauthorized"}, status=401)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        name = data.get("name")
        if not name:
            return JsonResponse({"error": "Name is required"}, status=400)

        if Category.objects.filter(name=name).exists():
            return JsonResponse({"error": "Category name must be unique"}, status=400)

        category = Category(name=name)
        category.save()

        return JsonResponse(
            {"message": "Category created", "id": category.id}, status=201
        )
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


# -----------------------------editing categories----------------------


# @csrf_exempt
def patch_category(request, category_id):
    if request.method != "PATCH":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    api_key = request.headers.get("Auth-API-KEY")
    if api_key != "aqaq1212":
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return JsonResponse({"error": "Category not found"}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    name = data.get("name")
    if not name:
        return JsonResponse({"error": "Name is required"}, status=400)

    if Category.objects.filter(name=name).exclude(id=category_id).exists():
        duplicates = Category.objects.filter(name=name).exclude(id=category_id)
        duplicate_id = [cat.id for cat in duplicates]

        return JsonResponse(
            {"error": "Category name must be unique", "duplicate ID": duplicate_id},
            status=400,
        )

    category.name = name
    category.save()

    return JsonResponse({"message": "Category updated"})


# -----------------------------deleting categories----------------------
@csrf_exempt
def delete_category(request, category_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    api_key = request.headers.get("Auth-API-KEY")
    if api_key != "aqaq1212":
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        category = Category.objects.get(id=category_id)
        category.delete()
        return JsonResponse({"message": "Category deleted"})
    except Category.DoesNotExist:
        return JsonResponse({"error": "Category not found"}, status=404)


# -------Handeling the same view for updating or deleting categories------


@csrf_exempt
def category_router(request, category_id):
    if request.method == "PATCH":
        return patch_category(request, category_id)
    elif request.method == "DELETE":
        return delete_category(request, category_id)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
