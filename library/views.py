#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from imp import PKG_DIRECTORY
import re
from django.shortcuts import render,get_object_or_404,HttpResponseRedirect, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import BookForm
from library.models import Book, Category, Place, Reader, User, Favourite, Borrowing,Author,Publisher
from library.forms import SearchForm, LoginForm, RegisterForm, ResetPasswordForm
from django.views.generic import CreateView, UpdateView
from django.db.models import Count


#! -----------------------error-----------------------

#si la pagina no se encuentra se procede a devolver un error404
#docs:
#The default 404 view will pass two variables to the template: request_path, which is the URL that resulted in the error, and exception,
#which is a useful representation of the exception that triggered the view (e.g. containing any message passed to a specific Http404 instance).
def page_not_found_view(request, exception=None):
    context = {
        'searchForm': SearchForm(),
    }
    return render(request, 'error/404.html',context)





#! -----------------------category-----------------------


class AddCategoryView(CreateView):
    model = Category
    template_name = 'categories/add_category.html'
    fields = '__all__'

class AddAuthorView(CreateView):
    model = Author
    template_name = 'categories/add_category.html'
    fields = '__all__'

class AddPublisherView(CreateView):
    model = Publisher
    template_name = 'categories/add_category.html'
    fields = '__all__'

class AddPlaceView(CreateView):
    model = Place
    template_name = 'categories/add_category.html'
    fields = '__all__'


def categoriesList(request):
    categories = Category.objects.all().annotate(book_count=Count('book'))


    context={'categories': categories,}
    return render(request,'categories/categories_list.html',context)


def categoryView(request, cats):
    page = request.GET.get('page', 1)
    current_path = request.get_full_path()
    category_books = Book.objects.filter(category__name=cats)
    paginator = Paginator(category_books, 5)

    try:
        category_books = paginator.page(page)
    except PageNotAnInteger:
        category_books = paginator.page(1)
    except EmptyPage:
        category_books = paginator.page(paginator.num_pages)

    context = {
        'category_books':category_books,
        'current_path': current_path,
        'searchForm': SearchForm(),
        'cats':cats,
    }
    return render(request, 'categories/categories.html',context)





#! -----------------------loan-----------------------

def borrow(request,id,action):
    state=None
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')

    if action == 'return_book':

        if not id:
            return HttpResponse('El id del libro no se ha encontrado, porfavor comuniqueselo al administrador')

        print('id: '+str(id))
        b = Borrowing.objects.get(pk=id)
        print('b: '+str(b))
        b.date_returned = datetime.date.today()
        b.save()

        r = Reader.objects.get(user=request.user)
        print('r: '+str(r))
        r.max_borrowing += 1
        r.save()

        bk = Book.objects.get(id=b.book.id)
        print('book: '+str(bk))
        bk.quantity += 1
        bk.save()

        borrowing = Borrowing.objects.filter(reader=r).exclude(date_returned__isnull=False)
        print('borrowing: '+str(borrowing))
        state = 'return_success'

        context = {
            'state': state,
            'borrowing':borrowing,
        }
        return render(request,'loan/prestados.html', context)



    elif action == 'renew_book':
        if not id:
            return HttpResponse('No se ha encontrado el ID del libro')

        b = Borrowing.objects.get(pk=id)
        if (b.date_due_to_returned - b.date_issued) < datetime.timedelta(60):
            b.date_due_to_returned += datetime.timedelta(30)
            b.save()
        r = Reader.objects.get(user=request.user)
        borrowing = Borrowing.objects.filter(reader=r).exclude(date_returned__isnull=False)
        state = 'renew_success'

        context = {
            'state': state,
            'borrowing':borrowing,
        }
        return render(request,'loan/prestados.html', context)


    elif action == 'borrow':
        if not request.user.is_authenticated:
            state = 'no_user'

        else:
            reader = Reader.objects.get(user_id=request.user.id)
            if reader.max_borrowing > 0:
                reader.max_borrowing -= 1
                reader.save()
                bk = Book.objects.get(pk=id)
                bk.quantity -= 1
                bk.save()
                issued = datetime.date.today()
                due_to_returned = issued + datetime.timedelta(30)
                b = Borrowing.objects.create(
                    reader=reader,
                    book=bk,
                    date_issued=issued,
                    date_due_to_returned=due_to_returned)
                b.save()
                borrowing = Borrowing.objects.filter(reader=reader).exclude(date_returned__isnull=False)
                state = 'borrow_success'

                context = {
                    'state': state,
                    'borrowing':borrowing
                }
                return render(request,'loan/prestados.html', context)

            else:
                state = 'upper_limit'


def borrowed_books(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    id = request.user.id

    try:
        reader = Reader.objects.get(user_id=id)
    except Reader.DoesNotExist:
        return HttpResponse('No se encuentra al usuario')
    borrowing = Borrowing.objects.filter(reader=reader).exclude(date_returned__isnull=False)

    context = {
        'reader': reader,
        'borrowing': borrowing,
    }
    return render(request, 'loan/prestados.html', context)





#! -----------------------CRUD-----------------------

def book_detail(request,id):
    state = None
    action = request.GET.get('action', None)
    reader=[]
    reader_id = request.user.id
    if request.user.is_authenticated:
        try:
            reader = Reader.objects.get(user_id=reader_id)
        except Reader.DoesNotExist:
            return HttpResponse('este usuario no posee ID, contacte con soporte para que le creen otra cuenta')
    if not id:
        return HttpResponse('No se ha encontrado el ID del libro 1')

    try:
        book = Book.objects.get(id=id)
        try:
            fav = Favourite.objects.get(book=book)
        except:
            fav = 'no'
    except Book.DoesNotExist:
        return HttpResponse('No se ha encontrado el ISBN del libro 2')




    context = {
        'reader':reader,
        'state': state,
        'book': book,
        'fav': fav
    }
    return render(request,  'CRUD/book_detail.html', context)


def update_view(request, id):
    context ={}

    print(id)
    if not id:
        return HttpResponse('No existe un ID 1')
    try:
        book = Book.objects.get(pk=id)
    except Book.DoesNotExist:
        return HttpResponse('No existe un ID 2')

    form = BookForm(request.POST or None, instance = book)
    if form.is_valid():
        form.save()
        id= form.save().id
        return HttpResponseRedirect('/book/detail/'+str(id))

    context["form"] = form
    return render(request, "CRUD/update_view.html", context)


class update_profile(UpdateView):
    model = Reader
    fields = "_all_"
    template_name = "account/update_profile.html"

def delete_view(request,id):
    context ={}

    print(id)
    if not id:
        return HttpResponse('No existe un ID')
    try:
        book = Book.objects.get(pk=id)
    except Book.DoesNotExist:
        return HttpResponse('No existe un ID')

    obj = get_object_or_404(Book, pk = id)
    if request.method =="POST":
        obj.delete()
        return HttpResponseRedirect("/")

    return render(request, "CRUD/delete_view.html", context)



def create_view(request):
        context ={}
        if User.has_perm('library.create_book'):
            pass

        form = BookForm(request.POST,request.FILES or None)
        if form.is_valid():
            form.save()
            id= form.save().id

            #book = Book.objects.get(pk=id)

            return HttpResponseRedirect('/book/detail/'+str(id))

        context = {
            'form':form
        }
        return render(request, "CRUD/create_view.html", context)





#! -----------------------generic-----------------------

def book_search(request):
    search_by = request.GET.get('search_by', 'Book_name')
    books = []
    current_path = request.get_full_path()
    keyword = request.GET.get('keyword', u'all')

    if keyword == u'all':
        books = Book.objects.all()
    else:
        if search_by == u'Book_name':
            keyword = request.GET.get('keyword', None)
            books = Book.objects.filter(title__contains=keyword).order_by('-title')[0:50]
        elif search_by == u'ISBN':
            keyword = request.GET.get('keyword', None)
            books = Book.objects.filter(ISBN__contains=keyword).order_by('-title')[0:50]
        elif search_by == u'author':
            keyword = request.GET.get('keyword', None)
            books = Book.objects.filter(author__contains=keyword).order_by('-title')[0:50]
        elif search_by == u'publisher':
            keyword = request.GET.get('keyword', None)
            books = Book.objects.filter(publisher__contains=keyword).order_by('-title')[0:50]

    paginator = Paginator(books, 5)
    page = request.GET.get('page', 1)

    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)

    # ugly solution for &page=2&page=3&page=4

    if '&page' in current_path:
        current_path = current_path.split('&page')[0]

    context = {
        'books': books,
        'search_by': search_by,
        'keyword': keyword,
        'current_path': current_path,
        'searchForm': SearchForm(),
    }
    return render(request, 'generic/search.html', context)


def about(request):
    context = {
        'searchForm': SearchForm()
    }
    return render(request, "generic/about.html", context)


def index(request):
    reader=[]
    id = request.user.id
    if request.user.is_authenticated:
        try:
            reader = Reader.objects.get(user_id=id)
        except Reader.DoesNotExist:
            return HttpResponse('este usuario no posee ID, contacte con soporte para que le creen otra cuenta')
    context = {
        'reader': reader,
        'searchForm': SearchForm(),
    }
    return render(request, 'generic/index.html', context)





#! -----------------------account-----------------------

def user_login(request):
    state = None
    if request.user.is_authenticated:
        return HttpResponseRedirect('/profile')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect('/profile')
            else:
                return HttpResponse(u'Tu cuenta está inhabilitada.')
        else:
            state = 'not_exist_or_password_error'

    context = {
        'loginForm': LoginForm(),
        'state': state,
    }
    return render(request, 'account/login.html', context)


def user_register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/profile')

    registerForm = RegisterForm()
    state = None

    if request.method == 'POST':
        registerForm = RegisterForm(request.POST, request.FILES)
        password = request.POST.get('password', '')
        repeat_password = request.POST.get('re_password', '')
        email = request.POST.get('email', '')
        username = request.POST.get('username', '')
        name = request.POST.get('name', '')
        photo = request.FILES.get('photo', '')

    
        if User.objects.filter(username=username):
            state = 'user_exist'
        if not photo.name[-3:].lower() in ['jpg','png','jpeg','gif']:
            state="wrong_extension"
        elif password == '' :
            state = 'empty_password'
        elif repeat_password == '':
            state= 'empty_repeat_password'
        elif password != repeat_password:
            state = 'repeat_error'
        elif email =='':
            state = 'empty_email'
        elif '@addinformatica.com' not in email:
            state = 'wrong_email'
        else:
            new_user = User.objects.create(username=username)
            new_user.set_password(password)
            new_user.save()
            new_reader = Reader.objects.create(user=new_user, name=name,email=email)
            new_reader.photo = request.FILES['photo']
            new_reader.save()
            state = 'success'

            auth.login(request, new_user)

            context = {
                'state': state,
                'registerForm': registerForm,
            }
            return HttpResponseRedirect('/profile')
    context = {
        'state': state,
        'registerForm': registerForm,
    }
    return render(request, 'account/register.html', context)


@login_required
def set_password(request):
    user = request.user
    state = None
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        repeat_password = request.POST.get('repeat_password', '')

        if user.check_password(old_password):
            if not new_password:
                state = 'empty'
            elif new_password != repeat_password:
                state = 'repeat_error'
            else:
                user.set_password(new_password)
                user.save()
                state = 'success'

    context = {
        'state': state,
        'resetPasswordForm': ResetPasswordForm(),
    }
    return render(request, 'account/set_password.html', context)


@login_required
def user_logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')


def profile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    id = request.user.id

    try:
        reader = Reader.objects.get(user_id=id)
    except Reader.DoesNotExist:
        return HttpResponse('No existe este usuario, contacte con el administrador.')
    borrowing = Borrowing.objects.filter(reader=reader).exclude(date_returned__isnull=False)

    context = {
        'state': request.GET.get('state', None),
        'reader': reader,
        'borrowing': borrowing,
    }
    return render(request, 'account/profile.html', context)





#! -----------------------favourite-----------------------
def fav_view(request):
    if request.user.is_authenticated:
        user = request.user
        favs = Favourite.objects.filter(user=user)
        return render(request, "favourite/favourite.html", {"favs": favs})
    return redirect("user_login")


def add_to_fav(request, id):
    if request.user.is_authenticated:
        book = Book.objects.filter(pk=id).first()
        fav = Favourite()
        fav.user = request.user
        fav.book = book
        fav.save()
        return redirect("favourite")
    return redirect("user_login")


@login_required
def remove_fav(request, id):
    if request.user.is_authenticated:
        book = Book.objects.filter(pk=id).first()
        fav = Favourite.objects.filter(user=request.user, book=book)
        fav.delete()
        return redirect("favourite")
    return redirect("user_login")
