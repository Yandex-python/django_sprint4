from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
    CreateView,
    DeleteView,
)
from django.db.models import Count
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from core.utils import post_all_query, post_published_query
from core.mixins import CommentMixinView
from .models import Post, User, Category, Comment
from .forms import UserEditForm, PostEditForm, CommentEditForm

def annotate_posts_with_comment_count(queryset):
    return queryset.annotate(comment_count=Count('comments'))

def sort_posts_by_pub_date(queryset):
    return queryset.order_by('-pub_date')

def paginate_queryset(request, queryset, items_per_page):
    paginator = Paginator(queryset, items_per_page)
    page = request.GET.get('page')
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)
    return paginated_queryset

class MainPostListView(ListView):
    model = Post
    template_name = "blog/index.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = post_published_query()
        queryset = annotate_posts_with_comment_count(queryset)
        return sort_posts_by_pub_date(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = paginate_queryset(self.request, self.get_queryset(), self.paginate_by)
        return context

class CategoryPostListView(MainPostListView):
    template_name = "blog/category.html"
    category = None

    def get_queryset(self):
        slug = self.kwargs["category_slug"]
        self.category = get_object_or_404(
            Category, slug=slug, is_published=True
        )
        queryset = super().get_queryset().filter(category=self.category)
        queryset = annotate_posts_with_comment_count(queryset)
        return sort_posts_by_pub_date(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context['page_obj'] = paginate_queryset(self.request, self.get_queryset(), self.paginate_by)
        return context

class UserPostsListView(MainPostListView):
    template_name = "blog/profile.html"
    author = None

    def get_queryset(self):
        username = self.kwargs["username"]
        self.author = get_object_or_404(User, username=username)
        if self.author == self.request.user:
            queryset = post_all_query().filter(author=self.author)
        else:
            queryset = super().get_queryset().filter(author=self.author)
        queryset = annotate_posts_with_comment_count(queryset)
        return sort_posts_by_pub_date(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.author
        context['page_obj'] = paginate_queryset(self.request, self.get_queryset(), self.paginate_by)
        return context
