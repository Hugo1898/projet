from django.contrib.auth.decorators import *
from django.shortcuts import *
from .models import *
from .forms import *


@login_required
def communautes(request):
    communities = Communaute.objects.all()
    abonnement = Communaute.objects.filter(abonnes=request.user)
    return render(request, 'communitymanager/voir_communautes.html', locals())


@login_required
def abonnement(request, action, com_id):
    com = get_object_or_404(Communaute, pk=com_id)

    if action == "abo":
        com.abonnes.add(request.user)
        com.save()
    elif action == "desabo":
        com.abonnes.remove(request.user)
        com.save()

    return redirect('communautes')


@login_required
def communaute(request, com_id):
    com = get_object_or_404(Communaute, pk=com_id)
    posts = Post.objects.filter(communaute=com_id)
    return render(request, 'communitymanager/voir_posts.html', locals())

@login_required
def post(request, post_id):
    form = CommentaireForm(request.POST or None)

    if form.is_valid():
        contenu = form.cleaned_data['contenu']
        return redirect(reverse('commentaire', kwargs={"post_id": post_id, "contenu": contenu}))

    post = get_object_or_404(Post, pk=post_id)
    coments = Commentaire.objects.filter(post=post_id).order_by('date_creation')
    return render(request, 'communitymanager/voir_commentaires.html', locals())

@login_required
def commentaire(request, post_id, contenu):
    coment = Commentaire()
    coment.auteur = request.user
    coment.contenu = contenu
    post = get_object_or_404(Post, pk=post_id)
    coment.post = post
    coment.save()
    return redirect('post', post_id=post_id)
