from django.utils.http import is_safe_url 
from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import ListView ,DetailView,DeleteView ,CreateView ,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import ProductForm
from django.contrib.auth import get_user
from cart.models import Cart
from .models import Product
from analysis.mixins import ObjectViewMixin
# Create your views here.


class ProductListView(ListView):
    model = Product
    ordering = ['-arrival_date']
    template_name = "Product/Product_list.html"
    
    def get_context_data(self, **kwargs):
        context = super(ProductListView,self).get_context_data(**kwargs)
        cart,new=Cart.objects.new_or_get(self.request)
        context["cart"] = cart
        return context

class ProductDetailView(ObjectViewMixin,DetailView):
    model=Product
    context_object_name='product'
    template_name = "Product/product_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super(ProductDetailView,self).get_context_data(**kwargs)
        cart,new=Cart.objects.new_or_get(self.request)
        context["cart"] = cart
        return context
    
    def get_object(self):
        return get_object_or_404(Product,slug=self.kwargs.get('slug'))

# class DeleteProductView(DeleteView,LoginRequiredMixin):
#     model = Product
#     success_url=reverse_lazy('product:home')

@login_required
def deleteProduct(request,slug):
    product_obj = Product.objects.get(seller=request.user,slug=slug)
    if product_obj is not None and request.method == 'POST':
        product_obj.delete()
        return redirect("product:my_products")
    return render(request,'Product/product_confirm_delete.html',{})

# class CreateProductView(LoginRequiredMixin,CreateView):
#     model=Product
#     fields=('title','description','price','image')
#     redirect_field_name ='Product/Product_list.html'

@login_required
def UpdateProductView(request,slug):
    product_obj= Product.objects.get(slug=slug)
    form = ProductForm(request.POST or None,instance=product_obj)
    if request.method == 'POST' and form.is_valid(): 
        form.save() 
        return redirect('product:product_detail',slug=slug) 
    return render(request,'Product/product_update.html',{'form':form})

@login_required
def add_product(request):
    form=ProductForm()
    if request.method == 'POST':
        form=ProductForm(request.POST)
        if form.is_valid():
            product=form.save(commit=False)
            product.seller=get_user(request)
            product=form.save()
            return redirect('product:home')
        else:
            form=ProductForm()
    return render(request,'Product/product_form.html',{'form':form})

@login_required
def myProductsListView(request):
    qs=Product.objects.filter(seller=request.user).order_by("-arrival_date")
    return render(request,'Product/my_product_list.html',{'my_products':qs})
    