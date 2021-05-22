from django import forms
from .models import *


class CommentaireForm(forms.Form):
    contenu = forms.CharField(required=True)
