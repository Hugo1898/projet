from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import *
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import *
from django.template.defaultfilters import register

from .forms import *


@login_required
def communautes(request):
    communities = Communaute.objects.all()
    abonnement = Communaute.objects.filter(abonnes=request.user)

    for com in communities:
        com.user_is_manager = False
        if request.user in com.managers.all():
            com.user_is_manager = True

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

    if request.user in com.managers.all():
        posts = Post.objects.filter(communaute=com_id).order_by('-sticky', '-date_creation')
    else:
        posts = Post.objects.filter(communaute=com_id, visible=True).order_by('-sticky', '-date_creation')

    counts = {}
    for post in posts:
        counts[post.titre] = Commentaire.objects.filter(post=post).count()
    user = request.user

    # Pour vérifier si l'user est un manager
    com.user_is_manager = False
    if request.user in com.managers.all():
        com.user_is_manager = True
    return render(request, 'communitymanager/voir_posts.html', locals())


@login_required
def post(request, post_id):
    form = CommentaireForm(request.POST or None)

    if form.is_valid():
        contenu = form.cleaned_data['contenu']
        return redirect(reverse('commentaire', kwargs={"post_id": post_id, "contenu": contenu}))

    post = get_object_or_404(Post, pk=post_id)

    if request.user in post.communaute.managers.all():
        coments = Commentaire.objects.filter(post=post_id).order_by('-date_creation')
    else:
        coments = Commentaire.objects.filter(post=post_id, visible=True).order_by('-date_creation')

    count = coments.count()

    # Pour vérifier si l'user est manager de la communaute du commentaire
    for coment in coments:
        coment.user_is_manager = False
        if request.user in coment.post.communaute.managers.all():
            coment.user_is_manager = True
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


@login_required
def nouveau_post(request, sticky_post=0):
    form = PostForm(request.POST or None)
    mod = False
    if form.is_valid():
        post = form.save(commit=False)
        post.auteur = request.user
        post.visible=True
        if (sticky_post==1) and request.user in post.communaute.managers.all():
            post.sticky=True
        post.save()
        return redirect('post', post_id=post.id)

    communautes = Communaute.objects.all()
    return render(request, 'communitymanager/nouveau_post.html', locals())


@login_required
def modif_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    mod = True
    if form.is_valid():
        postm = form.save(commit=False)
        postm.auteur = request.user
        postm.save()
        return redirect('post', post_id=post_id)
    return render(request, 'communitymanager/nouveau_post.html', locals())


@login_required
def news_feed(request):
    communautes = request.user.communautes.all()
    coments = Commentaire.objects.all()
    posts = Post.objects.filter(visible=True).order_by('-date_creation').filter(communaute__in=communautes)
    counts = {}
    for post in posts:
        counts[post.titre] = Commentaire.objects.filter(post=post).count()
    return render(request, 'communitymanager/news_feed.html', locals())


@login_required
def nouvelle_communaute(request):
    form = CommunauteForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('communautes')

    return render(request, 'communitymanager/nouvelle_communaute.html', locals())

@login_required
def modif_communaute(request, communaute_id):
    communaute = get_object_or_404(Communaute, pk=communaute_id)
    if request.user in communaute.managers.all():

        form = CommunauteForm(request.POST or None, instance=communaute)

        mod = True
        if form.is_valid():
            form.save()
            return redirect('communautes')

        return render(request, 'communitymanager/nouvelle_communaute.html', locals())
    return redirect('communautes')

@login_required
def delete_communaute(request, communaute_id):
    communaute = get_object_or_404(Communaute, pk=communaute_id)
    if request.user in communaute.managers.all():
        communaute.delete()
    return redirect('communautes')

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    com_id=post.communaute.id
    if request.user in post.communaute.managers.all():
        post.delete()
    return redirect('communaute', com_id=com_id)

@login_required
def visibility_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user in post.communaute.managers.all():
        if (post.visible):
            post.visible=False
        elif (not post.visible):
            post.visible=True
        post.save()
    return redirect('communaute', com_id=post.communaute.id)

@login_required
def visibility_comment(request, commentaire_id):
    commentaire = get_object_or_404(Commentaire, pk=commentaire_id)
    if request.user in commentaire.post.communaute.managers.all():
        if (commentaire.visible):
            commentaire.visible=False
        elif (not commentaire.visible):
            commentaire.visible=True
        commentaire.save()
    return redirect('post', post_id=commentaire.post.id)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('communautes')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_color(dictionary, key):
    key = str(key)
    switcher = {
        "blanche" : "beige",
        "jaune" : "gold",
        "orange" : "darkorange",
        "rouge" : "#a50505",
        "écarlate" : "#ff0101"
    }
    return switcher.get(key)
