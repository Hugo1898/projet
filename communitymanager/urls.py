from django.urls import path
from . import views

urlpatterns = [
    path('communautes/', views.communautes, name='communautes'),
    path('communautes/<str:action>/<int:com_id>/', views.abonnement, name='abonnement'),
    path('communaute/<int:com_id>/', views.communaute, name='communaute'),
    path('post/<int:post_id>/', views.post, name='post'),
    path('commentaire/<int:post_id>/<str:contenu>/', views.commentaire, name='commentaire'),
    path('nouveau_post/', views.nouveau_post, name='nouveau_post'),
    path('modif_post/<int:post_id>/', views.modif_post, name='modif_post'),
    path('news_feed/', views.news_feed, name='news_feed'),
    path('nouvelle_communaute/', views.nouvelle_communaute, name='nouvelle_communaute'),
    path('modif_communaute/<int:communaute_id>/', views.modif_communaute, name='modif_communaute'),
    path('delete_communaute/<int:communaute_id>/', views.delete_communaute, name='delete_communaute'),
    path('visibility_post/<int:post_id>/', views.visibility_post, name='visibility_post'),
    path('nouveau_post/<int:sticky_post>/', views.nouveau_post, name='nouveau_sticky_post'),
    path('visibility_comment/<int:commentaire_id>/', views.visibility_comment, name='visibility_comment'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),

]