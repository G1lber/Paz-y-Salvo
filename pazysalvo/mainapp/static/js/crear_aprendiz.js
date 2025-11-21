document.addEventListener("DOMContentLoaded", function() {
  const btnAbrir = document.getElementById("btn-abrir-modal");
  const modal = document.getElementById("modal-crear");
  const btnCancelar = document.getElementById("btn-cancelar");

  // ✅ Función para mostrar/ocultar instructor en modal crear
  function toggleInstructorCrear() {
    const checkPatro = document.querySelector('#modal-crear input[name="es_patrocinado"]');
    const checkResultados = document.querySelector('#modal-crear input[name="resultados"]');
    const instructorRow = document.getElementById('instructor-row');
    
    if (instructorRow) {
      if (checkPatro.checked || checkResultados.checked) {
        instructorRow.style.display = 'block';
      } else {
        instructorRow.style.display = 'none';
      }
    }
  }

  // Abrir modal
  if (btnAbrir) {
    btnAbrir.addEventListener("click", () => {
      modal.style.display = "flex";
    });
  }

  // ✅ Event listeners para los checkboxes
  const checkPatro = document.querySelector('#modal-crear input[name="es_patrocinado"]');
  const checkResultados = document.querySelector('#modal-crear input[name="resultados"]');
  
  if (checkPatro) {
    checkPatro.addEventListener('change', toggleInstructorCrear);
  }
  
  if (checkResultados) {
    checkResultados.addEventListener('change', toggleInstructorCrear);
  }

  // Cerrar modal
  if (btnCancelar) {
    btnCancelar.addEventListener("click", () => {
      modal.style.display = "none";
    });
  }
});
