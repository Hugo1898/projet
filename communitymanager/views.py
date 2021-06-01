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
    if request.user.is_superuser:
        communities = Communaute.objects.all()
    else:
        communities = Communaute.objects.filter(Q(suspended=0) | Q(suspended=1))
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

    # Si la communauté est suspendue et que l'user n'est pas superuser, il ne peut pas y accéder
    if com.suspended == 2 and not request.user.is_superuser :
        return redirect("communautes")

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
    post = get_object_or_404(Post, pk=post_id)

    # Si la communauté est suspendue et que l'user n'est pas superuser, il ne peut pas y accéder
    if post.communaute.suspended == 2 and not request.user.is_superuser:
        return redirect("communautes")

    form = CommentaireForm(request.POST or None)

    if form.is_valid():
        contenu = form.cleaned_data['contenu']
        return redirect(reverse('commentaire', kwargs={"post_id": post_id, "contenu": contenu}))

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
        if post.communaute.open:
            post.save()
            return redirect('post', post_id=post.id)

    communautes = Communaute.objects.all()
    return render(request, 'communitymanager/nouveau_post.html', locals())


@login_required
def modif_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    # Si la communauté est suspendue et que l'user n'est pas superuser, il ne peut pas modifier le post
    if (post.communaute.suspended == (2 or 1) )and not request.user.is_superuser:
        print(post.communaute.suspended)
        return redirect("communautes")

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
    communautes = request.user.communautes.filter(Q(suspended=0) | Q(suspended=1))
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


@login_required
def suspend_communaute(request, com_id, action):
    communaute = get_object_or_404(Communaute, pk=com_id)
    if request.user.is_superuser and (action in {0,1,2}):
        communaute.suspended = action
        communaute.save()
    return redirect('communautes')




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

    coms = Communaute.objects.all()
    priorites = Priorite.objects.all().order_by("degre")

    if prio_deg != 0:
        choix_prio = get_object_or_404(Priorite, degre=prio_deg)

    if com_id != 0:
        choix_com = get_object_or_404(Communaute, pk=com_id)

    date_d = conv_date(j_d, m_d, y_d)
    date_f = conv_date(j_f, m_f, y_f)
    posts = filter(com_id, prio_deg, date_d, date_f)

    return render(request, 'communitymanager/calendrier.html', locals())

@login_required()
def advanced_search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            print("form is valid")
            # text search in all text fields
            content = form.cleaned_data['content']
            community_titles = Communaute.objects.filter(nom__contains=content)
            community_desc = Communaute.objects.filter(description__contains=content)
            posts_written_by = Post.objects.filter(auteur__username__contains=content)
            posts_title = Post.objects.filter(titre__contains=content)
            posts_content = Post.objects.filter(description__contains=content)
            comments_written_by = Commentaire.objects.filter(auteur__username__contains=content)
            comments_containing = Commentaire.objects.filter(contenu__contains=content)
            # date creation filter
            if form.start:
                start = form.cleaned_data['start']
                posts_written_by = Post.objects.filter(date_creation__gt=start)
                posts_title = Post.objects.filter(date_creation__gt=start)
                posts_content = Post.objects.filter(date_creation__gt=start)
                comments_written_by = Commentaire.objects.filter(date_creation__gt=start)
                comments_containing = Commentaire.objects.filter(date_creation__gt=start)
            if form.end:
                end = form.cleaned_data['end']
                posts_written_by = Post.objects.filter(post__date_creation__lt=end)
                posts_title = Post.objects.filter(date_creation__lt=end)
                posts_content = Post.objects.filter(date_creation__lt=end)
                comments_written_by = Commentaire.objects.filter(date_creation__lt=end)
                comments_containing = Commentaire.objects.filter(date_creation__lt=end)
            subscribed_only = form.cleaned_data['subscribed_only']
            if subscribed_only:
                community_titles = Communaute.objects.filter(abonnes__communautes__abonnes__contains=request.user)
                community_desc = Communaute.objects.filter(abonnes__communautes__abonnes__contains=request.user)
                posts_written_by = Post.objects.filter(communaute__abonnes__post__contains=request.user)
                posts_title = Post.objects.filter(communaute__abonnes__post__contains=request.user)
                posts_content = Post.objects.filter(communaute__abonnes__post__contains=request.user)
                comments_written_by = Commentaire.objects.filter(
                    communaute__abonnes__post__commentaire__contains=request.user)
                comments_containing = Commentaire.objects.filter(
                    communaute__abonnes__post__commentaire__contains=request.user)
            return render(request, 'communitymanager/search_result.html', {'community_titles': community_titles,
                                                                          'community_desc': community_desc,
                                                                          'posts_written_by': posts_written_by,
                                                                          'posts_titles': posts_title,
                                                                          'posts_content': posts_content,
                                                                          'comments_written_by': comments_written_by,
                                                                          'comments_containing': comments_containing})
        else:
            print(form.errors)
    return render(request, 'communitymanager/search_result.html')
