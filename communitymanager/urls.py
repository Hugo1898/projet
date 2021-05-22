from django.urls import path
from . import views

urlpatterns = [
    path('communautes/', views.communautes, name='communautes'),
    path('communautes/<str:action>/<int:com_id>/', views.abonnement, name='abonnement'),
    path('communaute/<int:com_id>/', views.communaute, name='communaute'),
    path('post/<int:post_id>/', views.post, name='post'),
    path('commentaire/<int:post_id>/<str:contenu>/', views.commentaire, name='commentaire'),
]