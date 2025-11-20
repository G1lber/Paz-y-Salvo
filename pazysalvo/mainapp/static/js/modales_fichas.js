$(document).ready(function() {
    // Modal Crear Ficha
    $('#btn-abrir-modal-crear').click(function() {
        $('#modal-crear-ficha').show();
    });

    // Modal Editar Ficha
    $('.btn-editar').click(function() {
        const fichaId = $(this).data('ficha-id');
        const programaId = $(this).data('programa');
        const fechaInicio = $(this).data('fecha-inicio');
        const fechaFin = $(this).data('fecha-fin');

        $('#ficha-id-original').val(fichaId);
        $('#num-ficha-editar').val(fichaId);
        $('#programa-editar').val(programaId);
        $('#fecha-inicio-editar').val(fechaInicio);
        $('#fecha-fin-editar').val(fechaFin);

        $('#modal-editar-ficha').show();
    });

    // Modal Eliminar Ficha
    $('.btn-eliminar').click(function() {
        const fichaId = $(this).data('ficha-id');
        $('#ficha-id-eliminar').val(fichaId);
        $('#ficha-numero-eliminar').text(fichaId);
        $('#modal-eliminar-ficha').show();
    });

    // Cerrar modales
    $('.btn-cancelar').click(function() {
        $(this).closest('.modal').hide();
    });

    // Cerrar modal al hacer click fuera del contenido
    $(window).click(function(event) {
        if ($(event.target).hasClass('modal')) {
            $('.modal').hide();
        }
    });
});

// Abrir modal Crear Programa
$("#btn-abrir-modal-crear-programa").on("click", function () {
    $("#modal-crear-programa").fadeIn();
});

// Cerrar modal Crear Programa
$("#modal-crear-programa .btn-cancelar").on("click", function () {
    $("#modal-crear-programa").fadeOut();
});
