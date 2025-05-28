from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Joueur, Partie
from django.contrib.auth.models import User

@login_required
def dashboard(request):
    joueur, _ = Joueur.objects.get_or_create(user=request.user)
    parties = Partie.objects.filter(joueur=joueur).order_by('-date')[:10]
    return render(request, 'aviator/dashboard.html', {
        'joueur': joueur,
        'parties': parties
    })

def leaderboard(request):
    meilleurs_joueurs = Joueur.objects.select_related('user').order_by('-solde')[:10]
    return render(request, 'aviator/leaderboard.html', {
        'meilleurs_joueurs': meilleurs_joueurs
    })

@login_required
def historique(request):
    joueur, _ = Joueur.objects.get_or_create(user=request.user)
    parties = Partie.objects.filter(joueur=joueur).order_by('-date')
    return render(request, 'aviator/historique.html', {
        'joueur': joueur,
        'parties': parties
    })
