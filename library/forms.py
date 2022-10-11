#!/usr/bin/env python
# -*- coding: utf-8 -*-
from shutil import ReadError
from django.forms import ModelForm
from django import forms
from .models import Book, Reader, Category
from easy_select2 import Select2, select2_modelform, Select2Multiple
from django.core.validators import FileExtensionValidator

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=16,
        label=u'usuario: ',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'name': 'username',
            'id': 'id_username',
        })
    )
    password = forms.CharField(
        label=u'contraseña: ',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'password',
            'name': 'password',
            'id': 'id_password',
        }),
    )


class RegisterForm(forms.Form):
    username = forms.CharField(
        label=u'Nombre de usuario: ',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'name': 'username',
            'id': 'id_username',
        }),
    )
    name = forms.CharField(
        label=u'Nombre: ',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'name': 'name',
            'id': 'id_name',
        }),
    )
    password = forms.CharField(
        label=u'Contraseña: ',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'name': 'password',
            'id': 'id_password',
            'type': 'password'
        }),
    )
    re_password = forms.CharField(
        label=u'Repetir contraseña：',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'password',
            'name': 're_password',
            'id': 'id_re_password',
        }),
    )
    email = forms.CharField(
        label=u'e-mail：',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'name': 'email',
            'id': 'id_email',
        }),
        required=False,
    )

    photo = forms.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=['jpg'])],
        label=u'Avatar：',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'name': 'photo',
            'id': 'id_photo',
        }),
        required=False,
    )






class ResetPasswordForm(forms.Form):
    old_password = forms.CharField(
        label=u'contraseña original：',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'name': 'old_password',
            'id': 'id_old',
            'type': 'password'
        }),
    )
    new_password = forms.CharField(
        label=u'contraseña nueva：',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'name': 'new_password',
            'id': 'id_new',
            'type': 'password'
        }),
    )
    repeat_password = forms.CharField(
        label=u'repite la contraseña：',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'name': 'repeat_password',
            'id': 'id_repeat',
            'type': 'password'
        }),
    )



class SearchForm(forms.Form):
        CHOICES = [
            (u'ISBN', u'ISBN'),
            (u'Book_name', u'Nombre'),
            (u'author', u'autor'),
            (u'publisher', u'editorial')
        ]

        search_by = forms.ChoiceField(
            label='',
            choices=CHOICES,
            widget=forms.RadioSelect(),
            initial=u'Book_name',
        )

        keyword = forms.CharField(
            label='',
            max_length=32,
            widget=forms.TextInput(attrs={
                'class': 'form-control input-lg',
                'placeholder': u'buscador',
                'name': 'keyword',
            })
        )



class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = ['fav']
        widgets = {
        'category': Select2Multiple(attrs={'class':'select2','required': 'True'}),#attrs={'name':"category", 'required':"", 'multiple':"", 'data-select2-id':"id_category", 'tabindex':"-1", 'class':"select2-hidden-accessible", 'aria-hidden':"true"}),
        'place':Select2(attrs={'class':'select2'}),
        'author':Select2(attrs={'class':'select2'}),
        'publisher':Select2(attrs={'class':'select2'}),
        'description':forms.Textarea(attrs={'rows':'10', 'cols':'150'}),
        }


class ReaderForm(ModelForm):
    class Meta:
        model = Reader
        fields = '__all__'


class ReaderForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        name = forms.CharField(
            max_length=32,
            widget=forms.TextInput(attrs={

                'style':"margin:5px 0px 5px 10px"

            })
        )
