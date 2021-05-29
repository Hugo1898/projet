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
    path('calendrier/<int:com_id>/<int:prio_deg>/<int:j_d>/<int:m_d>/<int:y_d>/<int:j_f>/<int:m_f>/<int:y_f>/'
         , views.calendrier, name='calendrier'),
]