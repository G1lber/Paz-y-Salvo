document.addEventListener("DOMContentLoaded", function() {
  // Para el modal de CREAR
  const fichaCrear = document.querySelector('#modal-crear select[name="id_ficha_FK"]');
  const instructorRowCrear = document.getElementById("instructor-row");

  if (fichaCrear && instructorRowCrear) {
    fichaCrear.addEventListener("change", function() {
      if (this.value) {
        instructorRowCrear.style.display = "block";
      } else {
        instructorRowCrear.style.display = "none";
      }
    });
  }

  // Para el modal de EDITAR
  const fichaEditar = document.querySelector('#editarModal select[name="id_ficha_FK"]');
  const instructorRowEditar = document.getElementById("editar-instructor-row");

  if (fichaEditar && instructorRowEditar) {
    fichaEditar.addEventListener("change", function() {
      if (this.value) {
        instructorRowEditar.style.display = "block";
      } else {
        instructorRowEditar.style.display = "none";
      }
    });

    // Mostrar el campo si ya tiene una ficha asignada al abrir el modal
    if (fichaEditar.value) {
      instructorRowEditar.style.display = "block";
    }
  }
});
