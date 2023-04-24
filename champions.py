from random import randint
import random
import os


class champion():
    def __init__(self):
        self.atac = randint(1, 100)
        self.vida = randint(1, 1000)
        self.vidaMaxima = self.vida
        self.atacMagic = randint(1, 100)
        self.mana = randint(1, 100)
        self.armadura = randint(1, 50)
        self.pocions = randint(1, 10)
        self.imatge = selectChampImage()
        self.nom = selectChampName(self.imatge)
        self.winingqueue = 0

    def atacar(self):
        return self.atac + randint(1, 100)

    def atacarAmbMagia(self):
        resultat = 0
        if self.mana >= 19:
            self.mana -= 10
            resultat = self.atacMagic + randint(1, 100)
        return resultat

    def defensar(self):
        return self.armadura + randint(1, 100)

    def curar(self):
        puntsCurats = 0
        if self.pocions > 0:
            self.pocions -= 1
            punts = randint(1, 500)
            puntsCurats = min(punts, self.vidaMaxima - self.vida)
            self.vida += punts
            self.vida = min(self.vida, self.vidaMaxima)
        return puntsCurats

    def danyar(self, mal):
        malRebut = 0
        malRebut = min(self.vida, mal)
        self.vida -= malRebut
        return malRebut

    def winingqueueplus(self):
        self.winingqueue += 1
        return str(self.winingqueue)

    def winingqueuelose(self):
        self.winingqueue = 0
        if self.winingqueue == 0:
            return ""


def selectChampImage():
    dir_path = "./static/champ"
    img_list = os.listdir(dir_path)
    random_img = random.choice(img_list)
    img_path = os.path.join(dir_path, random_img)
    return img_path


def selectChampName(img_path):
    img_nom = img_path.replace("./static/champ/", "")
    img_nom = img_nom.replace(".jpg", "")
    return img_nom
