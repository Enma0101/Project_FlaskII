import sqlite3

# Conexión a la base de datos
conn = sqlite3.connect('DataBase.sqlite3')
cursor = conn.cursor()

# Crear tablas
cursor.execute('''
CREATE TABLE IF NOT EXISTS Estudiante (
    id_estudiante INTEGER PRIMARY KEY AUTOINCREMENT,
    dni_estudiante VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    genero CHAR(1) CHECK(genero IN ('M', 'F'))
)
''')
print("Tabla Estudiante creada")

cursor.execute('''
CREATE TABLE IF NOT EXISTS Profesor (
    id_profesor INTEGER PRIMARY KEY AUTOINCREMENT,
    dni_profesor VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    genero CHAR(1) CHECK(genero IN ('M', 'F'))
)
''')
print("Tabla Profesor creada")

cursor.execute('''
CREATE TABLE IF NOT EXISTS Curso (
    id_curso INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_curso VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    id_categoria INTEGER,
    FOREIGN KEY(id_categoria) REFERENCES Categoria(id_categoria) ON DELETE RESTRICT
)
''')
print("Tabla Curso creada")

cursor.execute('''
CREATE TABLE IF NOT EXISTS Matricula (
    id_matricula INTEGER PRIMARY KEY AUTOINCREMENT,
    id_estudiante INTEGER,
    id_curso INTEGER,
    fecha_matricula VARCHAR(10) NOT NULL,
    FOREIGN KEY(id_estudiante) REFERENCES Estudiante(id_estudiante) ON DELETE CASCADE,
    FOREIGN KEY(id_curso) REFERENCES Curso(id_curso) ON DELETE CASCADE
)
''')
print("Tabla Matricula creada")

cursor.execute('''
CREATE TABLE IF NOT EXISTS NotaFinal (
    id_nota_final INTEGER PRIMARY KEY AUTOINCREMENT,
    id_matricula INTEGER,
    nota_final DECIMAL(5,2) NOT NULL,
    
    FOREIGN KEY(id_matricula) REFERENCES Matricula(id_matricula) ON DELETE RESTRICT
)
''')
print("Tabla NotaFinal creada")

cursor.execute('''
CREATE TABLE IF NOT EXISTS Categoria (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL
)
''')
print("Tabla Categoria creada")

cursor.execute('''
CREATE TABLE IF NOT EXISTS CursoProfesor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_curso INTEGER NOT NULL,
    id_profesor INTEGER NOT NULL,
    FOREIGN KEY(id_curso) REFERENCES Curso(id_curso) ON DELETE CASCADE,
    FOREIGN KEY(id_profesor) REFERENCES Profesor(id_profesor) ON DELETE CASCADE
)
''')
print("Tabla CursoProfesor creada")

# Confirmar los cambios
conn.commit()

# Cerrar la conexión
conn.close()
print("Conexión cerrada")