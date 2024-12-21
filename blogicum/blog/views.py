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

def filter_published_posts(queryset):
    return queryset.filter(is_published=True, pub_date__lte=now(), category__is_published=True)

class UserPostsListView(MainPostListView):
    template_name = "blog/profile.html"
    author = None

    def get_queryset(self):
        username = self.kwargs["username"]
        self.author = get_object_or_404(User, username=username)
        if self.author == self.request.user:
            queryset = post_all_query().filter(author=self.author)
        else:
            queryset = filter_published_posts(super().get_queryset().filter(author=self.author))
        queryset = annotate_posts_with_comment_count(queryset)
        return sort_posts_by_pub_date(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.author
        context['page_obj'] = paginate_queryset(self.request, self.get_queryset(), self.paginate_by)
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"
    post_data = None
    def get_queryset(self):
        self.post_data = get_object_or_404(Post, pk=self.kwargs["pk"])
        if self.post_data.author == self.request.user:
            return post_all_query().filter(pk=self.kwargs["pk"])
        return post_published_query().filter(pk=self.kwargs["pk"])
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.check_post_data():
            context["flag"] = True
            context["form"] = CommentEditForm()
        context["comments"] = self.object.comments.all().select_related(
            "author"
        )
        return context
    def check_post_data(self):
        return all(
            (
                self.post_data.is_published,
                self.post_data.pub_date <= now(),
                self.post_data.category.is_published,
            )
        )
class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = "blog/user.html"
    def get_object(self, queryset=None):
        return self.request.user
    def get_success_url(self):
        username = self.request.user
        return reverse("blog:profile", kwargs={"username": username})
        
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostEditForm
    template_name = "blog/create.html"
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    def get_success_url(self):
        username = self.request.user
        return reverse("blog:profile", kwargs={"username": username})
        
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostEditForm
    template_name = "blog/create.html"
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)
    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse("blog:post_detail", kwargs={"pk": pk})
        
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/create.html"
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostEditForm(instance=self.object)
        return context
    def get_success_url(self):
        username = self.request.user
        return reverse_lazy("blog:profile", kwargs={"username": username})
        
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentEditForm
    template_name = "blog/comment.html"
    post_data = None
    def dispatch(self, request, *args, **kwargs):
        self.post_data = get_object_or_404(Post, pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_data
        if self.post_data.author != self.request.user:
            self.send_author_email()
        return super().form_valid(form)
    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse("blog:post_detail", kwargs={"pk": pk})
    def send_author_email(self):
        post_url = self.request.build_absolute_uri(self.get_success_url())
        recipient_email = self.post_data.author.email
        subject = "New comment"
        message = (
            f"Пользователь {self.request.user} добавил "
            f"комментарий к посту {self.post_data.title}.\n"
            f"Читать комментарий {post_url}"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email="from@example.com",
            recipient_list=[recipient_email],
            fail_silently=True,
        )
        
class CommentUpdateView(CommentMixinView, UpdateView):
    form_class = CommentEditForm
