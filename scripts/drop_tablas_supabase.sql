-- =========================================================
-- DROP ALL TABLES (para recrear con python manage.py migrate)
-- Ejecutar en SQL Editor de Supabase ANTES de redeploy
-- =========================================================

DROP TABLE IF EXISTS mainapp_agempleo CASCADE;
DROP TABLE IF EXISTS mainapp_instructorxaprendiz CASCADE;
DROP TABLE IF EXISTS mainapp_seguimiento CASCADE;
DROP TABLE IF EXISTS mainapp_reporteseguimiento CASCADE;
DROP TABLE IF EXISTS mainapp_prestamobienestar CASCADE;
DROP TABLE IF EXISTS mainapp_prestamolibro CASCADE;
DROP TABLE IF EXISTS mainapp_registrohoras CASCADE;
DROP TABLE IF EXISTS mainapp_prestarequipos CASCADE;
DROP TABLE IF EXISTS mainapp_reportecoordinacion CASCADE;
DROP TABLE IF EXISTS mainapp_controlpazysalvo CASCADE;
DROP TABLE IF EXISTS mainapp_pazysalvo CASCADE;
DROP TABLE IF EXISTS mainapp_login CASCADE;
DROP TABLE IF EXISTS mainapp_usuario CASCADE;
DROP TABLE IF EXISTS mainapp_ficha CASCADE;
DROP TABLE IF EXISTS mainapp_programa CASCADE;
DROP TABLE IF EXISTS mainapp_tipodoc CASCADE;
DROP TABLE IF EXISTS mainapp_roles CASCADE;
DROP TABLE IF EXISTS mainapp_centro CASCADE;

-- También dropear tablas de Django por si acaso
DROP TABLE IF EXISTS django_migrations CASCADE;
DROP TABLE IF EXISTS django_session CASCADE;
DROP TABLE IF EXISTS django_admin_log CASCADE;
DROP TABLE IF EXISTS django_content_type CASCADE;
DROP TABLE IF EXISTS auth_permission CASCADE;
DROP TABLE IF EXISTS auth_group_permissions CASCADE;
DROP TABLE IF EXISTS auth_user_groups CASCADE;
DROP TABLE IF EXISTS auth_user_user_permissions CASCADE;
DROP TABLE IF EXISTS auth_group CASCADE;
DROP TABLE IF EXISTS auth_user CASCADE;
