from django.db import models
from django.contrib.auth.models import User

class Joueur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    solde = models.IntegerField(default=10000)

    def __str__(self):
        return self.user.username

    def ajouter_solde(self, montant):
        self.solde += montant
        self.save()

    def retirer_solde(self, montant):
        if self.solde >= montant:
            self.solde -= montant
            self.save()
            return True
        return False


class Partie(models.Model):
    joueur = models.ForeignKey(Joueur, on_delete=models.CASCADE)
    mise = models.IntegerField()
    multiplicateur = models.FloatField()
    gain = models.IntegerField()
    retire_avant_crash = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.joueur.user.username} - {self.date.strftime('%Y-%m-%d %H:%M')}"
