// Función para cargar datos en el modal de edición
function cargarDatosEdicion(id, nombre, apellidos, num_doc, id_tipodoc_FK, id_ficha_FK, es_patrocinado, resultados, tyt, instSeguimiento) {

    document.getElementById('usuario_id').value = id;
    document.querySelector('#editarModal input[name="nombre"]').value = nombre;
    document.querySelector('#editarModal input[name="apellidos"]').value = apellidos;
    document.querySelector('#editarModal input[name="num_doc"]').value = num_doc;

    document.querySelector('#editarModal select[name="id_tipodoc_FK"]').value = id_tipodoc_FK;
    document.querySelector('#editarModal select[name="id_ficha_FK"]').value = id_ficha_FK;

    document.querySelector('#editarModal input[name="es_patrocinado"]').checked =
        es_patrocinado === 'True' || es_patrocinado === true;

    document.querySelector('#editarModal input[name="resultados"]').checked =
        resultados === 'True' || resultados === true;

    document.querySelector('#editarModal input[name="tyt"]').checked =
        tyt === 'True' || tyt === true;

    // Instructor
    const selectInst = document.querySelector('#editarModal select[name="id_instructor"]');

    if (instSeguimiento && instSeguimiento !== "None") {
        selectInst.value = instSeguimiento;
    } else {
        selectInst.value = "";
    }

    actualizarInstructorEditar(); // Forzar actualización visible/oculto
}


// BÚSQUEDA
const inputBusqueda = document.getElementById('busqueda');
const filas = document.querySelectorAll('#tabla-aprendices tbody tr');

inputBusqueda.addEventListener('keyup', () => {
    const valor = inputBusqueda.value.toLowerCase();
    filas.forEach(fila => {
        const texto = fila.innerText.toLowerCase();
        fila.style.display = texto.includes(valor) ? '' : 'none';
    });
});


// MODAL CREAR
const modalCrear = document.getElementById('modal-crear');
const btnAbrirCrear = document.getElementById('btn-abrir-modal');
const btnCancelarCrear = document.getElementById('btn-cancelar');

btnAbrirCrear.addEventListener('click', () => modalCrear.style.display = 'flex');
btnCancelarCrear.addEventListener('click', () => modalCrear.style.display = 'none');


// MODAL EDITAR
const modalEditar = document.getElementById('editarModal');
const botonesEditar = document.querySelectorAll('.btn-abrir-editar');
const btnCancelarEditar = document.getElementById('btn-cancelar-editar');

botonesEditar.forEach(btn => {
    btn.addEventListener('click', () => {
        modalEditar.style.display = 'flex';
    });
});

btnCancelarEditar.addEventListener('click', () => {
    modalEditar.style.display = 'none';
});


// MOSTRAR / OCULTAR INSTRUCTOR (CREAR Y EDITAR)
document.addEventListener("DOMContentLoaded", function () {

    function actualizarInstructorCrear() {
        const resultados = document.getElementById("id_resultados");

        const row = document.getElementById("instructor-row");

        if (patrocinado && resultados) {
            row.style.display = (patrocinado.checked || resultados.checked) ? "block" : "none";
        }
    }

    function actualizarInstructorEditar() {
        const resultados = document.querySelector('#editarModal input[name="resultados"]');

        const row = document.getElementById("editar-instructor-row");

        if (patrocinado && resultados) {
            row.style.display = (patrocinado.checked || resultados.checked) ? "block" : "none";
        }
    }

    // Eventos del modal crear
    const resultadosCrear = document.getElementById("id_resultados");

    if (resultadosCrear) resultadosCrear.addEventListener("change", actualizarInstructorCrear);

    // Eventos del modal editar

    const resultadosEditar = document.querySelector('#editarModal input[name="resultados"]');

    if (resultadosEditar) resultadosEditar.addEventListener("change", actualizarInstructorEditar);

});
