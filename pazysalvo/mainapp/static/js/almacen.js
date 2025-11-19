 // 🔹 Filtro por estado
  function filtrar(estado) {
    const filas = document.querySelectorAll("#tabla-reportes tbody tr");
    const botones = document.querySelectorAll(".filter-btn");
    botones.forEach(btn => btn.classList.remove("active"));
    document.querySelector(`.filter-btn[onclick="filtrar('${estado}')"]`).classList.add("active");

    filas.forEach(fila => {
      // Ignorar la fila del mensaje vacío
      if (fila.id === "mensaje-vacio") return;

      if (estado === "Todos" || fila.dataset.estado === estado) {
        fila.style.display = "";
      } else {
        fila.style.display = "none";
      }
    });

    verificarResultados();
  }

  // 🔹 Búsqueda en tiempo real
  function buscarReporte() {
    const texto = normalizar(document.getElementById("search").value);
    const filas = document.querySelectorAll("#tabla-reportes tbody tr");

    filas.forEach(fila => {
      if (fila.id === "mensaje-vacio") return; // ignorar mensaje vacío
      const contenido = normalizar(fila.textContent);
      fila.style.display = contenido.includes(texto) ? "" : "none";
    });

    verificarResultados();
  }

  // 🔹 Elimina acentos y convierte a minúsculas
  function normalizar(texto) {
    return texto
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim();
  }

  // 🔹 Verifica si hay resultados visibles
  function verificarResultados() {
    const filas = document.querySelectorAll("#tabla-reportes tbody tr");
    const visibles = Array.from(filas).filter(
      fila => fila.style.display !== "none" && fila.id !== "mensaje-vacio"
    );

    let mensaje = document.querySelector("#mensaje-vacio");
    const tabla = document.querySelector("#tabla-reportes tbody");

    if (visibles.length === 0) {
      if (!mensaje) {
        mensaje = document.createElement("tr");
        mensaje.id = "mensaje-vacio";
        mensaje.innerHTML = `
          <td colspan="7" style="text-align:center; color:#777; font-style:italic;">
            No se encontraron resultados
          </td>`;
        tabla.appendChild(mensaje);
      }
    } else {
      if (mensaje) mensaje.remove();
    }
  }