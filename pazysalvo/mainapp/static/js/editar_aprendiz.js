document.addEventListener("DOMContentLoaded", function() {
  const botonesEditar = document.querySelectorAll(".btn-editar");
  const modal = document.getElementById("editarModal");
  const btnCancelarEditar = document.getElementById("btn-cancelar-editar");

  // ✅ Función para mostrar/ocultar instructor en modal editar
  function toggleInstructorEditar() {
    const checkPatro = document.querySelector('#editarModal input[name="es_patrocinado"]');
    const checkResultados = document.querySelector('#editarModal input[name="resultados"]');
    const instructorRow = document.getElementById('editar-instructor-row');
    
    if (instructorRow) {
      if (checkPatro.checked || checkResultados.checked) {
        instructorRow.style.display = 'block';
      } else {
        instructorRow.style.display = 'none';
      }
    }
  }

  botonesEditar.forEach(boton => {
    boton.addEventListener("click", function(event) {
      event.preventDefault();

      // 🟢 Obtener los valores del botón
      const id = this.dataset.id;
      const nombre = this.dataset.nombre;
      const apellidos = this.dataset.apellidos;
      const num_doc = this.dataset.numdoc;
      const tipo_doc = this.dataset.tipodoc;
      const ficha = this.dataset.ficha;
      const patrocinado = this.dataset.patrocinado;
      const resultados = this.dataset.resultados;
      const tyt = this.dataset.tyt;
      const instructor = this.dataset.instructor;

      // 🧠 Asignar los valores al formulario del modal
      document.querySelector('#editarModal input[name="usuario_id"]').value = id;
      document.querySelector('#editarModal input[name="nombre"]').value = nombre;
      document.querySelector('#editarModal input[name="apellidos"]').value = apellidos;
      document.querySelector('#editarModal input[name="num_doc"]').value = num_doc;

      // Selects
      document.querySelector('#editarModal select[name="id_tipodoc_FK"]').value = tipo_doc || "";
      document.querySelector('#editarModal select[name="id_ficha_FK"]').value = ficha || "";

      // Checkboxes ✅
      const checkPatro = document.querySelector('#editarModal input[name="es_patrocinado"]');
      checkPatro.checked = (patrocinado === "True" || patrocinado === true);

      const checkResultados = document.querySelector('#editarModal input[name="resultados"]');
      if (checkResultados) {
        checkResultados.checked = (resultados === "True" || resultados === true);
      }

      const checkTyt = document.querySelector('#editarModal input[name="tyt"]');
      if (checkTyt) {
        checkTyt.checked = (tyt === "True" || tyt === true);
      }

      // Instructor
      const selectInstructor = document.querySelector('#editarModal select[name="id_instructor"]');
      if (selectInstructor) {
        selectInstructor.value = (instructor && instructor !== "null" && instructor !== "None") ? instructor : "";
      }

      // ✅ Verificar y mostrar instructor row si corresponde
      toggleInstructorEditar();

      // Mostrar el modal
      modal.style.display = "flex";
    });
  });

  // ✅ Event listeners para los checkboxes (cuando cambien en el modal)
  const checkPatroEdit = document.querySelector('#editarModal input[name="es_patrocinado"]');
  const checkResultadosEdit = document.querySelector('#editarModal input[name="resultados"]');
  
  if (checkPatroEdit) {
    checkPatroEdit.addEventListener('change', toggleInstructorEditar);
  }
  
  if (checkResultadosEdit) {
    checkResultadosEdit.addEventListener('change', toggleInstructorEditar);
  }

  // 🔴 Cerrar modal
  if (btnCancelarEditar) {
    btnCancelarEditar.addEventListener("click", () => {
      modal.style.display = "none";
    });
  }
});