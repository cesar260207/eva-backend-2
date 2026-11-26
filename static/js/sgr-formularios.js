/* SGR · Evaluación 3: búsqueda dinámica del Tubo, autocompletado de vecinos y subtipos de atención.
   Todo es mejora progresiva: sin JavaScript los formularios funcionan igual con «Buscar / filtrar» y «Guardar». */
(function () {
    'use strict';

    function esperar(funcion, ms) {
        var temporizador = null;
        return function () {
            var args = arguments;
            window.clearTimeout(temporizador);
            temporizador = window.setTimeout(function () { funcion.apply(null, args); }, ms);
        };
    }

    function aplicarVistaGuardada() {
        var tablero = document.querySelector('[data-tablero]');
        if (!tablero) { return; }
        var vista = null;
        try { vista = window.localStorage.getItem('sgr-vista-tubo'); } catch (error) { vista = null; }
        tablero.classList.toggle('es-lista', vista === 'lista');
    }

    /* Búsqueda dinámica: al escribir (o cambiar un filtro) se pide solo el bloque de resultados y se reemplaza. */
    function iniciarBusquedaDinamica() {
        document.querySelectorAll('form[data-busqueda-dinamica]').forEach(function (formulario) {
            var destino = document.querySelector(formulario.getAttribute('data-busqueda-dinamica'));
            if (!destino || !window.fetch || !window.URLSearchParams) { return; }
            var ultima = 0;

            function buscar() {
                var parametros = new URLSearchParams(new FormData(formulario));
                var visible = parametros.toString();
                parametros.set('parcial', '1');
                var numero = ++ultima;
                destino.setAttribute('aria-busy', 'true');
                var base = formulario.getAttribute('action') || window.location.pathname;
                window.fetch(base + '?' + parametros.toString(), {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }, credentials: 'same-origin'
                }).then(function (respuesta) {
                    if (!respuesta.ok) { throw new Error('HTTP ' + respuesta.status); }
                    return respuesta.text();
                }).then(function (html) {
                    if (numero !== ultima) { return; } /* llegó tarde: ya hay una búsqueda más nueva */
                    destino.innerHTML = html;
                    aplicarVistaGuardada();
                    try { window.history.replaceState(null, '', window.location.pathname + '?' + visible); } catch (error) { /* sin historial */ }
                }).catch(function () {
                    formulario.submit(); /* si falla la carga parcial, se usa la búsqueda normal */
                }).then(function () {
                    destino.setAttribute('aria-busy', 'false');
                });
            }

            var buscarAlEscribir = esperar(buscar, 300);
            formulario.querySelectorAll('[data-busqueda-texto]').forEach(function (campo) {
                campo.addEventListener('input', buscarAlEscribir);
            });
            formulario.querySelectorAll('select, input[type="date"]').forEach(function (campo) {
                campo.addEventListener('change', buscar);
            });
            formulario.addEventListener('submit', function (evento) {
                evento.preventDefault();
                buscar();
            });
        });
    }

    /* Autocompletado: un RUT o un vecino registrado completa nombre y teléfono del solicitante. */
    function iniciarAutocompletado() {
        document.querySelectorAll('form[data-url-vecino]').forEach(function (formulario) {
            var url = formulario.getAttribute('data-url-vecino');
            var campoRut = formulario.querySelector('[data-autocompletar-rut]');
            var campoVecino = formulario.querySelector('[data-autocompletar-vecino]');
            if (!campoRut && !campoVecino) { return; }
            var destinos = {
                nombre: formulario.querySelector('[name="solicitante"], [name="nombre_usuario"], [name="contacto_nombre"]'),
                telefono: formulario.querySelector('[name="solicitante_telefono"], [name="telefono_usuario"], [name="contacto_telefono"]'),
                rut: campoRut,
                territorio: formulario.querySelector('[name="territorio"]')
            };
            var aviso = document.createElement('div');
            aviso.className = 'form-text';
            aviso.setAttribute('role', 'status');
            (campoRut || campoVecino).insertAdjacentElement('afterend', aviso);

            function completar(datos) {
                if (!datos.encontrado) {
                    aviso.textContent = datos.rut_valido === false ? 'RUT incompleto o no válido.' : 'RUT válido, sin vecino registrado: completa los datos a mano.';
                    return;
                }
                ['nombre', 'telefono', 'rut'].forEach(function (clave) {
                    var campo = destinos[clave];
                    if (campo && datos[clave] && !campo.value) { campo.value = datos[clave]; }
                });
                if (destinos.territorio && !destinos.territorio.value && datos.territorio) { destinos.territorio.value = datos.territorio; }
                if (campoVecino && datos.id && !campoVecino.value) { campoVecino.value = String(datos.id); }
                aviso.textContent = 'Datos completados desde el registro de vecinos: ' + datos.nombre + ' (' + datos.delegacion + ').';
            }

            function consultar(parametro, valor) {
                if (!valor) { aviso.textContent = ''; return; }
                window.fetch(url + '?' + parametro + '=' + encodeURIComponent(valor), { credentials: 'same-origin' })
                    .then(function (respuesta) { return respuesta.ok ? respuesta.json() : { encontrado: false }; })
                    .then(completar)
                    .catch(function () { aviso.textContent = ''; });
            }

            if (campoRut) {
                campoRut.addEventListener('input', esperar(function () { consultar('rut', campoRut.value.trim()); }, 400));
            }
            if (campoVecino) {
                campoVecino.addEventListener('change', function () { consultar('id', campoVecino.value); });
            }
        });
    }

    /* Subtipos de atención: solo se ofrecen los del tipo de atención elegido. */
    function iniciarSubtipos() {
        document.querySelectorAll('select[data-filtra-por]').forEach(function (subtipos) {
            var tipo = subtipos.form && subtipos.form.querySelector('[name="' + subtipos.getAttribute('data-filtra-por') + '"]');
            if (!tipo) { return; }
            var opciones = Array.prototype.slice.call(subtipos.options);
            function filtrar() {
                opciones.forEach(function (opcion) {
                    var visible = !opcion.value || !tipo.value || opcion.getAttribute('data-tipo') === tipo.value;
                    opcion.hidden = !visible;
                    opcion.disabled = !visible;
                    if (!visible && opcion.selected) { subtipos.value = ''; }
                });
            }
            tipo.addEventListener('change', filtrar);
            filtrar();
        });
    }

    function iniciar() {
        iniciarBusquedaDinamica();
        iniciarAutocompletado();
        iniciarSubtipos();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', iniciar);
    } else {
        iniciar();
    }
}());
