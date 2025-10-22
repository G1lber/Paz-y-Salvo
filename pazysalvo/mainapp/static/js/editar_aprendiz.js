
document.addEventListener("DOMContentLoaded", function() {
  const botonesEditar = document.querySelectorAll(".btn-editar");
  const modal = document.getElementById("editarModal");
  const btnCancelarEditar = document.getElementById("btn-cancelar-editar");

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
      const instructor = this.dataset.instructor;

    //   console.log("🟢 Datos recibidos:", { id, nombre, apellidos, num_doc, tipo_doc, ficha, patrocinado, instructor });

      // 🧠 Asignar los valores al formulario del modal
      document.querySelector('#editarModal input[name="usuario_id"]').value = id;
      document.querySelector('#editarModal input[name="nombre"]').value = nombre;
      document.querySelector('#editarModal input[name="apellidos"]').value = apellidos;
      document.querySelector('#editarModal input[name="num_doc"]').value = num_doc;

      // Selects
      document.querySelector('#editarModal select[name="id_tipodoc_FK"]').value = tipo_doc || "";
      document.querySelector('#editarModal select[name="id_ficha_FK"]').value = ficha || "";

      // Checkbox
      const checkPatro = document.querySelector('#editarModal input[name="es_patrocinado"]');
      checkPatro.checked = (patrocinado === "True" || patrocinado === true);

      // Instructor (ajusta aquí si tu name es distinto)
      const selectInstructor = document.querySelector('#editarModal select[name="id_instructor"]') 
                            || document.querySelector('#editarModal select[name="id_instructor_FK"]');
      if (selectInstructor) {
        selectInstructor.value = (instructor && instructor !== "null" && instructor !== "None") ? instructor : "";
      }

      // Mostrar el modal
      modal.style.display = "flex";
    });
  });

  // 🔴 Cerrar modal
  if (btnCancelarEditar) {
    btnCancelarEditar.addEventListener("click", () => {
      modal.style.display = "none";
    });
  }
});