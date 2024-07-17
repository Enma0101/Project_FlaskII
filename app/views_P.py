from flask import Flask, render_template, request, g, redirect, url_for, flash
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

def handle_error(error_message, template, **kwargs):
    flash(error_message, 'danger')
    return render_template(template, **kwargs)

#   ----CRUD-ESTUDIANTES----

# Rutas para estudiantes  
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

            # Validación simple de campos
            errores = []
            if not dni_estudiante:
                errores.append('El DNI es obligatorio.')
            if not nombre:
                errores.append('El nombre es obligatorio.')
            if not apellido:
                errores.append('El apellido es obligatorio.')
            if not fecha_nacimiento:
                errores.append('La fecha de nacimiento es obligatoria.')
            if not direccion:
                errores.append('La dirección es obligatoria.')
            if not telefono:
                errores.append('El teléfono es obligatorio.')
            if not email:
                errores.append('El email es obligatorio.')
            if not genero:
                errores.append('El género es obligatorio.')

            if errores:
                return render_template('add_estudiante.html', errores=errores)

            conn.execute('''
                INSERT INTO Estudiante (dni_estudiante, nombre, apellido, fecha_nacimiento, direccion, telefono, email, genero)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dni_estudiante, nombre, apellido, fecha_nacimiento, direccion, telefono, email, genero))
            conn.commit()
        
            return redirect(url_for('estudiantes'))
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed: Estudiante.dni_estudiante' in str(e):
                flash('El DNI ya está registrado.', 'danger')
            elif 'UNIQUE constraint failed: Estudiante.email' in str(e):
                flash('El correo electrónico ya está registrado.', 'danger')
            else:
                return handle_error(f'Error al agregar estudiante: {str(e)}', 'add_estudiante.html')
        except Exception as e:
            return handle_error(f'Error al agregar estudiante: {str(e)}', 'add_estudiante.html')
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

            # Validación simple de campos
            errores = []
            if not dni_estudiante:
                errores.append('El DNI es obligatorio.')
            if not nombre:
                errores.append('El nombre es obligatorio.')
            if not apellido:
                errores.append('El apellido es obligatorio.')
            if not fecha_nacimiento:
                errores.append('La fecha de nacimiento es obligatoria.')
            if not direccion:
                errores.append('La dirección es obligatoria.')
            if not telefono:
                errores.append('El teléfono es obligatorio.')
            if not email:
                errores.append('El email es obligatorio.')
            if not genero:
                errores.append('El género es obligatorio.')

            if errores:
                return render_template('edit_estudiante.html', id=id, errores=errores)

            conn.execute('''
                UPDATE Estudiante
                SET dni_estudiante = ?, nombre = ?, apellido = ?, fecha_nacimiento = ?, direccion = ?, telefono = ?, email = ?, genero = ?
                WHERE id_estudiante = ?
            ''', (dni_estudiante, nombre, apellido, fecha_nacimiento, direccion, telefono, email, genero, id))
            conn.commit()
            flash('Estudiante actualizado correctamente.', 'success')
            return redirect(url_for('estudiantes'))
        except Exception as e:
            return handle_error(f'Error al editar estudiante: {str(e)}', 'edit_estudiante.html', id=id)
        finally:
            conn.close()
    else:
        cursor = conn.execute('SELECT * FROM Estudiante WHERE id_estudiante = ?', (id,))
        estudiante = cursor.fetchone()
        conn.close()
        return render_template('edit_estudiante.html', estudiante=estudiante, id=id)

@app.route('/delete_estudiante/<int:id>', methods=['POST'])
def delete_estudiante(id):
    conn = get_db()
    try:
        conn.execute('DELETE FROM Estudiante WHERE id_estudiante = ?', (id,))
        conn.commit()
        flash('Estudiante eliminado correctamente.', 'success')
        return redirect(url_for('estudiantes'))
    except Exception as e:
        return handle_error(f'Error al eliminar estudiante: {str(e)}', 'estudiantes.html')
    finally:
        conn.close()



#----CRUD-pROFESORES----



# Rutas para profesores
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

            # Validación simple de campos
            errores = []
            if not dni_profesor:
                errores.append('El DNI es obligatorio.')
            if not nombre:
                errores.append('El nombre es obligatorio.')
            if not apellido:
                errores.append('El apellido es obligatorio.')
            if not fecha_nacimiento:
                errores.append('La fecha de nacimiento es obligatoria.')
            if not direccion:
                errores.append('La dirección es obligatoria.')
            if not telefono:
                errores.append('El teléfono es obligatorio.')
            if not email:
                errores.append('El email es obligatorio.')
            if not genero:
                errores.append('El género es obligatorio.')

            if errores:
                return render_template('add_profesor.html', errores=errores)

            conn.execute('''
                INSERT INTO Profesor (dni_profesor, nombre, apellido, fecha_nacimiento, direccion, telefono, email, genero)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dni_profesor, nombre, apellido, fecha_nacimiento, direccion, telefono, email, genero))
            conn.commit()
            flash('Profesor agregado correctamente.', 'success')
            return redirect(url_for('profesores'))
        except Exception as e:
            return handle_error(f'Error al agregar profesor: {str(e)}')
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

            # Validación simple de campos
            errores = []
            if not dni_profesor:
                errores.append('El DNI es obligatorio.')
            if not nombre:
                errores.append('El nombre es obligatorio.')
            if not apellido:
                errores.append('El apellido es obligatorio.')
            if not fecha_nacimiento:
                errores.append('La fecha de nacimiento es obligatoria.')
            if not direccion:
                errores.append('La dirección es obligatoria.')
            if not telefono:
                errores.append('El teléfono es obligatorio.')
            if not email:
                errores.append('El email es obligatorio.')
            if not genero:
                errores.append('El género es obligatorio.')

            if errores:
                return render_template('edit_profesor.html', id=id, errores=errores)

            conn.execute('''
                UPDATE Profesor
                SET dni_profesor = ?, nombre = ?, apellido = ?, fecha_nacimiento = ?, direccion = ?, telefono = ?, email = ?, genero = ?
                WHERE id_profesor = ?
            ''', (dni_profesor, nombre, apellido, fecha_nacimiento, direccion, telefono, email, genero, id))
            conn.commit()
            flash('Profesor actualizado correctamente.', 'success')
            return redirect(url_for('profesores'))
        except Exception as e:
            return handle_error(f'Error al editar profesor: {str(e)}')
        finally:
            conn.close()
    else:
        cursor = conn.execute('SELECT * FROM Profesor WHERE id_profesor = ?', (id,))
        profesor = cursor.fetchone()
        conn.close()
        return render_template('edit_profesor.html', profesor=profesor, id=id)

@app.route('/delete_profesor/<int:id>', methods=['POST'])
def delete_profesor(id):
    conn = get_db()
    try:
        conn.execute('DELETE FROM Profesor WHERE id_profesor = ?', (id,))
        conn.commit()
        flash('Profesor eliminado correctamente.', 'success')
        return redirect(url_for('profesores'))
    except Exception as e:
        return handle_error(f'Error al eliminar profesor: {str(e)}')
    finally:
        conn.close()

# Rutas para categorías y cursos
@app.route('/categorias')
def categorias():
    conn = get_db()
    cursor = conn.execute('SELECT * FROM Categoria')
    categorias = cursor.fetchall()
    conn.close()
    return render_template('categorias.html', categorias=categorias)

@app.route('/edit_categoria/<int:id_categoria>', methods=['GET', 'POST'])
def edit_categoria(id_categoria):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        if not nombre:
            flash('El nombre es obligatorio', 'error')
        else:
            cursor.execute('UPDATE Categoria SET nombre = ? WHERE id_categoria = ?', (nombre, id_categoria))
            conn.commit()
            flash('Categoría actualizada exitosamente', 'success')
            return redirect(url_for('categorias'))
    
    cursor.execute('SELECT * FROM Categoria WHERE id_categoria = ?', (id_categoria,))
    categoria = cursor.fetchone()
    if categoria is None:
        flash('Categoría no encontrada', 'error')
        return redirect(url_for('categorias'))
    
    return render_template('edit_categoria.html', categoria=categoria)



@app.route('/cursos/<int:id_categoria>')
def cursos(id_categoria):
    conn = get_db()
    
    # Obtener el nombre de la categoría
    cursor = conn.execute('SELECT nombre FROM Categoria WHERE id_categoria = ?', (id_categoria,))
    categoria = cursor.fetchone()
    
    # Obtener los cursos asociados a la categoría
    cursor = conn.execute('SELECT * FROM Curso WHERE id_categoria = ?', (id_categoria,))
    cursos = cursor.fetchall()
    
    conn.close()
    
    if categoria:
        nombre_categoria = categoria['nombre']
    else:
        nombre_categoria = 'Categoría no encontrada'
    
    return render_template('cursos.html', cursos=cursos, id_categoria=id_categoria, nombre_categoria=nombre_categoria)

@app.route('/add_categoria', methods=['GET', 'POST'])
def add_categoria():
    if request.method == 'POST':
        conn = get_db()
        try:
            nombre = request.form['nombre']
            conn.execute('INSERT INTO Categoria (nombre) VALUES (?)', (nombre,))
            conn.commit()
            flash('Categoría agregada correctamente.', 'success')
            return redirect(url_for('categorias'))
        except Exception as e:
            return handle_error(f'Error al agregar categoría: {str(e)}')
        finally:
            conn.close()
    return render_template('add_categoria.html')

@app.route('/delete_categoria/<int:id>', methods=['POST'])
def delete_categoria(id):
    conn = get_db()
    # Verificar si existen cursos asociados a la categoría
    cursor = conn.execute('SELECT COUNT(*) FROM Curso WHERE id_categoria = ?', (id,))
    cursos_count = cursor.fetchone()[0]
    if cursos_count > 0:
        flash('No se puede eliminar la categoría porque tiene cursos asociados.', 'error')
    else:
        try:
            conn.execute('DELETE FROM Categoria WHERE id_categoria = ?', (id,))
            conn.commit()
            flash('Categoría eliminada correctamente.', 'success')
        except Exception as e:
            flash(f'Error al eliminar categoría: {str(e)}', 'error')
        finally:
            conn.close()
    
    return redirect(url_for('categorias'))






@app.route('/add_curso/<int:id_categoria>', methods=['GET', 'POST'])
def add_curso(id_categoria):
    if request.method == 'POST':
        conn = get_db()
        try:
            nombre_curso = request.form['nombre_curso']
            descripcion = request.form['descripcion']
            conn.execute('''
                INSERT INTO Curso (nombre_curso, descripcion, id_categoria)
                VALUES (?, ?, ?)
            ''', (nombre_curso, descripcion, id_categoria))
            conn.commit()
            flash('Curso agregado correctamente.', 'success')
            return redirect(url_for('cursos', id_categoria=id_categoria))
        except Exception as e:
            return handle_error(f'Error al agregar curso: {str(e)}')
        finally:
            conn.close()
    return render_template('add_curso.html', id_categoria=id_categoria)
    
@app.route('/edit_curso/<int:id_curso>', methods=['GET', 'POST'])
def edit_curso(id_curso):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        nombre_curso = request.form['nombre_curso']
        descripcion = request.form['descripcion']
        if not nombre_curso or not descripcion:
            flash('Todos los campos son obligatorios', 'error')
        else:
            cursor.execute('UPDATE Curso SET nombre_curso = ?, descripcion = ? WHERE id_curso = ?', (nombre_curso, descripcion, id_curso))
            conn.commit()
            flash('Curso actualizado exitosamente', 'success')
            return redirect(url_for('cursos', id_categoria=request.form['id_categoria']))
    
    cursor.execute('SELECT * FROM Curso WHERE id_curso = ?', (id_curso,))
    curso = cursor.fetchone()
    if curso is None:
        flash('Curso no encontrado', 'error')
        return redirect(url_for('categorias'))
    
    return render_template('edit_curso.html', curso=curso)


# Resto de las rutas y funciones existentes...



if __name__ == '__main__':
    app.run(debug=True)