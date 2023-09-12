from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from NewsPaper.models import Post
from NewsPaper.forms import FormCreatePost, FormSearchPost
from NewsPaper.filters import PostFilter


######################################################################################################################


def index(request):
    """
    Главная страница
    :param request:
    :return:
    """
    return redirect(reverse('post_list'))


######################################################################################################################


class PostCreateView(LoginRequiredMixin, CreateView):
    """
    Класс создания записи
    """
    template_name = 'post/create.html'
    form_class = FormCreatePost

    def form_valid(self, form):
        messages.success(self.request, 'Запись успешно создана.')
        return super(PostCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


######################################################################################################################


class PostDetailView(DetailView):
    """
    Класс просмотра записи
    """
    template_name = 'post/show.html'
    queryset = Post.objects.all()

    def get_object(self, **kwargs):
        post_id = self.kwargs.get('post_id')
        return Post.objects.get(pk=post_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_active'] = True
        return context


######################################################################################################################


class PostEditView(LoginRequiredMixin, UpdateView):
    template_name = 'post/edit.html'
    form_class = FormCreatePost

    def form_valid(self, form):
        messages.success(self.request, 'Запись успешно отредактирована.')
        return super(PostEditView, self).form_valid(form)

    def get_object(self, **kwargs):
        post_id = self.kwargs.get('post_id')
        return Post.objects.get(pk=post_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_active'] = True
        return context


######################################################################################################################


class PostDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'post/delete.html'
    queryset = Post.objects.all()
    success_url = reverse_lazy('post_list')

    def get_object(self, **kwargs):
        post_id = self.kwargs.get('post_id')
        return Post.objects.get(pk=post_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_active'] = True
        return context


######################################################################################################################


class PostList(ListView):
    model = Post
    template_name = 'post/list.html'
    context_object_name = 'list_post'
    ordering = ['-create_date']
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_active'] = True
        return context


######################################################################################################################


def search_post(request):
    if request.POST:
        form_search = FormSearchPost(request.POST)
        search_query = form_search['search'].value()
        ordering = form_search['ordering'].value()
        list_search_id = list(
            set(
                list(Post.objects.filter(title__icontains=search_query).values_list('id', flat=True)) +
                list(Post.objects.filter(text__icontains=search_query).values_list('id', flat=True))
            )
        )
        count_search_total = len(list_search_id)
        list_search_result = Post.objects.filter(id__in=list_search_id).order_by(ordering)[:10]
        count_search_view = len(list_search_result)
        if count_search_total > 0:
            message_text = f'При поиске "{search_query}" найдено записей - {count_search_total}, отображается {count_search_view}.'
        else:
            message_text = f'При поиске "{search_query}" не найдено ни одного совпадения'
        messages.info(request, message_text)
    else:
        search_query = ''
        list_search_result = []
        form_search = FormSearchPost()
    context = {
        'title': 'Результаты поиска',
        'list_post': list_search_result,
        'search': search_query,
        'form_search': form_search,
    }
    return render(request=request, template_name='post/search.html', context=context)


######################################################################################################################
