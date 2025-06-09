from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from .models import Task
from .forms import TaskForm
from django.views.generic import CreateView

def index_view(request):
    return render(request, 'home.html')

class TaskListView(LoginRequiredMixin,ListView):
    model = Task
    template_name = 'task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

class TaskCreateView(LoginRequiredMixin,CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = '/blog/tasks/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

class TaskUpdateView(LoginRequiredMixin,UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = '/blog/tasks/'

    def get_object(self, queryset=None):
        task = super().get_object(queryset)
        if task.user != self.request.user:
            raise PermissionDenied()
        return task
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

class TaskDeleteView(LoginRequiredMixin,DeleteView):
    model = Task
    template_name = 'task_confirm_delete.html'
    success_url = '/blog/tasks/'

    def get_object(self, queryset=None):
        task = super().get_object(queryset)
        if task.user != self.request.user:
            raise PermissionDenied()
        return task
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

class TaskDoneToggleView(LoginRequiredMixin,View):

    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk, user=request.user)
        task.is_done = not task.is_done
        task.save()
        return redirect('blog:task-list')
