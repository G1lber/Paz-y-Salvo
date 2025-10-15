
// Función para cargar datos en el modal de edición
function cargarDatosEdicion(id, nombre, apellidos, num_doc, id_tipodoc_FK, id_ficha_FK, es_patrocinado, instSeguimiento) {
    document.getElementById('usuario_id').value = id;
    document.querySelector('#editarModal input[name="nombre"]').value = nombre;
    document.querySelector('#editarModal input[name="apellidos"]').value = apellidos;
    document.querySelector('#editarModal input[name="num_doc"]').value = num_doc;
    document.querySelector('#editarModal select[name="id_tipodoc_FK"]').value = id_tipodoc_FK;
    document.querySelector('#editarModal select[name="id_ficha_FK"]').value = id_ficha_FK;
    document.querySelector('#editarModal input[name="es_patrocinado"]').checked = es_patrocinado === 'True' || es_patrocinado === true;

    if (instSeguimiento) {
        document.querySelector('#editarModal select[name="id_instructor"]').value = instSeguimiento;
    }
    const selector = document.querySelector('#editarModal select[name="id_instructor_FK"]');
    selector.value = "";

    // Si hay instructor en el seguimiento, asignarlo
    if (instSeguimiento && instSeguimiento !== "None") {
        selector.value = instSeguimiento;
    }
}


  const inputBusqueda = document.getElementById('busqueda');
  const filas = document.querySelectorAll('#tabla-aprendices tbody tr');

  inputBusqueda.addEventListener('keyup', () => {
    const valor = inputBusqueda.value.toLowerCase();
    filas.forEach(fila => {
      const texto = fila.innerText.toLowerCase();
      fila.style.display = texto.includes(valor) ? '' : 'none';
    });
  });

  const modal = document.getElementById('modal-crear');
  const btnAbrir = document.getElementById('btn-abrir-modal');
  const btnCancelar = document.getElementById('btn-cancelar');

  btnAbrir.addEventListener('click', () => {
    modal.style.display = 'flex';
  });

  btnCancelar.addEventListener('click', () => {
    modal.style.display = 'none';
  });



const botonesEditar = document.querySelectorAll('.btn-abrir-editar');
const modalEditar = document.getElementById('editarModal');
const btnCancelarEditar = document.getElementById('btn-cancelar-editar');

botonesEditar.forEach(btn => {
  btn.addEventListener('click', () => {
    modalEditar.style.display = 'flex';
  });
});

btnCancelarEditar.addEventListener('click', () => {
  modalEditar.style.display = 'none';
});


