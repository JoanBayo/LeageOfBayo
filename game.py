from champions import champion
from flask import Flask, redirect, url_for, session, render_template, request
from jinja2 import Environment, FileSystemLoader
from flask_session import Session
import ZODB, ZODB.FileStorage
import transaction
import pygame
import random


pygame.init()
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
storage = ZODB.FileStorage.FileStorage('safeGame.fs')
db = ZODB.DB(storage)


@app.route('/guardarPartida')
def guardarPartida():
    connection = db.open()
    root = connection.root()
    root['faccio1'] = session['faccio1']
    root['faccio2'] = session['faccio2']
    root['accio'] = session['accio']
    transaction.commit()
    connection.close()
    return retornaPagina()


@app.route('/recuperarPartida')
def recuperarPartida():
    connection = db.open()
    root = connection.root()
    session['faccio1'].clear()
    for p in root['faccio1']:
        session['faccio1'].append(p)
    session['faccio2'].clear()
    for p in root['faccio2']:
        session['faccio2'].append(p)

    session['accio'] = ""
    session['accio'] = root['accio']

    connection.close()
    return retornaPagina()


def crearPersonatge(faccio):
    c = champion()
    faccio.append(c)


def retornaPagina():
    environment = Environment(loader=FileSystemLoader("template/"))
    template = environment.get_template("champion.html")
    info = {"accio": session["accio"], "personatge1": session["faccio1"][len(session["faccio1"]) - 1].__dict__,
            "personatge2": session["faccio2"][len(session["faccio2"]) - 1].__dict__}
    contingut = template.render(info)
    return f'{contingut}'


@app.route('/')
def default():
    try:
        return retornaPagina()
    except:
        enviroment = Environment(loader=FileSystemLoader("template/"))
        template = enviroment.get_template("iniciGame.html")
        contingut = template.render()
        return f'{contingut}'


@app.route('/nova')
def novaPartida():
    session["accio"] = ""
    session["faccio1"] = []
    session["faccio2"] = []
    session["faccio1"].clear()
    session["faccio2"].clear()
    crearPersonatge(session["faccio1"])
    crearPersonatge(session["faccio2"])
    session["character1"] = 0
    session["character2"] = 0

    return retornaPagina()


@app.route('/atacar1')
def ataca1():
    session["accio1"] = "atacar"
    return redirect(url_for('default'))


@app.route('/magia1')
def magia1():
    session["accio1"] = "magia"
    return redirect(url_for("default"))


@app.route('/defensar1')
def defensar1():
    session["accio1"] = "defensar"
    return redirect(url_for("default"))


@app.route('/curar1')
def curar1():
    session["accio1"] = "curar"
    return redirect(url_for("default"))


@app.route('/atacar2')
def atacar2():
    session["accio2"] = "atacar"
    return redirect(url_for("default"))


@app.route('/magia2')
def magia2():
    session["accio2"] = "magia"
    return redirect(url_for("default"))


@app.route('/defensar2')
def defensar2():
    session["accio2"] = "defensar"
    return redirect(url_for("default"))


@app.route('/curar2')
def curar2():
    session["accio2"] = "curar"
    return redirect(url_for('default'))


@app.route('/recuperarMana1')
def recuperarMana1():
    session["accio1"] = "recuperarMana"
    return redirect(url_for('default'))


@app.route('/recuperarMana2')
def recuperarMana2():
    session["accio2"] = "recuperarMana"
    return redirect(url_for('default'))


@app.route('/torn')
def ferTorn():
    p1 = session["faccio1"][len(session["faccio1"]) - 1]
    p2 = session["faccio2"][len(session["faccio2"]) - 1]
    a1 = p1.armadura
    a2 = p2.armadura
    accio = ""

    # Defençar:
    if session["accio1"] == "defensar":
        a1 = p1.defensar()
        accio = "-> El personatge 1 és proteigeix amb una força de " + str(a1) + ".\n" + accio
        pygame.mixer.Sound("static/music/defensar.mp3").play()

    if session["accio2"] == "defensar":
        a2 = p2.defensar()
        accio = "-> El personatge 2 és proteigeix amb una força de " + str(a2) + ".\n" + accio
        pygame.mixer.Sound("static/music/defensar.mp3").play()

    # Curació:
    if session["accio1"] == "curar":
        c1 = p1.curar()
        accio = "-> Personatge 1 es cura " + str(c1) + " de vida.\n" + accio
        pygame.mixer.Sound("static/music/pocioVida.mp3").play()

    if session["accio2"] == "curar":
        c2 = p2.curar()
        accio = "-> Personatge 2 es cura " + str(c2) + " de vida.\n" + accio
        pygame.mixer.Sound("static/music/pocioVida.mp3").play()

    # RecuperarMana:
    if session["accio1"] == "recuperarMana":
        m1 = p1.recuperarMana()
        accio = "-> Personatge 1 recupera " + str(m1) + " punts de mana.\n" + accio
        pygame.mixer.Sound("static/music/pocioMana.mp3").play()

    if session["accio2"] == "recuperarMana":
        m2 = p2.recuperarMana()
        accio = "-> Personatge 2 recupera " + str(m2) + " punts de mana.\n" + accio
        pygame.mixer.Sound("static/music/pocioMana.mp3").play()

    # Atac físic:
    if session["accio1"] == "atacar":
        atac = p1.atacar()
        mal = atac - a2
        print(mal)
        print(atac)
        print(a2)
        if mal < 0:
            mal = 0
        accio = "-> Personatge 1 ataca amb una força de " + str(atac) + " i fa " + str(
            p2.danyar(mal)) + " punts de mal.\n" + accio
        pygame.mixer.Sound("static/music/atacar.mp3").play()

    if session["accio2"] == "atacar":
        atac = p2.atacar()
        mal = atac - a1
        if mal < 0:
            mal = 0
        accio = "-> Personatge 2 ataca amb una fora de " + str(atac) + " i fa " + str(
            p1.danyar(mal)) + " punts de mal.\n" + accio
        pygame.mixer.Sound("static/music/atacar.mp3").play()

    # Atac magic:
    if session["accio1"] == "magia":
        atac = p1.atacarAmbMagia()
        mal = atac - a2
        if mal < 0:
            mal = 0
        accio = "-> Personatge 1 ataca amb un atac magic de " + str(atac) + " i fa " + str(
            p2.danyar(mal)) + " punts de mal.\n" + accio
        pygame.mixer.Sound("static/music/atacarMagic.mp3").play()

    if session["accio2"] == "magia":
        atac = p2.atacarAmbMagia()
        mal = atac - a1
        if mal < 0:
            mal = 0
        accio = "-> Personatge 2 ataca amb un atac magic de " + str(atac) + " i fa " + str(
            p1.danyar(mal)) + " punts de mal.\n" + accio
        pygame.mixer.Sound("static/music/atacarMagic.mp3").play()

    # Contratacar amb la defença:
    if session["accio1"] == "defensar":
        contratac = p1.defensar()
        r = random.randint(1, 100)
        if r <= contratac:
            atac = p1.atacar()
            mal = atac - a2
            if mal < 0:
                mal = 0
            accio = accio + "-> Finalment el personatge 1 contr ataca amb una força " + str(atac) + " i fa " + str(
                p2.danyar(mal)) + " punts de mal.\n\n" + accio
            pygame.mixer.Sound("static/music/atacar.mp3").play()

    if session["accio2"] == "defensar":
        contratac = p2.defensar()
        r = random.randint(1, 100)
        if r <= contratac:
            atac = p2.atacar()
            mal = atac - a1
            if mal < 0:
                mal = 0
            accio = accio + "-> Finalment el personatge 2 contr ataca amb una força " + str(atac) + " i fa " + str(
                p1.danyar(mal)) + " punts de mal.\n\n" + accio
            pygame.mixer.Sound("static/music/atacar.mp3").play()

    p1.recuperarManaPasiva()
    p2.recuperarManaPasiva()

    # Si mor un personatge generem un altre:
    if p1.vida <= 0:
        session["character1"] += 1
        accio = "\nPersonatge 1 ha mort, el Personatge 2 s'emporta la ronda\n\n" + accio
        p1.winingqueuelose()
        crearPersonatge(session["faccio1"])
        p2.recuperarVidaPasiva()
        pygame.mixer.Sound("static/music/mort.mp3").play()
        p2.winingqueueplus()
        if session["character1"] == 6:
            return guanyadorPartida(2)
        else:
            return deadChamp1()

    if p2.vida <= 0:
        session["character2"] += 1
        accio = "\n\n🥇 Personatge 2 ha mort, el Personatge 1 s'emporta la ronda 🥇\n\n\n" + accio
        pygame.mixer.Sound("static/music/mort.mp3").play()
        crearPersonatge(session["faccio2"])
        p1.recuperarVidaPasiva()
        p2.winingqueuelose()
        p1.winingqueueplus()
        if session["character2"] == 6:
            return guanyadorPartida(1)

        else:
            return deadChamp2()

    accio = "\n" + accio
    session["accio"] = accio + session["accio"]
    return retornaPagina()


def deadChamp1():
    environment = Environment(loader=FileSystemLoader("template/"))
    template = environment.get_template("StealChamps1.html")
    info = {"personatge1": session["faccio1"][len(session["faccio1"]) - 2].__dict__,
            "personatge2": session["faccio2"][len(session["faccio2"]) - 1].__dict__}
    contingut = template.render(info)
    return f'{contingut}'


def deadChamp2():
    environment = Environment(loader=FileSystemLoader("template/"))
    template = environment.get_template("StealChamps2.html")
    info = {"personatge1": session["faccio1"][len(session["faccio1"]) - 1].__dict__,
            "personatge2": session["faccio2"][len(session["faccio2"]) - 2].__dict__}
    contingut = template.render(info)
    return f'{contingut}'


@app.route('/procesar1', methods=['POST'])
def procesar1():
    pociones = request.form.get('pociones')
    armadura = request.form.get('armadura')
    mana = request.form.get('mana')

    if pociones == 'si':
        session["faccio2"][len(session["faccio2"]) - 1].sumarPotis(
            session["faccio1"][len(session["faccio1"]) - 2].pocions)
    if armadura == 'si':
        session["faccio2"][len(session["faccio2"]) - 1].sumarArmadura(
            session["faccio1"][len(session["faccio1"]) - 2].armadura)
    if mana == 'si':
        session["faccio2"][len(session["faccio2"]) - 1].sumarPotisMana(
            session["faccio1"][len(session["faccio1"]) - 2].pocionsMana)

    return redirect(url_for('default'))


@app.route('/procesar2', methods=['POST'])
def procesar2():
    pociones = request.form.get('pociones')
    armadura = request.form.get('armadura')
    mana = request.form.get('mana')

    if pociones == 'si':
        session["faccio1"][len(session["faccio1"]) - 1].sumarPotis(
            session["faccio2"][len(session["faccio2"]) - 2].pocions)
    if armadura == 'si':
        session["faccio1"][len(session["faccio1"]) - 1].sumarArmadura(
            session["faccio2"][len(session["faccio2"]) - 2].armadura)
    if mana == 'si':
        session["faccio1"][len(session["faccio1"]) - 1].sumarPotisMana(
            session["faccio2"][len(session["faccio2"]) - 2].pocionsMana)
    return redirect(url_for('default'))


def guanyadorPartida(winer):
    pygame.mixer.Sound("static/music/guanyarPartida.mp3").play()
    enviroment = Environment(loader=FileSystemLoader("template/"))
    template = enviroment.get_template("finalGame.html")
    info = {"info": "Jugador " + str(winer)}
    contingut = template.render(info)
    return f'{contingut}'

# kaisa
# milo
# belvez
# aatrox
