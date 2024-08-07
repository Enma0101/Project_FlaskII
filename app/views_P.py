from flask import Flask, render_template, request, g, redirect, url_for, flash, jsonify, send_file
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle 
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image , Spacer
from reportlab.lib.units import inch
import reportlab.rl_config
import os
import sqlite3
import io
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'
DATABASE = 'DataBase.sqlite3'

# Función para obtener la conexión a la base de datos
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON;")
        db.commit()
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

        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed: Estudiante.dni_estudiante' in str(e):
                flash('El DNI ya está registrado.', 'danger')
            elif 'UNIQUE constraint failed: Estudiante.email' in str(e):
                flash('Error al actualizarlo el correo electrónico ya está registrado.', 'danger')
            else:
                flash(f'Error al editar Estudiante: {str(e)}', 'danger')
        
        except Exception as e:
            flash(f'Error al editar Estudiante: {str(e)}', 'danger')

        finally:
            conn.close()

    else:  # GET request
        try:
            cursor = conn.execute('SELECT * FROM Estudiante WHERE id_estudiante = ?', (id,))
            estudiante = cursor.fetchone()
            
            if not estudiante:
                flash('Estudiante no encontrado.', 'danger')
                return redirect(url_for('estudiantes'))
            
            return render_template('edit_estudiante.html', estudiante=estudiante, id=id)

        except Exception as e:
            flash(f'Error al buscar Estudiante: {str(e)}', 'danger')

        finally:
            conn.close()

    return redirect(url_for('estudiantes'))


@app.route('/delete_estudiante/<int:id>', methods=['POST'])
def delete_estudiante(id):
    conn = get_db()
    try:
        conn.execute('DELETE FROM Estudiante WHERE id_estudiante = ?', (id,))
        conn.commit()
        
        return redirect(url_for('estudiantes'))
    except Exception as e:
        return handle_error(f'Error al eliminar estudiante: {str(e)}', 'estudiantes.html')
    finally:
        conn.close()



#----CRUD-pROFESORES----

@app.route('/profesor/<int:id>/cursos_asignados')
def profesor_cursos_asignados(id):
    conn = get_db()
    try:
        cursor = conn.execute('SELECT nombre, apellido FROM Profesor WHERE id_profesor = ?', (id,))
        profesor = cursor.fetchone()
        if not profesor:
            return handle_error('Profesor no encontrado.', 'profesor_cursos.html', profesor=None, cursos=[], id=id)

        cursor = conn.execute('''
            SELECT Curso.id_curso, Curso.nombre_curso, Curso.descripcion
            FROM Curso
            JOIN CursoProfesor ON Curso.id_curso = CursoProfesor.id_curso
            WHERE CursoProfesor.id_profesor = ?
        ''', (id,))
        cursos = cursor.fetchall()
    except Exception as e:
        return handle_error(f'Error al obtener los cursos asignados al profesor: {str(e)}', 'profesor_cursos.html', profesor=None, cursos=[], id=id)
    finally:
        conn.close()

    return render_template('profesor_cursos.html', profesor=profesor, cursos=cursos, id=id)

@app.route('/delete_asignacion/<int:id_profesor>/<int:id_curso>', methods=['POST'])
def eliminar_asignacion(id_profesor, id_curso):
    conn = get_db()
    try:
        conn.execute('DELETE FROM CursoProfesor WHERE id_profesor = ? AND id_curso = ?', (id_profesor, id_curso))
        conn.commit()
        flash('Asignación eliminada correctamente.', 'success')
    except Exception as e:
        return handle_error(f'Error al eliminar la asignación: {str(e)}', 'profesor_cursos.html', profesor=None, cursos=[], id=id_profesor)
    finally:
        conn.close()
    return redirect(url_for('profesor_cursos_asignados', id=id_profesor))

@app.route('/profesores')
def profesores():
    conn = get_db()
    cursor = conn.execute('SELECT * FROM Profesor')
    profesores = cursor.fetchall()
    conn.close()
    return render_template('profesores.html', profesores=profesores)

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

            return redirect(url_for('profesores'))
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed: Profesor.dni_profesor' in str(e):
                flash('El DNI ya está registrado.', 'danger')
            elif 'UNIQUE constraint failed: Profesor.email' in str(e):
                flash('El correo electrónico ya está registrado.', 'danger')
            else:
                flash(f'Error al agregar profesor: {str(e)}', 'danger')
        except Exception as e:
            flash(f'Error al agregar profesor: {str(e)}', 'danger')
        finally:
            conn.close()
    return render_template('add_profesor.html')

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
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed: Profesor.dni_profesor' in str(e):
                flash('El DNI ya está registrado.', 'danger')
            elif 'UNIQUE constraint failed: Profesor.email' in str(e):
                flash('Error al actualizarlo el correo electrónico ya está registrado.', 'danger')
            else:
                flash(f'Error al editar profesor: {str(e)}', 'danger')
        except Exception as e:
            flash(f'Error al editar profesor: {str(e)}', 'danger')
        finally:
            conn.close()

    else:
        try:
            cursor = conn.execute('SELECT * FROM Profesor WHERE id_profesor = ?', (id,))
            profesor = cursor.fetchone()
            if not profesor:
                flash('Profesor no encontrado.', 'danger')
                return redirect(url_for('profesores'))
            
            return render_template('edit_profesor.html', profesor=profesor, id=id)
        except Exception as e:
            flash(f'Error al buscar profesor: {str(e)}', 'danger')
        finally:
            conn.close()

    return redirect(url_for('profesores'))


@app.route('/delete_profesor/<int:id>', methods=['POST'])
def delete_profesor(id):
    conn = get_db()
    try:
        conn.execute('DELETE FROM Profesor WHERE id_profesor = ?', (id,))
        conn.commit()
        flash('Profesor eliminado correctamente.', 'success')
        return redirect(url_for('profesores'))
    except Exception as e:
        flash(f'Error al eliminar profesor: {str(e)}', 'profesores.html')
    finally:
        conn.close()

def handle_error(error_message, template, **kwargs):
    flash(error_message, 'danger')
    return render_template(template, **kwargs)

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

@app.route('/delete_curso/<int:id_curso>', methods=['POST'])
def delete_curso(id_curso):
    conn = get_db()
    try:
        # Verificar si hay estudiantes inscritos en el curso
        cursor = conn.execute('SELECT COUNT(*) FROM Matricula WHERE id_curso = ?', (id_curso,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            # Hay estudiantes inscritos, no se puede eliminar el curso
            flash('No se puede eliminar el curso porque tiene estudiantes inscritos.', 'error')
        else:
            # No hay estudiantes inscritos, proceder con la eliminación
            conn.execute('DELETE FROM Curso WHERE id_curso = ?', (id_curso,))
            conn.commit()
            flash('Curso eliminado correctamente.', 'success')
    except Exception as e:
        flash(f'Error al eliminar curso: {str(e)}', 'error')
    finally:
        conn.close()
    
        return redirect(url_for('cursos', id_categoria=request.form['id_categoria']))


# Resto de las rutas y funciones existentes...
#Matricula
@app.route('/matricula', methods=['GET', 'POST'])
def matricula():
    conn = get_db()
    if request.method == 'POST':
        try:
            dni_estudiante = request.form['dni_estudiante']
            id_curso = request.form['id_curso']
            fecha_matricula = request.form['fecha_matricula']

            # Chequear si estudiante esta inscrito en el curso
            cursor = conn.execute('''
                SELECT id_estudiante FROM Matricula 
                WHERE id_estudiante = (SELECT id_estudiante FROM Estudiante WHERE dni_estudiante = ?)
                AND id_curso = ?
            ''', (dni_estudiante, id_curso))
            existing_matricula = cursor.fetchone()

            if existing_matricula:
                flash('Este estudiante ya está matriculado en este curso.', 'error')
                return redirect(url_for('matricula'))

            # Obtener el ID del estudiante usando el DNI
            cursor = conn.execute('SELECT id_estudiante FROM Estudiante WHERE dni_estudiante = ?', (dni_estudiante,))
            estudiante = cursor.fetchone()
            if estudiante:
                id_estudiante = estudiante['id_estudiante']

                # Insertar la matrícula en la base de datos
                conn.execute('''
                    INSERT INTO Matricula (id_estudiante, id_curso, fecha_matricula)
                    VALUES (?, ?, ?)
                ''', (id_estudiante, id_curso, fecha_matricula))
                conn.commit()
                flash('Matrícula realizada con éxito!', 'success')
                return redirect(url_for('matricula'))
            else:
                flash('No se encontró ningún estudiante con el DNI proporcionado.', 'error')
                return redirect(url_for('matricula'))
        except Exception as e:
            flash(f'Error al registrar matrícula: {str(e)}', 'error')
            return redirect(url_for('matricula'))
        finally:
            conn.close()
    else:
        estudiantes = conn.execute('SELECT id_estudiante, dni_estudiante, nombre || " " || apellido as nombre_completo FROM Estudiante').fetchall()
        categorias = conn.execute('SELECT id_categoria, nombre FROM Categoria').fetchall()
        cursos = conn.execute('SELECT id_curso, nombre_curso FROM Curso').fetchall()
        conn.close()
        return render_template('matricula.html', estudiantes=estudiantes, categorias=categorias, cursos=cursos)

@app.route('/get_student_name_by_dni/<dni>', methods=['GET'])
def get_student_name_by_dni(dni):
    conn = get_db()
    cursor = conn.execute('SELECT nombre, apellido FROM Estudiante WHERE dni_estudiante = ?', (dni,))
    estudiante = cursor.fetchone()
    conn.close()
    if estudiante:
        nombre_completo = f"{estudiante['nombre']} {estudiante['apellido']}"
        return jsonify({'nombre_completo': nombre_completo})
    else:
        return jsonify({'nombre_completo': None})

@app.route('/matriculas')
def matriculas():
    conn = get_db()
    cursor = conn.execute('''
        SELECT m.id_matricula, e.nombre as estudiante, c.nombre_curso as curso, m.fecha_matricula
        FROM Matricula m
        JOIN Estudiante e ON m.id_estudiante = e.id_estudiante
        JOIN Curso c ON m.id_curso = c.id_curso  
    ''')
    matriculas = cursor.fetchall()
    conn.close()
    return render_template('matriculas.html', matriculas=matriculas)


#Asignar notas
@app.route('/asignar_nota', methods=['GET', 'POST'])
def asignar_nota():
    if request.method == 'POST':
        try:
            conn = get_db()
            dni_estudiante = request.form['id_estudiante']
            id_curso = request.form['id_curso']
            nota = request.form['nota']
            
            # Buscar id_estudiante a partir del DNI
            cursor = conn.execute('''
                SELECT id_estudiante
                FROM Estudiante
                WHERE dni_estudiante = ?
            ''', (dni_estudiante,))
            estudiante = cursor.fetchone()

            if not estudiante:
                flash('Estudiante no encontrado', 'error')
                conn.close()
                return redirect(url_for('asignar_nota'))

            id_estudiante = estudiante[0]
            
            # Buscar id_matricula en función del id_estudiante y id_curso
            cursor = conn.execute('''
                SELECT id_matricula
                FROM Matricula
                WHERE id_estudiante = ? AND id_curso = ?
            ''', (id_estudiante, id_curso))
            matricula = cursor.fetchone()

            if not matricula:
                flash('No se encontró matrícula para el estudiante y curso seleccionados', 'error')
                conn.close()
                return redirect(url_for('asignar_nota'))

            id_matricula = matricula[0]

            # Verificar si ya existe una nota para esta matrícula
            cursor = conn.execute('''
                SELECT id_nota_final
                FROM NotaFinal
                WHERE id_matricula = ?
            ''', (id_matricula,))
            nota_existente = cursor.fetchone()

            #Editar nota
            if nota_existente:
                conn.execute('''
                    UPDATE NotaFinal
                    SET nota_final = ?
                    WHERE id_matricula = ?
                ''', (nota, id_matricula))
                conn.commit()
                flash('Nota actualizada correctamente', 'success')
                
            else:
                conn.execute('''
                    INSERT INTO NotaFinal (id_matricula, nota_final)
                    VALUES (?, ?)
                ''', (id_matricula, nota))
                conn.commit()
                flash('Nota agregada correctamente', 'success')

            conn.close()
            return redirect(url_for('asignar_nota'))
        except Exception as e:
            flash(f'Error al asignar nota: {str(e)}', 'error')
            return redirect(url_for('asignar_nota'))
    else:
        conn = get_db()
        estudiantes = conn.execute('SELECT id_estudiante, dni_estudiante, nombre, apellido FROM Estudiante').fetchall()
        categorias = conn.execute('SELECT id_categoria, nombre FROM Categoria').fetchall()
        cursos = conn.execute('SELECT id_curso, nombre_curso FROM Curso').fetchall()
        nota_existente = None
        conn.close()
        return render_template('asignar_nota.html', estudiantes=estudiantes, cursos=cursos, categorias=categorias, nota_existente=nota_existente)


@app.route('/get_categories', methods=['GET'])
def get_categories():
    conn = get_db()
    cursor = conn.execute('SELECT id_categoria, nombre FROM Categoria')
    categories = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in categories])

@app.route('/get_courses/<int:category_id>', methods=['GET'])
def get_courses(category_id):
    if category_id <= 0:
        return jsonify([])
    try:
        conn = get_db()
        cursor = conn.execute('SELECT id_curso, nombre_curso FROM Curso WHERE id_categoria = ?', (category_id,))
        courses = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in courses])
    except Exception as e:
        print(f"Error fetching courses: {str(e)}")
        return jsonify({"error": "Error fetching courses"}), 500
    
def get_students(course_id):
    conn = get_db()
    cursor = conn.execute('''
        SELECT e.id_estudiante, e.dni_estudiante, e.nombre, e.apellido 
        FROM Estudiante e
        JOIN Matricula m ON e.id_estudiante = m.id_estudiante
        WHERE m.id_curso = ?
    ''', (course_id,))
    students = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in students])

## para asignar un curso a un profesor 
@app.route('/get_profesor_by_dni/<dni>', methods=['GET'])
def get_profesor_by_dni(dni):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id_profesor, nombre, apellido FROM Profesor WHERE dni_profesor = ?", (dni,))
    profesor = cursor.fetchone()
    cursor.close()

    if profesor:
        return jsonify({
            'id_profesor': profesor[0],
            'nombre_completo': f"{profesor[1]} {profesor[2]}"
        })
    else:
        return jsonify({'nombre_completo': None})

@app.route('/get_cursos_by_categoria/<int:categoria_id>', methods=['GET'])
def get_cursos_by_categoria(categoria_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id_curso, nombre_curso FROM Curso WHERE id_categoria = ?", (categoria_id,))
    cursos = cursor.fetchall()
    cursor.close()

    return jsonify({'cursos': [{'id_curso': curso[0], 'nombre_curso': curso[1]} for curso in cursos]})

@app.route('/asignar_curso', methods=['GET', 'POST'])
def asignar_curso():
    conn = get_db()
    if request.method == 'POST':
        dni_profesor = request.form['dni_profesor']
        id_curso = request.form['id_curso']

        cursor = conn.cursor()
        cursor.execute("SELECT id_profesor FROM Profesor WHERE dni_profesor = ?", (dni_profesor,))
        profesor = cursor.fetchone()

        if not profesor:
            flash('Profesor no encontrado', 'danger')
            return redirect(url_for('asignar_curso'))

        id_profesor = profesor[0]

        try:
            # Verificar si la asignación ya existe
            cursor.execute("SELECT * FROM CursoProfesor WHERE id_profesor = ? AND id_curso = ?", (id_profesor, id_curso))
            if cursor.fetchone() is not None:
                flash('Este curso ya ha sido asignado a este profesor.', 'danger')
            else:
                # Insertar la nueva asignación
                cursor.execute("INSERT INTO CursoProfesor (id_curso, id_profesor) VALUES (?, ?)", (id_curso, id_profesor))
                conn.commit()
                flash('Curso asignado exitosamente.', 'success')
        except Exception as e:
            conn.rollback()
            flash(str(e), 'danger')
        finally:
            cursor.close()

        return redirect(url_for('asignar_curso'))

    # Obtener las categorías para el formulario
    cursor = conn.cursor()
    cursor.execute("SELECT id_categoria, nombre FROM Categoria")
    categorias = cursor.fetchall()
    cursor.close()

    return render_template('asignar_curso.html', categorias=categorias)


#Certificado

@app.route('/certificados')
def certificado():
    return render_template('certificados.html')

@app.route('/obtener_estudiante')
def obtener_estudiante():
    dni_estudiante = request.args.get('dni_estudiante')
    conn = get_db()
    cursor = conn.cursor()
    estudiante = cursor.execute('''
        SELECT nombre, apellido
        FROM Estudiante
        WHERE dni_estudiante = ?
    ''', (dni_estudiante,)).fetchone()
    conn.close()

    if estudiante:
        nombre_completo = f"{estudiante['nombre']} {estudiante['apellido']}"
        return jsonify({'nombre': nombre_completo})
    else:
        return jsonify({'error': 'Estudiante no encontrado'}), 404

@app.route('/obtener_cursos')
def obtener_cursos():
    dni_estudiante = request.args.get('dni_estudiante')
    conn = get_db()
    cursor = conn.cursor()
    cursos = cursor.execute('''
        SELECT Curso.id_curso, Curso.nombre_curso
        FROM Matricula
        JOIN Curso ON Matricula.id_curso = Curso.id_curso
        JOIN Estudiante ON Matricula.id_estudiante = Estudiante.id_estudiante
        WHERE Estudiante.dni_estudiante = ?
    ''', (dni_estudiante,)).fetchall()
    conn.close()

    if cursos:
        cursos_list = [{'id_curso': curso['id_curso'], 'nombre_curso': curso['nombre_curso']} for curso in cursos]
        return jsonify(cursos_list)
    else:
        return jsonify({'error': 'No se encontraron cursos para este estudiante'}), 404

views_folder = os.path.join(os.getcwd(), 'app', 'static')
pdf_template_path = os.path.join(views_folder, 'certificado_template.pdf')

@app.route('/generar_certificado', methods=['POST'])
def generar_certificado():
    dni_estudiante = request.form['dni_estudiante']
    id_curso = request.form['id_curso']
    conn = get_db()
    cursor = conn.cursor()

    try:
        estudiante = cursor.execute('''
            SELECT nombre, apellido
            FROM Estudiante
            WHERE dni_estudiante = ?
        ''', (dni_estudiante,)).fetchone()
        
        curso = cursor.execute('''
            SELECT nombre_curso
            FROM Curso
            WHERE id_curso = ?
        ''', (id_curso,)).fetchone()
        
        matricula = cursor.execute('''
            SELECT fecha_matricula
            FROM Matricula
            WHERE id_estudiante = (
                SELECT id_estudiante
                FROM Estudiante
                WHERE dni_estudiante = ?
            )
            AND id_curso = ?
        ''', (dni_estudiante, id_curso)).fetchone()
        
        nota_final = cursor.execute('''
            SELECT nota_final
            FROM NotaFinal
            WHERE id_matricula = (
                SELECT id_matricula
                FROM Matricula
                WHERE id_estudiante = (
                    SELECT id_estudiante
                    FROM Estudiante
                    WHERE dni_estudiante = ?
                )
                AND id_curso = ?
            )
        ''', (dni_estudiante, id_curso)).fetchone()
        
        conn.close()
        
        if estudiante and curso and matricula and nota_final:
            nota = nota_final[0]
            
            if nota is None:
                return jsonify({'error': 'No se encontró nota final para el estudiante y curso seleccionados.'}), 400

            if nota < 10:
                return jsonify({'error': 'La nota final del estudiante es menor a 10. No se puede generar el certificado.'}), 400
            
            # Obtener la fecha actual
            fecha_actual = datetime.now().strftime("%d/%m/%Y")
            
            # Registrar fuentes
            pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf')) 
            pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))     
            pdfmetrics.registerFont(TTFont('VeraBI', 'VeraBI.ttf'))
            
            # Generar el PDF con ReportLab
            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=letter)
            
            # Configuración de fuente y color
            c.setFillColorRGB(139/255, 119/255, 40/255)  # Color dorado
            c.setFont('VeraBd',30)
            
            # Dibujar el texto en el PDF
            c.drawCentredString(422, 280, f"{estudiante['nombre']} {estudiante['apellido']}")
            c.drawString(240, 170, curso['nombre_curso'])
            c.setFont('Vera', 15)
            c.drawString(520, 105, fecha_actual) 
            
            c.setFont('Vera', 8)
            c.save()
            
            # Mover el cursor al inicio del "archivo"
            packet.seek(0)
            
            # Crear un nuevo PDF a partir del template
            existing_pdf = PdfReader(open(pdf_template_path, "rb"))
            new_pdf = PdfReader(packet)
            
            output = PdfWriter()
            page = existing_pdf.pages[0]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)
            
            # Guardar el PDF generado en la carpeta 'static'
            output_filename = f"certificado_{estudiante['nombre'].replace(' ', '_')}.pdf"
            output_path = os.path.join(os.getcwd(), 'app', 'static', 'certificados', output_filename)
            
            with open(output_path, "wb") as outputStream:
                output.write(outputStream)
            
            # Enviar el archivo como respuesta
            return send_file(output_path, as_attachment=True, download_name=output_filename, mimetype='application/pdf')
        
        else:
            return jsonify({'error': 'Estudiante, curso o matrícula no encontrados'}), 400

    except Exception as e:
        return jsonify({'error': f'Error al generar el certificado: {str(e)}'}), 500


#Reportes Estudiantes 
@app.route('/buscar_estudiante', methods=['GET', 'POST'])
def buscar_estudiante():
    if request.method == 'POST':
        dni_estudiante = request.form['dni_estudiante']
        return redirect(url_for('generar_reporte', dni_estudiante=dni_estudiante))
    return render_template('buscar_estudiante.html')

@app.route('/get_estudiante_by_dni/<dni>')
def get_estudiante_by_dni(dni):
    conn = get_db()
    try:
        cursor = conn.execute('SELECT id_estudiante, nombre, apellido FROM Estudiante WHERE dni_estudiante = ?', (dni,))
        estudiante = cursor.fetchone()
        if estudiante:
            return jsonify({
                'id_estudiante': estudiante['id_estudiante'],
                'nombre_completo': f"{estudiante['nombre']} {estudiante['apellido']}"
            })
        return jsonify({}), 404
    except Exception as e:
        print(f"Error al buscar estudiante: {str(e)}")
        return jsonify({}), 500
    finally:
        conn.close()

@app.route('/generar_reporte/<string:dni_estudiante>', methods=['GET'])
def generar_reporte(dni_estudiante):
    conn = get_db()
    try:
        # Obtener información del estudiante
        cursor = conn.execute('''
            SELECT *, strftime('%Y', 'now') - strftime('%Y', fecha_nacimiento) AS edad FROM Estudiante WHERE dni_estudiante = ?
        ''', (dni_estudiante,))
        estudiante = cursor.fetchone()

        if not estudiante:
            flash('Estudiante no encontrado.', 'error')
            return redirect(url_for('buscar_estudiante'))

        # Obtener cursos y notas del estudiante
        cursor = conn.execute('''
            SELECT c.nombre_curso, nf.nota_final
            FROM Matricula m
            JOIN Curso c ON m.id_curso = c.id_curso
            LEFT JOIN NotaFinal nf ON m.id_matricula = nf.id_matricula
            WHERE m.id_estudiante = ?
        ''', (estudiante['id_estudiante'],))
        cursos = cursor.fetchall()

        # Generar PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            alignment=1,  # Center alignment
            textColor=colors.HexColor('#dbdddc'),  # Black text color
            fontSize=18
        )

        # Title
        elements.append(Paragraph("Wizarding Academy Hub", title_style))

        # Spacer
        elements.append(Spacer(1, 1 * inch))

        # Información del estudiante
        genero_texto = "Masculino" if estudiante['genero'] == 'M' else "Femenino"
        data = [
            ["Información del Estudiante", " "],
            ["Nombre", f"{estudiante['nombre']} {estudiante['apellido']}"],
            ["DNI", estudiante['dni_estudiante']],
            ["Email", estudiante['email']],
            ["Edad", str(estudiante['edad'])],  # Agregado edad
            ["Género", genero_texto],
        ]

        # Tabla de cursos y notas
        if cursos:
            course_data = [["Curso", "Nota Final"]]
            for curso in cursos:
                course_data.append([curso['nombre_curso'], curso['nota_final'] if curso['nota_final'] else 'Sin nota'])
        else:
            course_data = [["Curso", "Nota Final"], ["No hay cursos asignados", ""]]

        # Crear tablas
        info_table = Table(data, colWidths=[150, 300])
        course_table = Table(course_data, colWidths=[225, 225])

        # Estilizar las tablas
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d3a625')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#ffffff')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#444444')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#f3f6f4')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
            ('GRID', (0, 1), (-1, -1), 1, colors.HexColor('#363434')),
            ('SPAN', (0, 0), (-1, 0)),  # Fusiona las celdas de la primera fila
            ('LINEABOVE', (0, 1), (-1, 1), 1, colors.HexColor('#5b5b5b')),  # Añade una línea encima de la segunda fila
        ]))

        course_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d3a625')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#ffffff')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#444444')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#f3f6f4')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#363434'))
        ]))

        elements.append(info_table)
        elements.append(Spacer(1, 0.5 * inch))  # Agregar espacio entre tablas
        elements.append(course_table)

        # Construir el PDF con la función de layout personalizada
        doc.build(elements, onFirstPage=lambda canvas, doc: add_page_layout1(canvas, doc ))

        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=f"reporte_{dni_estudiante}.pdf", mimetype='application/pdf')

    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('buscar_estudiante'))
    finally:
        conn.close()

def add_page_layout1(canvas, doc):
    # Set background color
    canvas.setFillColorRGB(116/255, 0/255, 1/255)  # Dark green background
    canvas.rect(0, 0, doc.width + 2 * doc.leftMargin, doc.height + 2 * doc.bottomMargin, stroke=0, fill=1)

    # Set logo path and position
    logo_path = os.path.join(app.root_path, 'static', 'Imagen_Gryffindor.png')
    logo = Image(logo_path, width=1.5*inch, height=1.7*inch)
    
    # Adjust y-coordinate to move the image down
    y_position = doc.height + doc.bottomMargin - 1*inch  # Adjust this value to move the image down
    logo.drawOn(canvas, doc.width + doc.leftMargin - 1*inch, y_position)




     #buscar -- Profesor   

@app.route('/buscar_profesor', methods=['GET', 'POST'])
def buscar_profesor():
    if request.method == 'POST':
        dni_profesor = request.form['dni_profesor']
        return redirect(url_for('generar_reporte_profesor', dni_profesor=dni_profesor))
    return render_template('buscar_profesor.html')

@app.route('/get_profesor_por_dni/<string:dni>')
def get_profesor_por_dni(dni):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id_profesor, nombre, apellido FROM profesor WHERE dni_profesor = ?', (dni,))
    profesor = cursor.fetchone()
    conn.close()

    if profesor:
        return jsonify({
            'id_profesor': profesor['id_profesor'],
            'nombre_completo': f"{profesor['nombre']} {profesor['apellido']}"
        })
    else:
        return jsonify({}), 404


@app.route('/generar_reporte_profesor', methods=['POST'])
def generar_reporte_profesor():
    dni_profesor = request.form['dni_profesor']
    conn = get_db()
    try:
        # Obtener información del profesor
        cursor = conn.execute('''
            SELECT id_profesor, dni_profesor, nombre, apellido, email, 
                   strftime('%Y', 'now') - strftime('%Y', fecha_nacimiento) AS edad, 
                   genero 
            FROM Profesor 
            WHERE dni_profesor = ?
        ''', (dni_profesor,))
        profesor = cursor.fetchone()

        if not profesor:
            flash('Profesor no encontrado.', 'error')
            return redirect(url_for('buscar_profesor'))

        # Obtener cursos asignados
        cursor = conn.execute('''
            SELECT c.nombre_curso, cat.nombre AS categoria
            FROM CursoProfesor cp
            JOIN Curso c ON cp.id_curso = c.id_curso
            JOIN Categoria cat ON c.id_categoria = cat.id_categoria
            WHERE cp.id_profesor = ?
        ''', (profesor['id_profesor'],))
        cursos = cursor.fetchall()

        # Generar PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            alignment=1,  # Center alignment
            textColor=colors.HexColor('#dbdddc'),  # Black text color
            fontSize=18
        )

        # Title
        elements.append(Paragraph("Wizarding Academy Hub", title_style))

        # Spacer
        elements.append(Spacer(1, 1 * inch))

        # Profesor information
        genero_texto = "Masculino" if profesor['genero'] == 'M' else "Femenino"
        data = [
            ["Información del Profesor", ""],
            ["Nombre ", f"{profesor['nombre']} {profesor['apellido']}"],
            ["DNI:", profesor['dni_profesor']],
            ["Email:", profesor['email']],
            ["Edad:", str(profesor['edad'])],
            ["Genero:", genero_texto],
        ]

        # Cursos table
        if cursos:
            course_data = [["Cursos Asignados:", ""]]
            for curso in cursos:
                course_data.append([curso['categoria'], curso['nombre_curso']])
        else:
            course_data = [["Cursos Asignados:", "No tiene cursos asignados"]]

        # Create tables
        info_table = Table(data, colWidths=[150, 300])
        course_table = Table(course_data, colWidths=[225, 225])

        # Style the tables
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a472a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#ffffff')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#444444')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#f3f6f4')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
            ('GRID', (0, 1), (-1, -1), 1, colors.HexColor('#363434')),
            ('SPAN', (0, 0), (-1, 0)),  # Fusiona las celdas de la primera fila
            ('LINEABOVE', (0, 1), (-1, 1), 1, colors.HexColor('#5b5b5b')),  # Añade una línea encima de la segunda fila
        ]))

        course_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a472a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#ffffff')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#444444')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#f3f6f4')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
            ('GRID', (0, 1), (-1, -1), 1, colors.HexColor('#363434')),
            ('SPAN', (0, 0), (-1, 0)),  # Fusiona las celdas de la primera fila
            ('LINEABOVE', (0, 1), (-1, 1), 1, colors.HexColor('#5b5b5b')),  # Añade una línea encima de la segunda fila
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.5 * inch))  # Add space between tables
        elements.append(course_table)

        # Build the PDF
        doc.build(elements, onFirstPage=add_page_layout)

        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=f"reporte_{dni_profesor}.pdf", mimetype='application/pdf')

    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('buscar_profesor'))
    finally:
        conn.close()

def add_page_layout(canvas, doc):
    # Set background color
    canvas.setFillColorRGB(26/255, 71/255, 42/255)  # Dark green background
    canvas.rect(0, 0, doc.width + 2 * doc.leftMargin, doc.height + 2 * doc.bottomMargin, stroke=0, fill=1)

    # Set logo path and position
    logo_path = os.path.join(app.root_path, 'static', 'Imagen_Slytherin.png')
    logo = Image(logo_path, width=1.5*inch, height=1.7*inch)
    
    # Adjust y-coordinate to move the image down
    y_position = doc.height + doc.bottomMargin - 1*inch  # Adjust this value to move the image down
    logo.drawOn(canvas, doc.width + doc.leftMargin - 1*inch, y_position)



if __name__ == '__main__':
    app.run(debug=True)