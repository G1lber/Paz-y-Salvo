# Paz-y-Salvo

Sistema de certificación "Paz y Salvo" para aprendices del SENA. Gestión de roles, préstamos, horas de bienestar y seguimiento académico.

## Roles del sistema

| Rol | Descripción |
|---|---|
| **Admin** | Acceso total a todas las funcionalidades del sistema |
| **Coordinador Académico** | Gestiona aprendices y fichas (grupos de formación) |
| **Biblioteca** | Administra préstamos de libros y reportes |
| **Responsable Bienestar** | Registra horas lúdicas y préstamo de equipos de bienestar |
| **Responsable Almacén** | Gestiona préstamo de equipos de almacén |
| **Instructor Seguimiento** | Realiza seguimiento de bitácoras de aprendices asignados |
| **Coordinador Empleo** | Administra la agencia de empleo y datos laborales |
| **Aprendiz** | Solicita y descarga el certificado Paz y Salvo |

## Funcionalidades por área

### Admin
- CRUD completo de todos los usuarios del sistema
- Acceso a todos los módulos: aprendices, fichas, biblioteca, bienestar, almacén, empleo e instructores

### Coordinador Académico
- Gestión de aprendices (crear, editar, eliminar)
- Gestión de fichas y programas de formación
- Marca requisitos académicos del aprendiz (resultados y prueba T y T)

### Biblioteca
- Registro de préstamos de libros a aprendices
- Visualización de aprendices con préstamos pendientes

### Responsable Bienestar
- Registro de horas lúdicas/recreativas para aprendices
- Préstamo de equipos de bienestar
- Consulta de horas faltantes por aprendiz

### Responsable Almacén
- Préstamo de equipos tecnológicos
- Reporte de equipos pendientes por devolver o vencidos

### Instructor Seguimiento
- Visualización de aprendices asignados
- Marca bitácoras completas para cada aprendiz a cargo

### Coordinador Empleo
- Gestión de datos laborales de aprendices
- Registro de información de empresas y fechas de vinculación

### Aprendiz
- Consulta de estado del certificado Paz y Salvo
- Actualización de datos personales y de empleo
- Descarga del certificado solo si cumple todos los requisitos

## Requisitos para obtener el Paz y Salvo

El aprendiz debe cumplir simultáneamente las siguientes condiciones:

1. **Requisitos académicos** — Haber presentado la prueba T y T y tener resultados académicos completos (marcado por Coordinador Académico)
2. **Bitácoras completas** — El instructor de seguimiento debe haber marcado las bitácoras como completas
3. **Horas de bienestar** — Acumular la cantidad requerida según el programa (30 para técnico, 60 para tecnólogo), registradas por Responsable Bienestar
4. **Sin deudas en biblioteca** — No tener libros pendientes por devolver
5. **Sin deudas en almacén** — No tener equipos pendientes por devolver
6. **Datos de empleo actualizados** — Haber diligenciado la información laboral

