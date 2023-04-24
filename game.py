from champions import champion
from flask import Flask, redirect, url_for, session
from jinja2 import Environment, FileSystemLoader
from flask_session import Session
import ZODB, ZODB.FileStorage
import transaction

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
        template = enviroment.get_template("baseLOB.html")
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


@app.route('/torn')
def ferTorn():
    p1 = session["faccio1"][len(session["faccio1"]) - 1]
    p2 = session["faccio2"][len(session["faccio2"]) - 1]
    a1 = p1.armadura
    a2 = p2.armadura
    accio = ""

    if session["accio1"] == "defensar":
        a1 = p1.defensar()
        accio = "-> El personatge 1 és proteigeix amb una força de " + str(a1) + ".\n" + accio
        print(accio)

    if session["accio2"] == "defensar":
        a2 = p2.defensar()
        accio = "-> El personatge 2 és proteigeix amb una força de " + str(a2) + ".\n" + accio
        print(accio)

    # Curació:
    if session["accio1"] == "curar":
        c1 = p1.curar()
        accio = "-> Personatge 1 es cura " + str(c1) + " de vida.\n" + accio
        print(accio)

    if session["accio2"] == "curar":
        c2 = p2.curar()
        accio = "-> Personatge 2 es cura " + str(c2) + " de vida.\n" + accio
        print(accio)

    # Atac físic:
    if session["accio1"] == "atacar":
        atac = p1.atacar()
        mal = atac - a2
        if mal < 0:
            mal = 0
        accio = "-> Personatge 1 ataca amb una força de " + str(atac) + " i fa " + str(
            p2.danyar(mal)) + " punts de mal.\n" + accio
        print(accio)

    if session["accio2"] == "atacar":
        atac = p2.atacar()
        mal = atac - a1
        if mal < 0:
            mal = 0
        accio = "-> Personatge 2 ataca amb una fora de " + str(atac) + " i fa " + str(
            p1.danyar(mal)) + " punts de mal.\n" + accio
        print(accio)

    if session["accio1"] == "magia":
        atac = p1.atacarAmbMagia()
        mal = atac - a2
        if mal < 0:
            mal = 0
        accio = "-> Personatge 1 ataca amb un atac magic de " + str(atac) + " i fa " + str(
            p2.danyar(mal)) + " punts de mal.\n" + accio
        print(accio)

    if session["accio2"] == "magia":
        atac = p2.atacarAmbMagia()
        mal = atac - a1
        if mal < 0:
            mal = 0
        accio = "-> Personatge 2 ataca amb un atac magic de " + str(atac) + " i fa " + str(
            p1.danyar(mal)) + " punts de mal.\n" + accio
        print(accio)

    # Si mor un personatge generem un altre:
    if p1.vida <= 0:
        crearPersonatge(session["faccio1"])
        accio = "\n\n🥇 Personatge 1 ha mort, el Personatge 2 s'emporta la victoria 🥇\n\n\n" + accio
        session["faccio1"].clear()
        crearPersonatge(session["faccio1"])
        print(accio)
        p1.winingqueuelose()
        p2.winingqueueplus()

    if p2.vida <= 0:
        crearPersonatge(session["faccio2"])
        accio = "\n\n🥇 Personatge 2 ha mort, el Personatge 1 s'emporta la victoria 🥇\n\n\n" + accio
        session["faccio2"].clear()
        crearPersonatge(session["faccio2"])
        print(accio)
        p2.winingqueuelose()
        p1.winingqueueplus()

    accio = "\n" + accio
    session["accio"] = accio + session["accio"]
    print(session["accio"])
    return retornaPagina()
