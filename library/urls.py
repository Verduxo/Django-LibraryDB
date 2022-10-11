#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.urls import re_path,path, include
from django.contrib.staticfiles import views as static_views
from django.conf.urls.static import static
from django.conf import settings
import library.views as views


urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^login/', views.user_login, name='user_login'),
    re_path(r'^logout/', views.user_logout, name='user_logout'),
    re_path(r'^register/', views.user_register, name='user_register'),
    re_path(r'^set_password/', views.set_password, name='set_password'),
    re_path(r'^profile/', views.profile, name='profile'),
    re_path(r'^update_profile/',views.update_profile.as_view(),name="update_profile"),


    path('book/borrowed/', views.borrowed_books, name='borrowed_books'),
    path('book/borrow/<str:id>/<str:action>', views.borrow, name='borrow'),

    re_path(r'^static/(?P<path>.*)$', static_views.serve, name='static'),

    path('search', views.book_search, name='book_search'),

    #path('categories/<str:category>', views.categories, name='categories'),
    path('add_publisher/',views.AddPublisherView.as_view(),name="add_publisher"),
    path('add_author/',views.AddAuthorView.as_view(),name="add_author"),
    path('add_place/',views.AddPlaceView.as_view(),name="add_place"),

    path('add_category/',views.AddCategoryView.as_view(),name="add_category"),
    path('category/<str:cats>', views.categoryView, name="category"),
    path('categories/',views.categoriesList,name="categories_list"),

    path('about/', views.about, name='about'),

    #re_path(r'^update/profile/$', views.update_user_view,name="update_user"),

    path('create',views.create_view,name="create"),
    #path('create',views.BookCreateView.as_view(),name="create"),

    path("book/detail/<str:id>", views.book_detail, name='detail'),
    path("book/update/<str:id>",views.update_view,name="update"),
    path("book/delete/<str:id>", views.delete_view,name="delete"),

    path("favourite", views.fav_view, name="favourite"),
    path("book/fav/add/<str:id>", views.add_to_fav, name="addtofav"),
    path("book/fav/remove/<str:id>", views.remove_fav, name="removefav"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

