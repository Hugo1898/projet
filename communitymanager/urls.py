from django.urls import path
from . import views

urlpatterns = [
    # Projet individuel - Hugo
    path('communautes/', views.communautes, name='communautes'),
    path('communautes/<str:action>/<int:com_id>/', views.abonnement, name='abonnement'),
    path('communaute/<int:com_id>/<int:degre>/<int:event>/', views.communaute, name='communaute'),
    path('post/<int:post_id>/', views.post, name='post'),
    path('nouveau_post/', views.nouveau_post, name='nouveau_post'),
    path('modif_post/<int:post_id>/', views.modif_post, name='modif_post'),
    path('news_feed/', views.news_feed, name='news_feed'),
    path('nouvelle_communaute/', views.nouvelle_communaute, name='nouvelle_communaute'),
    path('', views.communautes, name='home'),

    #Extention 2 - Antoine

    ## Actions sur Communaute
    path('modif_communaute/<int:communaute_id>/', views.modif_communaute, name='modif_communaute'),
    path('delete_communaute/<int:communaute_id>/', views.delete_communaute, name='delete_communaute'),
    path('suspend_communaute/<int:com_id>/<int:action>/', views.suspend_communaute, name='suspend_communaute'),
    path('open_close_communaute/<int:communaute_id>/', views.open_close_communaute, name='open_close_communaute'),

    ## Actions sur Post
    path('visibility_post/<int:post_id>/', views.visibility_post, name='visibility_post'),
    path('nouveau_post/<int:special_post>/', views.nouveau_post, name='nouveau_special_post'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('sticky_modify_post/<int:post_id>/', views.sticky_modify_post, name='sticky_modify_post'),

    ## Actions sur Commentaire
    path('visibility_comment/<int:commentaire_id>/', views.visibility_comment, name='visibility_comment'),

    #Extention 4 - Hugo
    path('calendrier/<int:com_id>/<int:prio_deg>/<int:j_d>/<int:m_d>/<int:y_d>/<int:j_f>/<int:m_f>/<int:y_f>/'
         , views.calendrier, name='calendrier'),
    path('advanced_search/', views.advanced_search, name='recherche_avancee'),

]

