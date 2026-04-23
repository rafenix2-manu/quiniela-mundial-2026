from flask import Flask, render_template, request, send_file, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import os

# Importamos tu calendario y banderas
from partidos import calendario_2026, BANDERAS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mpc_mundialista_2026_full_104'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiniela.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# MODELOS DE BASE DE DATOS
# ==========================================
class Quiniela(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    pronosticos = db.relationship('Pronostico', backref='ticket', lazy=True, cascade="all, delete-orphan")

class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Usaremos el ID exacto de tu archivo
    equipo_local = db.Column(db.String(50), nullable=False)
    equipo_visitante = db.Column(db.String(50), nullable=False)
    fecha_partido = db.Column(db.DateTime, nullable=False)
    grupo = db.Column(db.String(10), nullable=True)
    ciudad = db.Column(db.String(50), nullable=True)
    
    goles_local_real = db.Column(db.Integer, nullable=True)
    goles_visitante_real = db.Column(db.Integer, nullable=True)
    pronosticos = db.relationship('Pronostico', backref='juego', lazy=True)

class Pronostico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiniela_id = db.Column(db.Integer, db.ForeignKey('quiniela.id'), nullable=False)
    partido_id = db.Column(db.Integer, db.ForeignKey('partido.id'), nullable=False)
    goles_local_pred = db.Column(db.Integer, nullable=False)
    goles_visitante_pred = db.Column(db.Integer, nullable=False)
    puntos_obtenidos = db.Column(db.Integer, default=0)

def calcular_puntos(pred_l, pred_v, real_l, real_v):
    if pred_l == real_l and pred_v == real_v: return 3
    t_pred = (pred_l > pred_v) - (pred_l < pred_v)
    t_real = (real_l > real_v) - (real_l < real_v)
    if t_pred == t_real: return 1
    return 0

# ==========================================
# RUTAS PÚBLICAS (JUGADORES)
# ==========================================
@app.route('/')
def index():
    ahora = datetime.now()
    partidos = Partido.query.order_by(Partido.fecha_partido).all()
    return render_template('index.html', partidos=partidos, ahora=ahora, banderas=BANDERAS)

@app.route('/guardar', methods=['POST'])
def guardar():
    nombre = request.form.get('nombre').strip()
    telefono = request.form.get('telefono').strip()
    ahora = datetime.now()
    
    if not nombre or not telefono:
        flash("Debes ingresar tu Nombre y Teléfono.")
        return redirect(url_for('index'))

    nueva_quiniela = Quiniela(nombre=nombre, telefono=telefono)
    db.session.add(nueva_quiniela)
    db.session.commit()

    partidos = Partido.query.all()
    for p in partidos:
        if ahora < p.fecha_partido:
            gl = request.form.get(f"gl_{p.id}")
            gv = request.form.get(f"gv_{p.id}")
            
            if gl != "" and gv != "" and gl is not None:
                pronostico = Pronostico(
                    quiniela_id=nueva_quiniela.id, partido_id=p.id, 
                    goles_local_pred=int(gl), goles_visitante_pred=int(gv)
                )
                db.session.add(pronostico)
                
    db.session.commit()
    flash(f"¡Éxito, {nombre}! Tus pronósticos han sido guardados (Folio #{nueva_quiniela.id}).")
    return redirect(url_for('index'))

# ==========================================
# RUTAS PRIVADAS (ADMIN)
# ==========================================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('user') == 'admin' and request.form.get('password') == 'mundial2026':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash("Credenciales incorrectas.")
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    partidos = Partido.query.order_by(Partido.fecha_partido).all()
    return render_template('admin_dashboard.html', partidos=partidos)

@app.route('/admin/actualizar_partido/<int:id>', methods=['POST'])
def actualizar_partido(id):
    if not session.get('admin'): return redirect(url_for('admin_login'))
    
    partido = Partido.query.get_or_404(id)
    gl_real = request.form.get('gl_real')
    gv_real = request.form.get('gv_real')

    if gl_real and gv_real:
        partido.goles_local_real = int(gl_real)
        partido.goles_visitante_real = int(gv_real)
        
        for pron in partido.pronosticos:
            pron.puntos_obtenidos = calcular_puntos(
                pron.goles_local_pred, pron.goles_visitante_pred,
                partido.goles_local_real, partido.goles_visitante_real
            )
        db.session.commit()
        flash(f"Marcador actualizado: {partido.equipo_local} {gl_real} - {gv_real} {partido.equipo_visitante}")
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/descargar_excel')
def descargar_excel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    
    registros, ranking = [], []
    quinielas = Quiniela.query.all()
    
    for q in quinielas:
        pts_totales = sum([pron.puntos_obtenidos for pron in q.pronosticos])
        ranking.append({
            "Folio": q.id, "Participante": q.nombre, "Teléfono": q.telefono, 
            "Puntos Totales": pts_totales, "Fecha Registro": q.fecha_registro.strftime('%Y-%m-%d %H:%M')
        })
        
        for pron in q.pronosticos:
            registros.append({
                "Folio": q.id, "Participante": q.nombre,
                "Partido": f"{pron.juego.equipo_local} vs {pron.juego.equipo_visitante}",
                "Su Pronóstico": f"{pron.goles_local_pred} - {pron.goles_visitante_pred}",
                "Puntos Obtenidos": pron.puntos_obtenidos
            })

    if not registros: 
        flash("No hay quinielas registradas aún.")
        return redirect(url_for('admin_dashboard'))

    df_ranking = pd.DataFrame(ranking).sort_values(by="Puntos Totales", ascending=False)
    df_detalles = pd.DataFrame(registros)
    
    output = "Resultados_Quiniela_104_Partidos.xlsx"
    with pd.ExcelWriter(output) as writer:
        df_ranking.to_excel(writer, sheet_name='Ranking General', index=False)
        df_detalles.to_excel(writer, sheet_name='Detalle por Partido', index=False)

    return send_file(output, as_attachment=True)

# ==========================================
# INICIALIZACIÓN INTELIGENTE DE BD
# ==========================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Escaneo y actualización inteligente: 
        # Si cambias un nombre en partidos.py, la base de datos lo actualizará sin borrar los puntos
        for p in calendario_2026:
            partido_db = Partido.query.get(p['id'])
            if partido_db:
                partido_db.equipo_local = p['local']
                partido_db.equipo_visitante = p['visitante']
                partido_db.fecha_partido = datetime.strptime(p['fecha'], "%Y-%m-%d %H:%M")
                partido_db.grupo = p.get('grupo', '')
                partido_db.ciudad = p.get('ciudad', '')
            else:
                nuevo_partido = Partido(
                    id=p['id'], equipo_local=p['local'], equipo_visitante=p['visitante'],
                    fecha_partido=datetime.strptime(p['fecha'], "%Y-%m-%d %H:%M"),
                    grupo=p.get('grupo', ''), ciudad=p.get('ciudad', '')
                )
                db.session.add(nuevo_partido)
        db.session.commit()
    app.run(debug=True)