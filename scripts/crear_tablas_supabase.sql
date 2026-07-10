-- =========================================================
-- CREAR TABLAS DE PAZ Y SALVO EN SUPABASE (PostgreSQL)
-- Los nombres con mayúsculas van ENTRE COMILLAS para que
-- PostgreSQL no los lowercase automáticamente.
-- Luego de ejecutar esto, corre:
--   python manage.py migrate mainapp --fake
--   python manage.py migrate contenttypes auth admin sessions messages
-- =========================================================

CREATE TABLE IF NOT EXISTS mainapp_centro (
    id BIGSERIAL PRIMARY KEY,
    "nombre_centro" VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS mainapp_roles (
    id BIGSERIAL PRIMARY KEY,
    "nombre_rol" VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS mainapp_tipodoc (
    id BIGSERIAL PRIMARY KEY,
    "nombre_tipo" VARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS mainapp_programa (
    "id_programa" SERIAL PRIMARY KEY,
    "nombre_programa" VARCHAR(150) NOT NULL,
    "tipo_programa" VARCHAR(10) NOT NULL DEFAULT 'tecnico',
    "id_centro_FK_id" INTEGER REFERENCES mainapp_centro(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mainapp_ficha (
    "num_ficha" VARCHAR(50) PRIMARY KEY,
    "fecha_inicio" DATE,
    "fecha_fin" DATE,
    "programa_FK_id" INTEGER REFERENCES mainapp_programa("id_programa") ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS mainapp_usuario (
    id BIGSERIAL PRIMARY KEY,
    "nombre" VARCHAR(200),
    "apellidos" VARCHAR(100),
    "num_doc" INTEGER NOT NULL UNIQUE,
    "datos_actualizados" BOOLEAN NOT NULL DEFAULT FALSE,
    "resultados" BOOLEAN NOT NULL DEFAULT FALSE,
    "tyt" BOOLEAN NOT NULL DEFAULT FALSE,
    "id_tipodoc_FK_id" INTEGER REFERENCES mainapp_tipodoc(id) ON DELETE SET NULL,
    "id_rol_FK_id" INTEGER REFERENCES mainapp_roles(id) ON DELETE SET NULL,
    "id_ficha_FK_id" VARCHAR(50) REFERENCES mainapp_ficha("num_ficha") ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS mainapp_login (
    id BIGSERIAL PRIMARY KEY,
    "password" VARCHAR(100),
    "id_usuario_FK_id" INTEGER NOT NULL UNIQUE REFERENCES mainapp_usuario(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mainapp_pazysalvo (
    id BIGSERIAL PRIMARY KEY,
    "lugar_diligen" VARCHAR(200) NOT NULL,
    "fecha_diligen" DATE NOT NULL,
    "regional" VARCHAR(100),
    "tramite" VARCHAR(200),
    "firma_responsable" VARCHAR(200),
    "observaciones" VARCHAR(200),
    "firma_certificacion" VARCHAR(200),
    "id_centro_FK_id" INTEGER REFERENCES mainapp_centro(id) ON DELETE CASCADE,
    "id_usuario_FK_id" INTEGER REFERENCES mainapp_usuario(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mainapp_controlpazysalvo (
    "id_control" SERIAL PRIMARY KEY,
    "id_usuario_FK_id" INTEGER REFERENCES mainapp_usuario(id) ON DELETE CASCADE,
    "id_ficha_FK_id" VARCHAR(50) REFERENCES mainapp_ficha("num_ficha") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mainapp_reportecoordinacion (
    id BIGSERIAL PRIMARY KEY,
    "paz_y_salvo" BOOLEAN NOT NULL DEFAULT FALSE,
    "observaciones" TEXT,
    "id_usuario_FK_id" INTEGER NOT NULL REFERENCES mainapp_usuario(id) ON DELETE CASCADE,
    "id_ficha_FK_id" VARCHAR(50) NOT NULL REFERENCES mainapp_ficha("num_ficha") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mainapp_prestarequipos (
    id BIGSERIAL PRIMARY KEY,
    "nombre_equipo" VARCHAR(100) NOT NULL,
    "fecha_prestamo" DATE NOT NULL,
    "fecha_devolucion" DATE,
    "observaciones" TEXT,
    "estado" VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
    "id_usuario_FK_id" INTEGER REFERENCES mainapp_usuario(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mainapp_registrohoras (
    id BIGSERIAL PRIMARY KEY,
    "cantidad_horas" INTEGER NOT NULL,
    "fecha_registro" DATE NOT NULL DEFAULT CURRENT_DATE,
    "id_usuario_FK_id" INTEGER REFERENCES mainapp_usuario(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mainapp_prestamolibro (
    id BIGSERIAL PRIMARY KEY,
    "titulo_libro" VARCHAR(200) NOT NULL,
    "fecha_prestamo" DATE NOT NULL,
    "centro_formacion" VARCHAR(200),
    "tipo_material" VARCHAR(100),
    "tiempo_prestamo" INTEGER,
    "id_usuario_FK_id" INTEGER REFERENCES mainapp_usuario(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mainapp_prestamobienestar (
    id BIGSERIAL PRIMARY KEY,
    "nombre_equipo" VARCHAR(100) NOT NULL,
    "serial" VARCHAR(100),
    "fecha_prestamo" DATE NOT NULL,
    "fecha_devolucion" DATE,
    "observaciones" TEXT,
    "id_usuario_FK_id" INTEGER REFERENCES mainapp_usuario(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mainapp_reporteseguimiento (
    id BIGSERIAL PRIMARY KEY,
    "paz_y_salvo" BOOLEAN NOT NULL DEFAULT FALSE,
    "observaciones" TEXT,
    "id_usuario_FK_id" INTEGER NOT NULL REFERENCES mainapp_usuario(id) ON DELETE CASCADE,
    "id_ficha_FK_id" VARCHAR(50) NOT NULL REFERENCES mainapp_ficha("num_ficha") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mainapp_seguimiento (
    id BIGSERIAL PRIMARY KEY,
    "pruebas_tyt" BOOLEAN,
    "juicios_evaluativos" BOOLEAN,
    "formato_etapaproductiva" BOOLEAN,
    "bitacora_etapaproductiva" BOOLEAN,
    "actividades_bienestar" BOOLEAN,
    "pazysalvo_biblioteca" BOOLEAN,
    "observaciones" VARCHAR(250),
    "fecha_seguimiento" DATE,
    "id_aprendiz_id" INTEGER REFERENCES mainapp_usuario(id) ON DELETE SET NULL,
    "id_instructor_id" INTEGER REFERENCES mainapp_usuario(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS mainapp_instructorxaprendiz (
    id BIGSERIAL PRIMARY KEY,
    "bitacoras_completas" BOOLEAN NOT NULL DEFAULT FALSE,
    "id_instructor_FK_id" INTEGER REFERENCES mainapp_usuario(id) ON DELETE SET NULL,
    "id_aprendiz_FK_id" INTEGER REFERENCES mainapp_usuario(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS mainapp_agempleo (
    id BIGSERIAL PRIMARY KEY,
    "fecha_nacimiento" DATE,
    "telefono" VARCHAR(20),
    "telefono_2" VARCHAR(20),
    "correo" VARCHAR(254),
    "nombre_empresa" VARCHAR(200),
    "fecha_inicio_empresa" DATE,
    "fecha_fin_empresa" DATE,
    "id_aprendiz_FK_id" INTEGER REFERENCES mainapp_usuario(id) ON DELETE CASCADE
);
