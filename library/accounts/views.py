from django.shortcuts import redirect, render, get_object_or_404, Http404
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.forms import RegistrationForm, ProfileUpdateForm
from .models import Student 
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from datetime import timedelta
from django.contrib.auth.views import LogoutView, PasswordChangeDoneView

def is_superuser(user):
    return user.is_superuser

@login_required
def profile(request):
    url = reverse('home')
    return redirect(url)

class AccountsDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'accounts/account_details.html'
    context_object_name = 'student'

    def get_object(self, queryset=None):
        return get_object_or_404(Student, pk=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):
        try:
            student = self.get_object()
        except Http404:
            return redirect('students.data')
        
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        student = self.get_object()
        form = ProfileUpdateForm(request.POST, instance=student)

        if form.is_valid():
            form.save()
            return redirect('accounts.profile', pk=student.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))
class AccountCreateView(CreateView):
    model = Student
    template_name = 'accounts/create.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        return response
    


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = ProfileUpdateForm
    template_name = 'accounts/edit_profile.html'

    def get_object(self):
        return self.request.user 

    def get_success_url(self):
        return reverse_lazy('accounts.profile', kwargs={'pk': self.request.user.pk})
    
@method_decorator(login_required, name='dispatch')    
@method_decorator(user_passes_test(is_superuser, login_url=reverse_lazy('home')), name='dispatch')
class StudentBorrowedBooksListView(ListView):
    model = Student
    template_name = 'accounts/admin_dashboard.html'
    context_object_name = 'students'

    def get_queryset(self):
        return Student.objects.prefetch_related('borrowed_books_set__book').order_by("id")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = context['students']
        for student in students:
            for borrowed_book in student.borrowed_books_set.all():
                if borrowed_book.date_borrowed:
                    borrowed_book.date_borrowed += timedelta(hours=3)
                if borrowed_book.return_date:
                    borrowed_book.return_date += timedelta(hours=3)
        return context
class CustomLogoutView(LogoutView):
    def get_next_page(self):
        return reverse_lazy('home') 

class CustomPasswordChangeView(PasswordChangeDoneView):
    def get_next_page(self):
        return reverse_lazy('home')  

