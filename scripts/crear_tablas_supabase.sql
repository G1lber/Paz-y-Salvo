-- =========================================================
-- SCRIPT PARA CREAR TABLAS DE PAZ Y SALVO EN SUPABASE (PG)
-- Copia y pega esto en el SQL Editor de Supabase
-- =========================================================

CREATE TABLE IF NOT EXISTS mainapp_centro (
    id SERIAL PRIMARY KEY,
    nombre_centro VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS mainapp_roles (
    id SERIAL PRIMARY KEY,
    nombre_rol VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS mainapp_tipodoc (
    id SERIAL PRIMARY KEY,
    nombre_tipo VARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS mainapp_programa (
    id_programa SERIAL PRIMARY KEY,
    nombre_programa VARCHAR(150) NOT NULL,
    tipo_programa VARCHAR(10) NOT NULL DEFAULT 'tecnico',
    id_centro_fk_id INTEGER REFERENCES mainapp_centro(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mainapp_ficha (
    num_ficha VARCHAR(50) PRIMARY KEY,
    fecha_inicio DATE,
    fecha_fin DATE,
    programa_fk_id INTEGER REFERENCES mainapp_programa(id_programa) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS mainapp_usuario (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200),
    apellidos VARCHAR(100),
    num_doc INTEGER NOT NULL UNIQUE,
    id_tipodoc_fk_id INTEGER REFERENCES mainapp_tipodoc(id) ON DELETE SET NULL,
    id_rol_fk_id INTEGER REFERENCES mainapp_roles(id) ON DELETE SET NULL,
    id_ficha_fk_id VARCHAR(50) REFERENCES mainapp_ficha(num_ficha) ON DELETE SET NULL,
    datos_actualizados BOOLEAN NOT NULL DEFAULT FALSE,
    resultados BOOLEAN NOT NULL DEFAULT FALSE,
    tyt BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS mainapp_login (
    id SERIAL PRIMARY KEY,
    id_usuario_fk_id INTEGER NOT NULL UNIQUE REFERENCES mainapp_usuario(id) ON DELETE CASCADE,
    password VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS mainapp_pazysalvo (
    id SERIAL PRIMARY KEY,
    lugar_diligen VARCHAR(200) NOT NULL,
    fecha_diligen DATE NOT NULL,
    id_centro_fk_id INTEGER REFERENCES mainapp_centro(id) ON DELETE CASCADE,
    regional VARCHAR(100),
    tramite VARCHAR(200),
    id_usuario_fk_id INTEGER REFERENCES mainapp_usuario(id) ON DELETE CASCADE,
    firma_responsable VARCHAR(200),
    observaciones VARCHAR(200),
    firma_certificacion VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS mainapp_controlpazysalvo (
    id_control SERIAL PRIMARY KEY,
    id_usuario_fk_id INTEGER REFERENCES mainapp_usuario(id) ON DELETE CASCADE,
    id_ficha_fk_id VARCHAR(50) REFERENCES mainapp_ficha(num_ficha) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mainapp_reportecoordinacion (
    id SERIAL PRIMARY KEY,
    id_usuario_fk_id INTEGER NOT NULL REFERENCES mainapp_usuario(id) ON DELETE CASCADE,
    id_ficha_fk_id VARCHAR(50) NOT NULL REFERENCES mainapp_ficha(num_ficha) ON DELETE CASCADE,
    paz_y_salvo BOOLEAN NOT NULL DEFAULT FALSE,
    observaciones TEXT
);

CREATE TABLE IF NOT EXISTS mainapp_prestarequipos (
    id SERIAL PRIMARY KEY,
    id_usuario_fk_id INTEGER REFERENCES mainapp_usuario(id) ON DELETE CASCADE,
    nombre_equipo VARCHAR(100) NOT NULL,
    fecha_prestamo DATE NOT NULL,
    fecha_devolucion DATE,
    observaciones TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
    CONSTRAINT chk_estado CHECK (estado IN ('Pendiente', 'Activo', 'Vencido'))
);

CREATE TABLE IF NOT EXISTS mainapp_registrohoras (
    id SERIAL PRIMARY KEY,
    id_usuario_fk_id INTEGER REFERENCES mainapp_usuario(id) ON DELETE CASCADE,
    cantidad_horas INTEGER NOT NULL CHECK (cantidad_horas >= 0),
    fecha_registro DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS mainapp_prestamolibro (
    id SERIAL PRIMARY KEY,
    id_usuario_fk_id INTEGER REFERENCES mainapp_usuario(id) ON DELETE CASCADE,
    titulo_libro VARCHAR(200) NOT NULL,
    fecha_prestamo DATE NOT NULL,
    centro_formacion VARCHAR(200),
    tipo_material VARCHAR(100),
    tiempo_prestamo INTEGER
);

CREATE TABLE IF NOT EXISTS mainapp_prestamobienestar (
    id SERIAL PRIMARY KEY,
    id_usuario_fk_id INTEGER REFERENCES mainapp_usuario(id) ON DELETE CASCADE,
    nombre_equipo VARCHAR(100) NOT NULL,
    serial VARCHAR(100),
    fecha_prestamo DATE NOT NULL,
    fecha_devolucion DATE,
    observaciones TEXT
);

CREATE TABLE IF NOT EXISTS mainapp_reporteseguimiento (
    id SERIAL PRIMARY KEY,
    id_usuario_fk_id INTEGER NOT NULL REFERENCES mainapp_usuario(id) ON DELETE CASCADE,
    id_ficha_fk_id VARCHAR(50) NOT NULL REFERENCES mainapp_ficha(num_ficha) ON DELETE CASCADE,
    paz_y_salvo BOOLEAN NOT NULL DEFAULT FALSE,
    observaciones TEXT
);

CREATE TABLE IF NOT EXISTS mainapp_seguimiento (
    id SERIAL PRIMARY KEY,
    id_aprendiz_id INTEGER REFERENCES mainapp_usuario(id) ON DELETE SET NULL,
    id_instructor_id INTEGER REFERENCES mainapp_usuario(id) ON DELETE SET NULL,
    pruebas_tyt BOOLEAN,
    juicios_evaluativos BOOLEAN,
    formato_etapaproductiva BOOLEAN,
    bitacora_etapaproductiva BOOLEAN,
    actividades_bienestar BOOLEAN,
    pazysalvo_biblioteca BOOLEAN,
    observaciones VARCHAR(250),
    fecha_seguimiento DATE
);

CREATE TABLE IF NOT EXISTS mainapp_instructorxaprendiz (
    id SERIAL PRIMARY KEY,
    id_instructor_fk_id INTEGER REFERENCES mainapp_usuario(id) ON DELETE SET NULL,
    id_aprendiz_fk_id INTEGER REFERENCES mainapp_usuario(id) ON DELETE SET NULL,
    bitacoras_completas BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS mainapp_agempleo (
    id SERIAL PRIMARY KEY,
    id_aprendiz_fk_id INTEGER REFERENCES mainapp_usuario(id) ON DELETE CASCADE,
    fecha_nacimiento DATE,
    telefono VARCHAR(20),
    telefono_2 VARCHAR(20),
    correo VARCHAR(254),
    nombre_empresa VARCHAR(200),
    fecha_inicio_empresa DATE,
    fecha_fin_empresa DATE
);
