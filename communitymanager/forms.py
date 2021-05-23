from django import forms
from .models import *


class CommentaireForm(forms.Form):
    contenu = forms.CharField(required=True)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        auteur_id = kwargs.pop('auteur_id')
        super(PostForm, self).__init__(*args, **kwargs)
        auteur = User.objects.get(id=auteur_id)
        self.fields['auteur'].initial = auteur

class CommunauteForm(forms.ModelForm):
    class Meta:
        model = Communaute
        fields = '__all__'