from django import forms
from .models import *


class CommentaireForm(forms.Form):
    contenu = forms.CharField(required=True)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ["auteur"]

    def clean(self):

        cleaned_data = super(PostForm, self).clean()
        date_evenement = cleaned_data['date_evenement']
        evenementiel = cleaned_data['evenementiel']

        if date_evenement < timezone.now() and evenementiel :
            raise forms.ValidationError('Votre événement doit se passer dans le futur !')
        return cleaned_data

class CommunauteForm(forms.ModelForm):
    class Meta:
        model = Communaute
        exclude = ["abonnes","suspended"]
