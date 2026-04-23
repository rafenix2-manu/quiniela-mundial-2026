from flask import Flask, render_template, request, send_file, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import os

# Importamos tu calendario maestro y el diccionario de banderas ISO desde partidos.py
try:
    from partidos import calendario_2026, BANDERAS
except ImportError:
    # En caso de que el archivo no exista o tenga error de importación
    calendario_2026 = []
    BANDERAS = {}

app = Flask(__name__)

# --- CONFIGURACIÓN DE SEGURIDAD Y BASE DE DATOS ---
app.config['SECRET_KEY'] = 'mpc_mundialista_2026_full_104_secure'
# Usamos SQLite (En Render recuerda que se borra al reiniciar si no usas disco persistente)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiniela.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# 1. MODELOS DE BASE DE DATOS (SQLAlchemy)
# ==========================================

class Quiniela(db.Model):
    """Representa un 'Ticket' de participación de un usuario"""
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    pronosticos = db.relationship('Pronostico', backref='ticket', lazy=True, cascade="all, delete-orphan")

class Partido(db.Model):
    """Representa el calendario oficial de partidos"""
    id = db.Column(db.Integer, primary_key=True) # ID oficial del archivo partidos.py
    equipo_local = db.Column(db.String(100), nullable=False)
    equipo_visitante = db.Column(db.String(100), nullable=False)
    fecha_partido = db.Column(db.DateTime, nullable=False)
    grupo = db.Column(db.String(20), nullable=True)
    ciudad = db.Column(db.String(100), nullable=True)
    
    # Resultados oficiales cargados por el Admin
    goles_local_real = db.Column(db.Integer, nullable=True)
    goles_visitante_real = db.Column(db.Integer, nullable=True)
    pronosticos = db.relationship('Pronostico', backref='juego', lazy=True)

class Pronostico(db.Model):
    """Guarda la predicción de goles por ticket y por partido"""
    id = db.Column(db.Integer, primary_key=True)
    quiniela_id = db.Column(db.Integer, db.ForeignKey('quiniela.id'), nullable=False)
    partido_id = db.Column(db.Integer, db.ForeignKey('partido.id'), nullable=False)
    goles_local_pred = db.Column(db.Integer, nullable=False)
    goles_visitante_pred = db.Column(db.Integer, nullable=False)
    puntos_obtenidos = db.Column(db.Integer, default=0)

# Lógica de cálculo de puntos
def calcular_puntos(pred_l, pred_v, real_l, real_v):
    if real_l is None or real_v is None: return 0
    # Marcador exacto: 3 puntos
    if pred_l == real_l and pred_v == real_v: return 3
    # Ganador o empate: 1 punto
    t_pred = (pred_l > pred_v) - (pred_l < pred_v)
    t_real = (real_l > real_v) - (real_l < real_v)
    if t_pred == t_real: return 1
    return 0

# ==========================================
# 2. RUTAS PÚBLICAS (JUGADORES)
# ==========================================

@app.route('/')
def index():
    ahora = datetime.now()
    partidos = Partido.query.order_by(Partido.fecha_partido).all()
    return render_template('index.html', partidos=partidos, ahora=ahora, banderas=BANDERAS)

@app.route('/guardar', methods=['POST'])
def guardar():
    nombre = request.form.get('nombre', '').strip()
    telefono = request.form.get('telefono', '').strip()
    ahora = datetime.now()
    
    if not nombre or not telefono:
        flash("Error: Nombre y Teléfono son requeridos.")
        return redirect(url_for('index'))

    # Creamos la quiniela (Ticket)
    nueva_quiniela = Quiniela(nombre=nombre, telefono=telefono)
    db.session.add(nueva_quiniela)
    db.session.commit()

    # Procesamos los resultados enviados
    partidos = Partido.query.all()
    for p in partidos:
        if ahora < p.fecha_partido: # Bloqueo por tiempo
            gl = request.form.get(f"gl_{p.id}")
            gv = request.form.get(f"gv_{p.id}")
            if gl is not None and gv is not None and gl != "" and gv != "":
                pron = Pronostico(
                    quiniela_id=nueva_quiniela.id,
                    partido_id=p.id,
                    goles_local_pred=int(gl),
                    goles_visitante_pred=int(gv)
                )
                db.session.add(pron)
                
    db.session.commit()
    flash(f"¡Éxito! Quiniela de {nombre} registrada con el Folio #{nueva_quiniela.id}")
    return redirect(url_for('index'))

# ==========================================
# 3. RUTAS ADMINISTRATIVAS
# ==========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('user') == 'admin' and request.form.get('password') == 'mundial2026':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash("Credenciales incorrectas")
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

@app.route('/admin/actualizar/<int:id>', methods=['POST'])
def actualizar_partido(id):
    if not session.get('admin'): return redirect(url_for('admin_login'))
    partido = Partido.query.get_or_404(id)
    gl = request.form.get('gl_real')
    gv = request.form.get('gv_real')
    
    if gl != "" and gv != "":
        partido.goles_local_real = int(gl)
        partido.goles_visitante_real = int(gv)
        
        # Actualizar puntos de todos los pronósticos de este partido
        for pron in partido.pronosticos:
            pron.puntos_obtenidos = calcular_puntos(
                pron.goles_local_pred, pron.goles_visitante_pred,
                partido.goles_local_real, partido.goles_visitante_real
            )
        db.session.commit()
        flash(f"Marcador actualizado para {partido.equipo_local} vs {partido.equipo_visitante}")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/excel')
def descargar_excel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    
    ranking = []
    detalle = []
    quinielas = Quiniela.query.all()
    
    for q in quinielas:
        pts = sum([p.puntos_obtenidos for p in q.pronosticos])
        ranking.append({
            "Folio": q.id, "Nombre": q.nombre, "Tel": q.telefono, 
            "Pts": pts, "Fecha": q.fecha_registro.strftime('%d/%m/%Y %H:%M')
        })
        for pron in q.pronosticos:
            detalle.append({
                "Folio": q.id, "Nombre": q.nombre,
                "Partido": f"{pron.juego.equipo_local} vs {pron.juego.equipo_visitante}",
                "Prediccion": f"{pron.goles_local_pred}-{pron.goles_visitante_pred}",
                "Puntos": pron.puntos_obtenidos
            })

    output = "Reporte_Quiniela_MPC.xlsx"
    with pd.ExcelWriter(output) as writer:
        pd.DataFrame(ranking).sort_values("Pts", ascending=False).to_excel(writer, sheet_name='Ranking', index=False)
        pd.DataFrame(detalle).to_excel(writer, sheet_name='Detalles', index=False)
    
    return send_file(output, as_attachment=True)

# ==========================================
# INICIALIZACIÓN DE LA APLICACIÓN
# ==========================================

with app.app_context():
    db.create_all()
    # Sincronización inteligente de partidos desde partidos.py
    for p in calendario_2026:
        partido_db = Partido.query.get(p['id'])
        if partido_db:
            partido_db.equipo_local = p['local']
            partido_db.equipo_visitante = p['visitante']
            partido_db.fecha_partido = datetime.strptime(p['fecha'], "%Y-%m-%d %H:%M")
            partido_db.grupo = p.get('grupo', '')
            partido_db.ciudad = p.get('ciudad', '')
        else:
            nuevo = Partido(
                id=p['id'], equipo_local=p['local'], equipo_visitante=p['visitante'],
                fecha_partido=datetime.strptime(p['fecha'], "%Y-%m-%d %H:%M"),
                grupo=p.get('grupo', ''), ciudad=p.get('ciudad', '')
            )
            db.session.add(nuevo)
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)