from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from .forms import UserLoginForm,UserRegisterForm,GuestForm
from django.contrib.auth import login ,authenticate ,logout,get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView,DeleteView ,UpdateView
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import  ValidationError
from django.utils.http import is_safe_url
from .models import GuestUser
from userinfo.models import UserInfo
  
# Create your views here.

User = get_user_model()

def about_us(request):
    return render(request,"about.html",{})

# def contact_us(request):
#     return render(request,"contact.html",{})

def LoginView(request):
    form=UserLoginForm(request.POST or None)
    next_=request.GET.get('next')
    next_post=request.POST.get('next')
    redirect_urls=next_ or next_post or None
    if form.is_valid():
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            try:
                del request.session['guest_user_id'] #if user try to login after checkout
            except:
                pass
            if is_safe_url(redirect_urls,request.get_host()):
                return redirect(redirect_urls)
            else:
                return redirect('/home')
        else:
            raise ValidationError('Invalid uname or password', code='invalid')
    return render(request,"auth/login.html",{'form':form})

def GuestView(request):
    form=GuestForm(request.POST or None)
    next_=request.GET.get('next')
    next_post=request.POST.get('next')
    redirect_urls=next_ or next_post or None
    if form.is_valid():
        email = form.cleaned_data.get('Email')
        new_guest,created=GuestUser.objects.get_or_create(email=email)
        request.session['guest_email_id']=new_guest.id
        if is_safe_url(redirect_urls,request.get_host()):
            return redirect(redirect_urls)
        else:
            return redirect('/register')
    return redirect('/register')

def RegisterView(request):
    form=UserRegisterForm(request.POST or None)
    if form.is_valid():
        uname=form.cleaned_data.get("Username")
        email=form.cleaned_data.get("Email")
        passwd=form.cleaned_data.get("Password")
        new_user=User.objects.create_user(uname,email,passwd)
        return redirect('/login')
    return render(request,"auth/register.html",{"form":form})

@login_required
def LogoutView(request):
    logout(request)
    return redirect('/login')

class UpdateUserView(LoginRequiredMixin,UpdateView):
    model = User
    fields=['username','email']
    template_name='auth/user_update.html'
    success_url=reverse_lazy('product:home')
    def get_object(self):
        return get_object_or_404(User,username=self.request.user.username)

class UserDetailView(DetailView,LoginRequiredMixin):
    model=User
    context_object_name='User'
    template_name = "auth/user_detail.html"
    def get_object(self):
        return get_object_or_404(User,username=self.request.user.username)
    # def get_context_data(self, **kwargs):
    #     context = super(UserDetailView, self).get_context_data(**kwargs)
    #     context['userinfo'] = UserInfo.objects.get_or_create(user=self.request.user,active=True)[0]
    #     return context

class DeleteUserView(DeleteView,LoginRequiredMixin):
    model = User
    success_url=reverse_lazy('product:home')
    template_name = 'auth/user_confirm_delete.html'
    def get_object(self):
        return get_object_or_404(User,username=self.request.user.username)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('account:user_detail')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'auth/change_password.html', {
        'form': form
    })