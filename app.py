from flask import Flask, render_template, request, send_file, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import os

# Importamos tu calendario maestro y el diccionario de banderas ISO
from partidos import calendario_2026, BANDERAS

app = Flask(__name__)
# Clave para encriptar sesiones y mensajes flash
app.config['SECRET_KEY'] = 'mpc_mundialista_2026_secure_key'
# Configuración de Base de Datos (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiniela.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# 1. MODELOS DE BASE DE DATOS
# ==========================================

class Quiniela(db.Model):
    """Modelo para cada registro de participación (Ticket)"""
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    # Relación con los pronósticos de este ticket
    pronosticos = db.relationship('Pronostico', backref='ticket', lazy=True, cascade="all, delete-orphan")

class Partido(db.Model):
    """Modelo para el calendario oficial de 104 partidos"""
    id = db.Column(db.Integer, primary_key=True) # Mantiene el ID oficial de la FIFA
    equipo_local = db.Column(db.String(50), nullable=False)
    equipo_visitante = db.Column(db.String(50), nullable=False)
    fecha_partido = db.Column(db.DateTime, nullable=False)
    grupo = db.Column(db.String(10), nullable=True)
    ciudad = db.Column(db.String(50), nullable=True)
    
    # Resultados reales cargados por el Admin
    goles_local_real = db.Column(db.Integer, nullable=True)
    goles_visitante_real = db.Column(db.Integer, nullable=True)
    pronosticos = db.relationship('Pronostico', backref='juego', lazy=True)

class Pronostico(db.Model):
    """Modelo para los goles que predijo un usuario en un partido"""
    id = db.Column(db.Integer, primary_key=True)
    quiniela_id = db.Column(db.Integer, db.ForeignKey('quiniela.id'), nullable=False)
    partido_id = db.Column(db.Integer, db.ForeignKey('partido.id'), nullable=False)
    goles_local_pred = db.Column(db.Integer, nullable=False)
    goles_visitante_pred = db.Column(db.Integer, nullable=False)
    puntos_obtenidos = db.Column(db.Integer, default=0)

# Lógica de puntuación profesional
def calcular_puntos(pred_l, pred_v, real_l, real_v):
    # Marcador exacto: 3 puntos
    if pred_l == real_l and pred_v == real_v: 
        return 3
    # Acierto a ganador o empate (Tendencia): 1 punto
    t_pred = (pred_l > pred_v) - (pred_l < pred_v)
    t_real = (real_l > real_v) - (real_l < real_v)
    if t_pred == t_real: 
        return 1
    return 0

# ==========================================
# 2. RUTAS PARA EL PÚBLICO
# ==========================================

@app.route('/')
def index():
    ahora = datetime.now()
    # Obtenemos partidos ordenados por fecha
    partidos = Partido.query.order_by(Partido.fecha_partido).all()
    return render_template('index.html', partidos=partidos, ahora=ahora, banderas=BANDERAS)

@app.route('/guardar', methods=['POST'])
def guardar():
    nombre = request.form.get('nombre').strip()
    telefono = request.form.get('telefono').strip()
    ahora = datetime.now()
    
    if not nombre or not telefono:
        flash("Error: El nombre y teléfono son campos obligatorios.")
        return redirect(url_for('index'))

    # Creamos la quiniela principal
    nueva_quiniela = Quiniela(nombre=nombre, telefono=telefono)
    db.session.add(nueva_quiniela)
    db.session.commit()

    # Guardamos los pronósticos solo de partidos que NO han iniciado
    partidos = Partido.query.all()
    for p in partidos:
        if ahora < p.fecha_partido:
            gl = request.form.get(f"gl_{p.id}")
            gv = request.form.get(f"gv_{p.id}")
            
            if gl != "" and gv != "" and gl is not None:
                pronostico = Pronostico(
                    quiniela_id=nueva_quiniela.id, 
                    partido_id=p.id, 
                    goles_local_pred=int(gl), 
                    goles_visitante_pred=int(gv)
                )
                db.session.add(pronostico)
                
    db.session.commit()
    flash(f"¡Listo {nombre}! Quiniela registrada correctamente con el Folio #{nueva_quiniela.id}.")
    return redirect(url_for('index'))

# ==========================================
# 3. RUTAS PARA EL ADMINISTRADOR
# ==========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        user = request.form.get('user')
        password = request.form.get('password')
        # Credenciales definidas por el usuario
        if user == 'admin' and password == 'mundial2026':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        flash("Acceso denegado: Credenciales incorrectas.")
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    partidos = Partido.query.order_by(Partido.fecha_partido).all()
    return render_template('admin_dashboard.html', partidos=partidos)

@app.route('/admin/actualizar/<int:id>', methods=['POST'])
def actualizar_partido(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    partido = Partido.query.get_or_404(id)
    gl_real = request.form.get('gl_real')
    gv_real = request.form.get('gv_real')

    if gl_real != "" and gv_real != "":
        partido.goles_local_real = int(gl_real)
        partido.goles_visitante_real = int(gv_real)
        
        # Recalcular puntos de todas las quinielas para este partido
        for pron in partido.pronosticos:
            pron.puntos_obtenidos = calcular_puntos(
                pron.goles_local_pred, pron.goles_visitante_pred,
                partido.goles_local_real, partido.goles_visitante_real
            )
        db.session.commit()
        flash(f"Resultado actualizado para {partido.equipo_local} vs {partido.equipo_visitante}")
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/excel')
def descargar_excel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    ranking_data = []
    detalle_data = []
    
    quinielas = Quiniela.query.all()
    for q in quinielas:
        total_pts = sum([p.puntos_obtenidos for p in q.pronosticos])
        ranking_data.append({
            "Folio": q.id,
            "Nombre": q.nombre,
            "WhatsApp": q.telefono,
            "Puntos Totales": total_pts,
            "Fecha Registro": q.fecha_registro.strftime('%d/%m/%Y %H:%M')
        })
        
        for pron in q.pronosticos:
            detalle_data.append({
                "Folio": q.id,
                "Participante": q.nombre,
                "Partido": f"{pron.juego.equipo_local} vs {pron.juego.equipo_visitante}",
                "Predicción": f"{pron.goles_local_pred}-{pron.goles_visitante_pred}",
                "Real": f"{pron.juego.goles_local_real}-{pron.juego.goles_visitante_real}" if pron.juego.goles_local_real is not None else "Pendiente",
                "Pts": pron.puntos_obtenidos
            })

    if not ranking_data:
        flash("No hay registros para exportar.")
        return redirect(url_for('admin_dashboard'))

    # Generación de Excel
    output_path = "Reporte_Quiniela_2026.xlsx"
    with pd.ExcelWriter(output_path) as writer:
        pd.DataFrame(ranking_data).sort_values(by="Puntos Totales", ascending=False).to_excel(writer, sheet_name='Ranking', index=False)
        pd.DataFrame(detalle_data).to_excel(writer, sheet_name='Detalle_Votos', index=False)

    return send_file(output_path, as_attachment=True)

# ==========================================
# INICIALIZACIÓN DE DATOS
# ==========================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Sincronización inteligente de partidos (actualiza nombres si cambian en partidos.py)
        for p in calendario_2026:
            partido_existente = Partido.query.get(p['id'])
            if partido_existente:
                partido_existente.equipo_local = p['local']
                partido_existente.equipo_visitante = p['visitante']
                partido_existente.fecha_partido = datetime.strptime(p['fecha'], "%Y-%m-%d %H:%M")
                partido_existente.grupo = p.get('grupo', '')
                partido_existente.ciudad = p.get('ciudad', '')
            else:
                nuevo = Partido(
                    id=p['id'],
                    equipo_local=p['local'],
                    equipo_visitante=p['visitante'],
                    fecha_partido=datetime.strptime(p['fecha'], "%Y-%m-%d %H:%M"),
                    grupo=p.get('grupo', ''),
                    ciudad=p.get('ciudad', '')
                )
                db.session.add(nuevo)
        db.session.commit()
    
    # En Render se usa gunicorn, pero dejamos esto para pruebas locales
    app.run(debug=True)