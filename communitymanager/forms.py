from django import forms

from .models import *


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        exclude = ["auteur", "date_creation", "post", "visible"]

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ["auteur"]
        widgets = {
            'date_evenement': forms.DateTimeInput(attrs={
            'class': 'form-control', 'type':'datetime-local',
            }, format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date_evenement"].input_formats = ["%Y-%m-%dT%H:%M"]

    """
    def clean(self):

        cleaned_data = super(PostForm, self).clean()
        date_evenement = cleaned_data['date_evenement']
        evenementiel = cleaned_data['evenementiel']

        if date_evenement < timezone.now() and evenementiel :
            raise forms.ValidationError('Votre événement doit se passer dans le futur !')
        return cleaned_data
    """

class CommunauteForm(forms.ModelForm):
    class Meta:
        model = Communaute
        exclude = ["abonnes","suspended"]


class CalendarForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ["auteur", "evenementiel"]
        widgets = {
            'date_evenement': forms.DateTimeInput(attrs={
            'class': 'form-control', 'type':'datetime-local',
            }, format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date_evenement"].input_formats = ["%Y-%m-%dT%H:%M"]

