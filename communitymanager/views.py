from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import *
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import *
from django.template.defaultfilters import register
from django.db.models import Q

from .forms import *
from .utils import *


@login_required
def communautes(request):
    """Page d'affichage des communautes, qui sert de page d'accueil
        Permet aux community managers et administrateurs de modifier l'état d'une communauté"""
    if request.user.is_superuser:
        communities = Communaute.objects.all()
    else:
        communities = Communaute.objects.filter(Q(suspended=0) | Q(suspended=1))
    abonnement = Communaute.objects.filter(abonnes=request.user)

    for com in communities:
        com.user_is_manager = False
        if request.user in com.managers.all():
            com.user_is_manager = True

    all_managers = []
    for com in communities:
        all_managers += com.managers.all()
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
def communaute(request, com_id, degre, event):
    """Page d'affichage des détails d'une communaute
            Permet aux community managers de suivre l'Etat des posts de leur communauté"""
    com = get_object_or_404(Communaute, pk=com_id)
    user = request.user

    # Si la communauté est suspendue et que l'user n'est pas superuser, il ne peut pas y accéder
    if com.suspended == 2 and not request.user.is_superuser:
        return redirect("communautes")

    if request.user in com.managers.all() and event == 1:
        posts = Post.objects.filter(communaute=com_id, priorite__degre__gte=degre, evenementiel=True).order_by(
            '-sticky', '-date_creation')
    elif request.user in com.managers.all() and event == 0:
        posts = Post.objects.filter(communaute=com_id, visible=True, priorite__degre__gte=degre).order_by('-sticky',
                                                                                                          '-date_creation')
    elif event == 1:
        posts = Post.objects.filter(communaute=com_id, visible=True, priorite__degre__gte=degre,
                                    evenementiel=True).order_by('-sticky',
                                                                '-date_creation')
    else:
        posts = Post.objects.filter(communaute=com_id, visible=True, priorite__degre__gte=degre).order_by('-sticky',
                                                                                                          '-date_creation')
    counts = {}
    for post in posts:
        counts[post.titre] = Commentaire.objects.filter(post=post).count()
    user = request.user

    for post in posts:
        post.lu = False
        if request.user in post.lecteurs.all():
            post.lu = True
            post.save()

    # Filtrage de l'affichage des posts selon leur priorité et leur statut d'évènement ou non ; fonctionnalité disponible si l'utilisateur est abonné  :

    if request.user in com.abonnes.all():

        priorite_form = PrioriteForm(request.POST or None)

        if priorite_form.is_valid():
            label = priorite_form.cleaned_data['label']
            print(type(label))
            if label:
                priorite = get_object_or_404(Priorite, label=label).degre
            évènement = priorite_form.cleaned_data['évènement']
            if évènement is True and 'priorite' in locals():
                return redirect('communaute', com_id, priorite, 1)
            elif évènement is False and 'priorite' in locals():
                return redirect('communaute', com_id, priorite, 0)
            elif évènement is True:
                return redirect('communaute', com_id, 0, 1)
            else:
                return redirect('communaute', com_id, 0, 0)

    # Pour vérifier si l'user est un manager
    com.user_is_manager = False
    if request.user in com.managers.all():
        com.user_is_manager = True

    return render(request, 'communitymanager/voir_posts.html', locals())


@login_required
def post(request, post_id):
    """Affichage d'un post et de ses commentaires"""
    post = get_object_or_404(Post, pk=post_id)

    if (request.user in post.lecteurs.all()) is False:
        post.lecteurs.add(request.user)
        post.save()

    # Si la communauté est suspendue et que l'user n'est pas superuser, il ne peut pas y accéder
    if post.communaute.suspended == 2 and not request.user.is_superuser:
        return redirect("communautes")
    # Si la communauté est fermée et que l'auteur n'est ni admin ni superuser
    if not post.visible:
        if not request.user.is_superuser and not request.user in post.communaute.managers.all():
            return redirect("communautes")

    form = CommentaireForm(request.POST or None)

    if form.is_valid():
        commentaire = form.save(commit=False)
        commentaire.auteur = request.user
        commentaire.post = post
        commentaire.visible = True
        commentaire.save()

    if request.user in post.communaute.managers.all():
        coments = Commentaire.objects.filter(post=post_id).order_by('date_creation')
    else:
        coments = Commentaire.objects.filter(post=post_id, visible=True).order_by('date_creation')

    count = coments.count()

    # Pour vérifier si l'user est manager de la communaute du commentaire
    for coment in coments:
        coment.user_is_manager = False
        if request.user in coment.post.communaute.managers.all():
            coment.user_is_manager = True
    return render(request, 'communitymanager/voir_commentaires.html', locals())


@login_required
def nouveau_post(request, special_post=0):
    form = PostForm(request.POST or None)
    mod = False
    if form.is_valid():
        post = form.save(commit=False)
        post.auteur = request.user

        post.visible = True
        if (special_post == 1) and request.user in post.communaute.managers.all():
            post.sticky = True
        if (special_post == 2) and request.user.is_superuser:
            post.avertissement = True

        if post.communaute.open:
            post.save()
            return redirect('post', post_id=post.id)

    # Choix de communautés dans lesquelles l'user peut créer un post,
    # Elle doit etre ouverte, non suspendue et il ne doit pas en être banni
    communautes_choices = Communaute.objects.filter(open=True, suspended=0).exclude(banned=request.user)
    # Sauf pour un avertissement qui peut toujours être créé par un administrateur
    if (special_post == 2) and request.user.is_superuser:
        communautes_choices = Communaute.objects.all()

    return render(request, 'communitymanager/nouveau_post.html', locals())


@login_required
def modif_post(request, post_id):
    """Page de modification d'un post"""
    post = get_object_or_404(Post, pk=post_id)

    # Si la communauté est suspendue et que l'user n'est pas superuser, il ne peut pas modifier le post

    if (post.communaute.suspended == (2 or 1)) and not request.user.is_superuser:
        return redirect("communautes")
    # Si la communauté est fermee et que l'user n'est pas manager, il ne peut pas modifier le post
    if not post.communaute.open and not request.user in post.communaute.managers.all():
        return redirect("communautes")
    # Si l'user est banni de la communaute
    if request.user in post.communaute.banned.all():
        return redirect("communautes")

    form = PostForm(request.POST or None, instance=post)
    mod = True
    if form.is_valid():
        postm = form.save(commit=False)
        postm.auteur = request.user
        postm.save()
        return redirect('post', post_id=post_id)

    communautes_choices = Communaute.objects.filter(open=True, suspended=0).exclude(banned=request.user)
    return render(request, 'communitymanager/nouveau_post.html', locals())


@login_required
def news_feed(request):
    """Affichage de tous les posts des communautés abonnées en ordre chronologique"""
    communautes = request.user.communautes.filter(Q(suspended=0) | Q(suspended=1))
    coments = Commentaire.objects.all()
    posts = Post.objects.filter(visible=True).order_by('-date_creation').filter(communaute__in=communautes)
    counts = {}
    for post in posts:
        counts[post.titre] = Commentaire.objects.filter(post=post).count()
    return render(request, 'communitymanager/news_feed.html', locals())


@login_required
def nouvelle_communaute(request):
    """Page de création d'une communauté"""
    form = CommunauteForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('communautes')

    return render(request, 'communitymanager/nouvelle_communaute.html', locals())


@login_required
def modif_communaute(request, communaute_id):
    """Page de modification d'une communauté"""
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
    """Commande pour la suppression d'une communaute si l'user est bien manager"""
    communaute = get_object_or_404(Communaute, pk=communaute_id)
    if request.user in communaute.managers.all():
        communaute.delete()
    return redirect('communautes')


@login_required
def open_close_communaute(request, communaute_id):
    """Commande pour l'ouverture/fermeture d'une communaute si l'user est bien manager"""

    communaute = get_object_or_404(Communaute, pk=communaute_id)
    if request.user in communaute.managers.all():
        if (communaute.open):
            communaute.open = False
        elif (not communaute.open):
            communaute.open = True
        communaute.save()
    return redirect('communautes')


@login_required
def suspend_communaute(request, com_id, action):
    """Commande pour la suspension d'une communaute si l'user est bien admin ie superuser"""

    communaute = get_object_or_404(Communaute, pk=com_id)
    if request.user.is_superuser and (action in {0, 1, 2}):
        communaute.suspended = action
        communaute.save()
    return redirect('communautes')


@login_required
def delete_post(request, post_id):
    """Commande pour la suppression d'un post"""
    post = get_object_or_404(Post, pk=post_id)
    com_id = post.communaute.id

    if request.user not in post.communaute.banned.all():
        if (not post.avertissement and request.user in post.communaute.managers.all()) or (
                post.avertissement and request.user.is_superuser):
            post.delete()

    return redirect('communaute', com_id=com_id)


@login_required
def visibility_post(request, post_id):
    """Commande pour le changement de statut de visibilité d'un post"""
    post = get_object_or_404(Post, pk=post_id)

    if request.user not in post.communaute.banned.all():
        if (not post.avertissement and request.user in post.communaute.managers.all()) or (
                post.avertissement and request.user.is_superuser):
            if (post.visible):
                post.visible = False
            elif (not post.visible):
                post.visible = True
            post.save()
    return redirect('communaute', com_id=post.communaute.id)


@login_required
def sticky_modify_post(request, post_id):
    """Commande pour transformer un post sticky en non et réciproquement"""
    post = get_object_or_404(Post, pk=post_id)

    if request.user not in post.communaute.banned.all():
        if not post.avertissement and request.user in post.communaute.managers.all():
            if (post.sticky):
                post.sticky = False
            elif (not post.sticky):
                post.sticky = True
            post.save()
    return redirect('communaute', com_id=post.communaute.id)


@login_required
def visibility_comment(request, commentaire_id):
    """Commande pour le changement de statut de visibilité d'un commentaire"""
    commentaire = get_object_or_404(Commentaire, pk=commentaire_id)
    if request.user in commentaire.post.communaute.managers.all():
        if (commentaire.visible):
            commentaire.visible = False
        elif (not commentaire.visible):
            commentaire.visible = True
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
        "blanche": "beige",
        "jaune": "gold",
        "orange": "darkorange",
        "rouge": "#a50505",
        "écarlate": "#ff0101"
    }
    return switcher.get(key)


@login_required
def calendrier(request, com_id, prio_deg, j_d, m_d, y_d, j_f, m_f, y_f):
    form = CalendarForm(request.POST or None, auto_id="cal_%s")
    if form.is_valid():
        post = form.save(commit=False)
        post.auteur = request.user
        post.evenementiel = True
        post.visible = True
        post.save()

    coms = Communaute.objects.exclude(suspended=2)
    priorites = Priorite.objects.all().order_by("degre")

    if prio_deg != 0:
        choix_prio = get_object_or_404(Priorite, degre=prio_deg)

    if com_id != 0:
        choix_com = get_object_or_404(Communaute, pk=com_id)

    date_d = conv_date(j_d, m_d, y_d)
    date_f = conv_date(j_f, m_f, y_f)
    posts = filter(com_id, prio_deg, date_d, date_f)

    communautes_choices = Communaute.objects.filter(open=True, suspended=0).exclude(banned=request.user)

    return render(request, 'communitymanager/calendrier.html', locals())


@login_required()
def advanced_search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            # text search in all text fields
            content = form.cleaned_data['content']
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
            in_posts = form.cleaned_data['in_posts']
            in_communities = form.cleaned_data['in_communities']
            in_authors = form.cleaned_data['in_authors']
            event_date_start = form.cleaned_data['event_date_start']
            event_date_end = form.cleaned_data['event_date_end']
            subscribed_only = form.cleaned_data['subscribed_only']
            if in_communities:
                communities = Communaute.objects.filter(Q(nom__contains=content) | Q(description__contains=content))
            if in_posts:
                if in_authors:
                    posts = Post.objects.filter(Q(titre__contains=content) | Q(description__contains=content)
                                                | Q(auteur__username__contains=content))
                    comments = Commentaire.objects.filter(Q(contenu__contains=content)
                                                          | Q(auteur__username__contains=content))
                else:
                    posts = Post.objects.filter(Q(titre__contains=content) | Q(description__contains=content))
                    comments = Commentaire.objects.filter(Q(contenu__contains=content))
                counts = {}
                for post in posts:
                    counts[post.titre] = Commentaire.objects.filter(post=post).count()
                    comments = Commentaire.objects.filter(Q(contenu__contains=content)
                                                          | Q(auteur__username__contains=content))
            if in_authors:
                if in_posts:
                    posts = Post.objects.filter(Q(titre__contains=content) | Q(description__contains=content)
                                                | Q(auteur__username__contains=content))
                    comments = Commentaire.objects.filter(Q(contenu__contains=content)
                                                          | Q(auteur__username__contains=content))
                else:
                    posts = Post.objects.filter(Q(auteur__username__contains=content))
                    comments = Commentaire.objects.filter(Q(auteur__username__contains=content))
                counts = {}
                for post in posts:
                    counts[post.titre] = Commentaire.objects.filter(post=post).count()
                    comments = Commentaire.objects.filter(Q(contenu__contains=content)
                                                          | Q(auteur__username__contains=content))

            # creation date filters
            if start:
                communities = Communaute.objects.none()
                posts = posts.filter(date_creation__gt=start)
                comments = comments.filter(date_creation__gt=start)
            if end:
                communities = Communaute.objects.none()
                posts = posts.filter(date_creation__lt=end)
                comments = comments.filter(date_creation__lt=end)
            if event_date_start:
                communities = Communaute.objects.none()
                posts = posts.filter(Q(evenementiel=True) & Q(date_evenement__gt=event_date_start))
                comments = comments.none()
            if event_date_end:
                communities = Communaute.objects.none()
                posts = posts.filter(Q(evenementiel=True) & Q(date_evenement__lt=event_date_end))
                comments = comments.none()
            # search only in subscribed communities
            if subscribed_only:
                communities = communities.filter(abonnes=request.user)
                posts = posts.filter(communaute__abonnes=request.user)
                comments = comments.filter(post__communaute__abonnes=request.user)
            return render(request, 'communitymanager/search_result.html', locals())

    return render(request, 'communitymanager/search_result.html')
