from django.test import TestCase
from django.test import TestCase, Client
from django.urls import reverse
from blog.models import Post, Category
import json


class BlogAPITests(TestCase):

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="TestCategory")
        self.post = Post.objects.create(title="Test Post", text="Test Content")
        self.post.categories.add(self.category)

    def test_list_posts(self):
        url = reverse('blog_posts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('posts', data)
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['posts'][0]['title'], 'Test Post')

    def test_create_post_unauthorized(self):
        url = reverse('blog_posts')
        payload = {
            "title": "New Post",
            "text": "Some text",
            "categories": [self.category.id]
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_create_post_authorized(self):
        url = reverse('blog_posts')
        payload = {
            "title": "New Post",
            "text": "Some text",
            "categories": [self.category.id]
        }
        headers = {'HTTP_AUTH_API_KEY': 'aqaq1212'} 
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json', **headers)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn('post_id', data)
