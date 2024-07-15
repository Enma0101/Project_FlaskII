from flask import Flask, render_template, request, g, redirect, url_for
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'
DATABASE = 'DataBase.sqlite3'

# Función para obtener la conexión a la base de datos
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

# Cerrar la conexión a la base de datos al finalizar la petición
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_estudiante', methods=['GET', 'POST'])
def add_estudiante():
    if request.method == 'POST':
        conn = get_db()
        try:
            dni_estudiante = request.form['dni_estudiante']
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            fecha_nacimiento = request.form['fecha_nacimiento']
            direccion = request.form['direccion']
            telefono = request.form['telefono']
            email = request.form['email']
            genero = request.form['genero']

            conn.execute('''
                INSERT INTO Estudiante (dni_estudiante, nombre, apellido, fecha_nacimiento, direccion, telefono, email, genero)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dni_estudiante, nombre, apellido, fecha_nacimiento, direccion, telefono, email, genero))
            conn.commit()
            return redirect(url_for('estudiantes'))
        except Exception as e:
            return f'Error al agregar estudiante: {str(e)}'
        finally:
            conn.close()
    return render_template('add_estudiante.html')

@app.route('/estudiantes')
def estudiantes():
    conn = get_db()
    cursor = conn.execute('SELECT * FROM Estudiante')
    estudiantes = cursor.fetchall()
    conn.close()
    return render_template('estudiantes.html', estudiantes=estudiantes)

@app.route('/edit_estudiante/<int:id>', methods=['GET', 'POST'])
def edit_estudiante(id):
    conn = get_db()
    if request.method == 'POST':
        try:
            dni_estudiante = request.form['dni_estudiante']
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            fecha_nacimiento = request.form['fecha_nacimiento']
            direccion = request.form['direccion']
            telefono = request.form['telefono']
            email = request.form['email']
            genero = request.form['genero']

            conn.execute('''
                UPDATE Estudiante
                SET dni_estudiante = ?, nombre = ?, apellido = ?, fecha_nacimiento = ?, direccion = ?, telefono = ?, email = ?, genero = ?
                WHERE id_estudiante = ?
            ''', (dni_estudiante, nombre, apellido, fecha_nacimiento, direccion, telefono, email, genero, id))
            conn.commit()
            return redirect(url_for('estudiantes'))
        except Exception as e:
            return f'Error al editar estudiante: {str(e)}'
        finally:
            conn.close()
    else:
        cursor = conn.execute('SELECT * FROM Estudiante WHERE id_estudiante = ?', (id,))
        estudiante = cursor.fetchone()
        conn.close()
        return render_template('edit_estudiante.html', estudiante=estudiante)
    
@app.route('/delete_estudiante/<int:id>', methods=['POST'])
def delete_estudiante(id):
    conn = get_db()
    try:
        conn.execute('DELETE FROM Estudiante WHERE id_estudiante = ?', (id,))
        conn.commit()
        return redirect(url_for('estudiantes'))
    except Exception as e:
        return f'Error al eliminar estudiante: {str(e)}'
    finally:
        conn.close()
@app.route('/add_profesor', methods=['GET', 'POST'])
def add_profesor():
    if request.method == 'POST':
        conn = get_db()
        try:
            dni_profesor = request.form['dni']
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            fecha_nacimiento = request.form['fecha_nacimiento']
            direccion = request.form['direccion']
            telefono = request.form['telefono']
            email = request.form['email']
            genero = request.form['genero']

            conn.execute('''
                INSERT INTO Profesor (dni_profesor, nombre, apellido, fecha_nacimiento, direccion, telefono, email, genero)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dni_profesor, nombre, apellido, fecha_nacimiento, direccion, telefono, email, genero))
            conn.commit()
            return redirect(url_for('profesores'))
        except Exception as e:
            return f'Error al agregar profesor: {str(e)}'
        finally:
            conn.close()
    return render_template('add_profesor.html')

@app.route('/profesores')
def profesores():
    conn = get_db()
    cursor = conn.execute('SELECT * FROM Profesor')
    profesores = cursor.fetchall()
    conn.close()
    return render_template('profesores.html', profesores=profesores)

@app.route('/edit_profesor/<int:id>', methods=['GET', 'POST'])
def edit_profesor(id):
    conn = get_db()
    if request.method == 'POST':
        try:
            dni_profesor = request.form['dni']
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            fecha_nacimiento = request.form['fecha_nacimiento']
            direccion = request.form['direccion']
            telefono = request.form['telefono']
            email = request.form['email']
            genero = request.form['genero']

            conn.execute('''
                UPDATE Profesor
                SET dni_profesor = ?, nombre = ?, apellido = ?, fecha_nacimiento = ?, direccion = ?, telefono = ?, email = ?, genero = ?
                WHERE id_profesor = ?
            ''', (dni_profesor, nombre, apellido, fecha_nacimiento, direccion, telefono, email, genero, id))
            conn.commit()
            return redirect(url_for('profesores'))
        except Exception as e:
            return f'Error al editar profesor: {str(e)}'
        finally:
            conn.close()
    else:
        cursor = conn.execute('SELECT * FROM Profesor WHERE id_profesor = ?', (id,))
        profesor = cursor.fetchone()
        conn.close()
        return render_template('edit_profesor.html', profesor=profesor)

@app.route('/delete_profesor/<int:id>', methods=['POST'])
def delete_profesor(id):
    conn = get_db()
    try:
        conn.execute('DELETE FROM Profesor WHERE id_profesor = ?', (id,))
        conn.commit()
        return redirect(url_for('profesores'))
    except Exception as e:
        return f'Error al eliminar profesor: {str(e)}'
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)