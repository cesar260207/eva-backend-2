// Verificación en vivo del RUT del menor: al salir del campo (o cambiar de actividad) consulta al servidor si el RUT
// es válido y si ya fue inscrito en la actividad, y muestra «RUT ya ingresado por <unidad>». La validación definitiva
// la hace siempre el servidor al guardar; esto solo avisa antes.
(function () {
    'use strict';
    var form = document.querySelector('form[data-url-verificar-rut]');
    if (!form) { return; }
    var campoRut = form.querySelector('[data-verificar-rut]');
    var campoEvento = form.querySelector('[name="evento"]');
    var aviso = document.getElementById('aviso-rut');
    if (!campoRut || !aviso) { return; }

    function mostrar(texto, clase) {
        aviso.textContent = texto;
        aviso.className = 'alert mt-2 ' + clase;
    }

    function verificar() {
        var rut = campoRut.value.trim();
        if (!rut) { aviso.className = 'alert d-none mt-2'; return; }
        var params = new URLSearchParams({
            rut: rut,
            evento: campoEvento ? campoEvento.value : '',
            excluir: campoRut.getAttribute('data-excluir') || ''
        });
        fetch(form.getAttribute('data-url-verificar-rut') + '?' + params.toString(), {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }, credentials: 'same-origin'
        })
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (datos) {
                if (!datos) { return; }
                if (!datos.valido) { mostrar(datos.mensaje, 'alert-warning'); return; }
                if (datos.duplicado) { mostrar(datos.mensaje, 'alert-danger'); return; }
                campoRut.value = datos.rut;
                mostrar(datos.mensaje, 'alert-success');
            })
            .catch(function () { /* sin conexión: el servidor validará al guardar */ });
    }

    campoRut.addEventListener('change', verificar);
    if (campoEvento) { campoEvento.addEventListener('change', verificar); }
})();
