#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
import uuid, os
from django.utils.deconstruct import deconstructible
from django.conf import settings
from django.urls import reverse


@deconstructible
class UploadToPathAndRename(object):
    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # get filename
        if instance.pk:
            filename = '{}.{}'.format(str(instance.pk)+'_'+str(uuid.uuid4().hex), ext)
        else:
            # set filename as random string
            filename = '{}.{}'.format(uuid.uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.sub_path, filename)


def custom_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
    return filename



class Reader(models.Model):
    max_borrowing = models.IntegerField(default=3, verbose_name='Cantidad disponible')
    user = models.OneToOneField(User,  unique=True,on_delete=models.CASCADE, verbose_name='Usuarios')
    name = models.CharField(max_length=16, verbose_name='Nombres')
    photo = models.ImageField(blank=True,upload_to=UploadToPathAndRename(os.path.join(settings.MEDIA_ROOT, 'profile')), verbose_name='Avatar')
    email = models.EmailField(max_length=255,verbose_name='E-mail')

    STATUS_CHOICES = (
        (0, 'normal'),
        (-1, 'overdue')
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=0,
    )
    class Meta:
        verbose_name = 'Lector'
        verbose_name_plural = 'Lectores'

        permissions = [
            ("create_book", "Puede crear libros"),
            ("delete_book", "Puede borrar libros"),
            ("update_book", "Puede cambiar la información mostrada sobre los libros"),
        ]

    def __str__(self):
        return self.name






class Category(models.Model):
    name = models.SlugField(max_length=255,verbose_name='Nombre')
    def __str__(self):
       return self.name

    def get_absolute_url(self):
        return reverse('index')
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'



class Place(models.Model):
    place = models.CharField(max_length=255,null="True",verbose_name='Localización')
    def __str__(self):
       return self.place
    def get_absolute_url(self):
        return reverse('index')
    class Meta:
        verbose_name = 'Localización'
        verbose_name_plural = 'Localizaciones'

class Author(models.Model):
    author = models.CharField(max_length=255,null="True",verbose_name='Autor')
    def __str__(self):
       return self.author
    def get_absolute_url(self):
        return reverse('index')
    class Meta:
        verbose_name = 'Autor'
        verbose_name_plural = 'Autores'

class Publisher(models.Model):
    publisher = models.CharField(max_length=64, verbose_name='Editorial',null=True)
    def __str__(self):
       return self.publisher
    def get_absolute_url(self):
        return reverse('index')
    class Meta:
        verbose_name = 'Editorial'
        verbose_name_plural = 'Editoriales'


class Book(models.Model):
    category = models.ManyToManyField(Category,verbose_name='Categoría')
    fav = models.ManyToManyField(Reader,related_name='fav',default='none',blank=True)
    place = models.ForeignKey(Place,on_delete=models.CASCADE,null="True",verbose_name='Localización')
    author = models.ForeignKey(Author,on_delete=models.CASCADE,null="True",verbose_name='Autor')
    publisher  = models.ForeignKey(Publisher,on_delete=models.CASCADE,null="True",verbose_name='Editorial')

    ISBN = models.CharField(max_length=15,verbose_name='ISBN')
    title = models.CharField(max_length=128, verbose_name='Título')
    description = models.CharField(max_length=1024, default='', verbose_name='Descripción')
    cover = models.ImageField(upload_to=UploadToPathAndRename(os.path.join(settings.MEDIA_ROOT, 'book_covers')), verbose_name='Portada')
    quantity = models.IntegerField(default=1, verbose_name='Cantidad')

    class Meta:
        verbose_name = 'Libro'
        verbose_name_plural = 'Libros'
    def __str__(self):
        return self.title



class Borrowing(models.Model):
    class Meta:
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'

    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, verbose_name='Lector')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Libro')

    date_issued = models.DateField(verbose_name='Día prestado')
    date_due_to_returned = models.DateField(verbose_name='Día de devolución')
    date_returned = models.DateField(null=True, verbose_name='Día devuelto')
    #amount_of_fine = models.FloatField(default=0.0, verbose_name='arrears')

    def __str__(self):
        return '{} borrowed {}'.format(self.reader, self.book)


class Favourite(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE,verbose_name='Libro')
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name='Usuario')

    class Meta:
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'
    def __str__(self):
        #return f"{self.book.title}, {self.user.username}"
        return self.book.title


