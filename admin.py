from flask import Flask, render_template, request, redirect
import linsimpy

tse = linsimpy.TupleSpaceEnvironment()

ambientes = []
tse.out(("Ambientes", tuple(ambientes)))

dispositivos = []
tse.out(("Dispositivos", tuple(dispositivos)))

usuarios = []
tse.out(("Usuarios", tuple(usuarios)))

auxAmb = 1
auxDisp = 1
auxUser = 1

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def main(): 
    return render_template('admin.html', ambientes = listarAmbientes(), dispositivos = listarDispositivos(), usuarios = listarUsuarios(), dispAmbs = listarDispositivosEmTodosAmbientes(), userAmbs = listarUsuariosEmTodosAmbientes())

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        usuario = str(request.form["usuario"])
        if usuario in listarUsuarios():
            return redirect('client/'+ usuario)
    return render_template('login.html', usuarios = listarUsuarios())

@app.route("/client/<string:user>", methods=["POST", "GET"])
def cliente(user):
    if request.method == "POST":
        usuario = str(request.form["usuario"])
        if usuario in listarUsuarios():
            return redirect('client/'+ usuario)
    ambiente = tse.rdp(("Usuario", user, str))[2]

    return render_template('client.html', usuario = user, ambiente = ambiente, mensagens = lerMensagens(ambiente))

@app.route("/client/<string:user>/send", methods=["POST"])
def mandarMensagem(user):
    if request.method == "POST":
        mensagem = str(request.form["mensagem"])
        ambiente = tse.rdp(("Usuario", user, str))[2]
        mgs = list(tse.inp(("Ambiente", ambiente, object))[2])
        mgs.append(user + ": " + mensagem)
        tse.out(("Ambiente", ambiente, tuple(mgs)))
    return redirect('/client/'+ user)

def lerMensagens(amb):
    mensagens = list(tse.rdp(("Ambiente", amb, object))[2])
    return mensagens

@app.route("/criarambiente", methods=["POST"])
def criarAmbiente():
    mensagens = []
    dispositivos = []
    usuarios = []
    
    global auxAmb
    amb = "amb" + str(auxAmb)

    tse.out(("Ambiente", amb, tuple(mensagens)))
    tse.out(("Dispositivos no ambiente", amb, tuple(dispositivos)))
    tse.out(("Usuarios no ambiente", amb, tuple(usuarios)))

    ambientes = tse.inp(("Ambientes", object))
    temp = list(ambientes[1])
    temp.append(amb)
    tse.out(("Ambientes", tuple(temp)))
    auxAmb += 1
    return redirect('/')

@app.route("/destruirambiente", methods=["POST"])
def destruirAmbiente():
    if request.method == "POST":
        amb = str(request.form["ambienteDestruido"])
        dispositivo = listarDispositivosEmTodosAmbientes()[amb]
        usuario = listarUsuariosEmTodosAmbientes()[amb]
        if list(dispositivo) == [] and list(usuario) == []:
            tse.inp(("Ambiente", amb, object))
            ambientes = list(tse.inp(("Ambientes", object))[1])
            ambientes.remove(amb)
            tse.out(("Ambientes", tuple(ambientes)))
            tse.inp(("Dispositivos no ambiente", amb, object))
            tse.inp(("Usuarios no ambiente", amb, object))
        return redirect('/')


def listarAmbientes():
    ambientes = tse.rdp(("Ambientes", object))
    return list(ambientes[1])

def listarDispositivosEmTodosAmbientes():
    dic = {}
    ambientes = listarAmbientes()
    for ambiente in ambientes:
        dispositivos = tse.rdp(("Dispositivos no ambiente", ambiente, object))
        dic[ambiente] = list(dispositivos[2])
    return dic

def listarUsuariosEmTodosAmbientes():
    dic = {}
    ambientes = listarAmbientes()
    for ambiente in ambientes:
        usuarios = tse.rdp(("Usuarios no ambiente", ambiente, object))
        dic[ambiente] = list(usuarios[2])
    return dic

@app.route("/criardispositivos", methods=["POST"])
def criarDispositivos():
    global auxDisp
    disp = "disp" + str(auxDisp)
    tse.out(("Dispositivo", disp, "Sem ambiente"))
    dispositivos = tse.inp(("Dispositivos", object))
    temp = list(dispositivos[1])
    temp.append(disp)
    tse.out(("Dispositivos", tuple(temp)))
    auxDisp += 1
    return redirect('/')

def listarDispositivos():
    dispositivos = tse.rdp(("Dispositivos", object))
    return list(dispositivos[1])

@app.route("/trocarambientedispositivo/<string:disp>", methods=["POST"])
def trocarAmbienteDispositivo(disp):
    if request.method == "POST":
        newAmb = str(request.form["ambiente"])
        amb = tse.inp(("Dispositivo", disp, str))[2]
        #remove
        if amb != "Sem ambiente":
            dispAmb = list(tse.inp(("Dispositivos no ambiente", amb, object))[2])
            dispAmb.remove(disp)
            tse.out(("Dispositivos no ambiente", amb, dispAmb))
        ##add
        tse.out(("Dispositivo", disp, newAmb))
        dispAmb = list(tse.inp(("Dispositivos no ambiente", newAmb, object))[2])
        dispAmb.append(disp)
        tse.out(("Dispositivos no ambiente", newAmb, dispAmb))
        return redirect('/')

@app.route("/trocarambienteusuario/<string:user>", methods=["POST"])
def trocarAmbienteUsuario(user):
    if request.method == "POST":
        newAmb = str(request.form["ambienteUser"])
        amb = tse.inp(("Usuario", user, str))[2]
        #remove
        if amb != "Sem ambiente":
            userAmb = list(tse.inp(("Usuarios no ambiente", amb, object))[2])
            userAmb.remove(user)
            tse.out(("Usuarios no ambiente", amb, userAmb))
        ##add
        tse.out(("Usuario", user, newAmb))
        userAmb = list(tse.inp(("Usuarios no ambiente", newAmb, object))[2])
        userAmb.append(user)
        tse.out(("Usuarios no ambiente", newAmb, userAmb))
        return redirect('/')

@app.route("/criarusuarios", methods=["POST"])
def criarUsuarios():
    global auxUser
    user = "user" + str(auxUser)
    tse.out(("Usuario", user, "Sem ambiente"))
    usuarios = tse.inp(("Usuarios", object))
    temp = list(usuarios[1])
    temp.append(user)
    tse.out(("Usuarios", tuple(temp)))
    auxUser += 1
    return redirect('/')

def listarUsuarios():
    usuarios = tse.rdp(("Usuarios", object))
    return list(usuarios[1])

if __name__ == "__main__":
    app.run(debug=True)