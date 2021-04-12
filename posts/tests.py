import time
import tempfile

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from PIL import Image

from .models import Group, Post, Follow

User = get_user_model()


class PostTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.anonymous_client = Client()
        self.user = User.objects.create_user(
                        username="test_user",
                        email="test_user@gmail.com",
                        password="1a2b3c4e5d"
        )
        self.client.force_login(self.user)
        self.cache_delay = 1

        self.post_text = "Test post"
        self.initial_text = "Initial"
        self.edited_text = "Edited"
        self.post_id = "12345"
        self.group = Group.objects.create(
            title="test_group", slug="test_group"
        )

    def test_profile(self):
        print("Testing profile creation...", end="\n\n")
        response = self.client.get(reverse("profile", args=(self.user,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["paginator"].count, 0)

    def test_post_publishing(self):
        print("Testing post creation...", end="\n\n")
        self.client.post(
            reverse("new_post"), data={
                "text": self.post_text,
                "author": self.user,
            }, follow=True
        )

        time.sleep(self.cache_delay)
        response = self.client.get(reverse("profile", args=(self.user,)))
        post_text = response.context["page"][0].text
        retrieved_post = Post.objects.get(id='1')

        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(retrieved_post.text, self.post_text)
        self.assertEqual(retrieved_post.author, self.user)
        self.assertEqual(post_text, self.post_text)
        self.assertEqual(len(response.context["page"]), 1)
        self.assertIsInstance(response.context["author"], User)

    def test_post_presence(self):
        print("Testing post presence at pages...", end="\n\n")
        self.client.post(
            reverse("new_post"), data={
                "text": self.post_text,
                "author": self.user,
                "group": self.group.id
            }, follow=True
        )

        time.sleep(self.cache_delay)
        self.run_request_sequence(self.post_text)

    def test_anonymous_post(self):
        print("Testing anonymous user posting attempt...", end="\n\n")
        login_path = "/auth/login/?next=/new/"
        response = self.anonymous_client.post(
            reverse("new_post"), data={
                "text": "anonymous text"
            }, follow=True
        )
        self.assertRedirects(response, login_path)
        self.assertEqual(Post.objects.count(), 0)

    def test_post_editing(self):
        print("Testing post editing...", end="\n\n")
        post = Post.objects.create(
            text=self.initial_text, author=self.user,
            group=self.group, id=self.post_id
        )

        self.client.post(
            reverse(
                "post_edit", kwargs={
                    "username": self.user.username,
                    "post_id": self.post_id
                }
            ), data={
                "group": self.group.id,
                "text": self.edited_text
            }, follow=True
        )

        post = Post.objects.get(id=self.post_id)
        self.assertEqual(post.text, self.edited_text)
        time.sleep(self.cache_delay)
        self.run_request_sequence(
            self.edited_text,
            self.initial_text,
            self.post_id
        )

    def test_image_publishing(self):
        print("Testing image publishing...", end="\n\n")
        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)

        with open(tmp_file.name, 'rb') as img:
            self.client.post(
                reverse("new_post"), data={
                    "text": self.post_text,
                    "author": self.user,
                    "group": self.group.id,
                    "image": img
                }, follow=True
            )

        tag = "<img"
        time.sleep(self.cache_delay)
        self.run_request_sequence(self.post_text, tag=tag)

    def test_nonimage_protection(self):
        print("Testing non-image protection...", end="\n\n")
        tmp_file = tempfile.NamedTemporaryFile(suffix='.txt')
        with open(tmp_file.name, 'rb') as img:
            self.client.post(
                reverse("new_post"), data={
                    "text": self.post_text,
                    "author": self.user,
                    "group": self.group.id,
                    "image": img
                }, follow=True
            )

        response = self.client.get(reverse("post", args=(self.user, '1',)))
        self.assertEqual(response.status_code, 404)

    def test_cache_delay(self):
        print("Testing cache delay...", end="\n\n")
        self.client.get(reverse("index"))
        self.client.post(
            reverse("new_post"), data={
                "text": self.post_text,
                "author": self.user,
            }, follow=True
        )

        response = self.client.get(reverse("index"))
        self.assertNotContains(response, self.post_text)
        time.sleep(self.cache_delay)
        response = self.client.get(reverse("index"))
        self.assertContains(response, self.post_text)

    def test_subscribing(self):
        print("Testing subscribing...", end="\n\n")
        subscriber = User.objects.create_user(
                        username="subsriber",
                        email="subsriber@gmail.com",
                        password="1a2b3c4e5d"
        )
        self.client.force_login(subscriber)

        self.client.get(reverse("profile_follow",
                        kwargs={"username": self.user.username}))
        self.assertEqual(Follow.objects.count(), 1)

    def test_unsubscribing(self):
        print("Testing subscribing...", end="\n\n")
        subscriber = User.objects.create_user(
                        username="subsriber",
                        email="subsriber@gmail.com",
                        password="1a2b3c4e5d"
        )
        self.client.force_login(subscriber)

        self.client.get(reverse("profile_unfollow",
                        kwargs={"username": self.user.username}))
        self.assertEqual(Follow.objects.count(), 0)

    def test_subscription_update(self):
        print("Testing subscription update...", end="\n\n")
        self.client.post(
            reverse("new_post"), data={
                "text": self.post_text,
                "author": self.user,
            }, follow=True
        )
        subscriber = User.objects.create_user(
                        username="subsriber",
                        email="subsriber@gmail.com",
                        password="1a2b3c4e5d"
        )
        non_subscriber = User.objects.create_user(
                        username="non_subscriber",
                        email="non_subscriber@gmail.com",
                        password="1a2b3c4e5d"
        )

        self.client.force_login(subscriber)
        self.client.get(reverse("profile_follow",
                        kwargs={"username": self.user.username}))
        response = self.client.get(reverse("follow_index"))
        self.assertContains(response, self.post_text)

        self.client.force_login(non_subscriber)
        response = self.client.get(reverse("follow_index"))
        self.assertNotContains(response, self.post_text)

    def test_comments(self):
        print("Testing comments...", end="\n\n")
        self.client.post(
            reverse("new_post"), data={
                "text": self.post_text,
                "author": self.user,
            }, follow=True
        )

        commentator = User.objects.create_user(
                        username="commentator",
                        email="subsriber@gmail.com",
                        password="1a2b3c4e5d"
        )
        self.client.force_login(commentator)
        self.client.post(
            reverse(
                "add_comment", kwargs={
                    "username": self.user.username,
                    "post_id": "1"
                }
            ), data={
                "text": "Test comment"
            }, follow=True
        )
        response = self.client.get(reverse("post", args=(self.user, "1")))
        self.assertContains(response, "Test comment")

        self.anonymous_client.post(
            reverse(
                "add_comment", kwargs={
                    "username": self.user.username,
                    "post_id": "1"
                }
            ), data={
                "text": "Anonymous comment"
            }, follow=True
        )
        response = self.client.get(reverse("post", args=(self.user, "1")))
        self.assertNotContains(response, "Anonymous comment")

    def run_request_sequence(self,
                             text_1,
                             text_2=None,
                             post_id='1',
                             tag="<main>"):
        request_list = [
            reverse("index"),
            reverse("group_posts", args=(self.group,)),
            reverse("profile", args=(self.user,)),
            reverse("post", args=(self.user, post_id,))
        ]

        for item in request_list:
            response = self.client.get(item)
            self.assertContains(response, text_1)
            self.assertContains(response, tag)
            self.assertNotContains(response, text_2)
            try:
                self.assertEqual(response.context["paginator"].count, 1)
            except KeyError:
                pass


class ErrorTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_404(self):
        print("Testing 404 error...", end="\n\n")
        response = self.client.get("/abracadabra/", follow=True)
        self.assertEqual(response.status_code, 404)
