/*
 * SGR · comportamiento de la interfaz. JavaScript propio, sin librerías (solo usa el collapse de Bootstrap
 * a través de sus atributos data-bs-*). Cada función revisa si su elemento existe y respeta
 * «prefers-reduced-motion». Sin JavaScript la página se ve completa: aquí solo se agrega movimiento y ayudas.
 */
(function () {
    'use strict';

    var raiz = document.documentElement;
    var movimientoReducido = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var hayObservador = 'IntersectionObserver' in window;

    /* Preferencias de accesibilidad (clases del Kit de Gobierno Digital en <html>). */
    var CLAVE_A11Y = 'sgr-accesibilidad';
    var NIVELES = ['a11y-font-0', 'a11y-font-1', 'a11y-font-2'];
    var PORCENTAJES = ['100 %', '125 %', '150 %'];

    function leerPreferencias() {
        try {
            var guardado = JSON.parse(window.localStorage.getItem(CLAVE_A11Y) || '{}');
            return {
                fuente: Math.min(2, Math.max(0, parseInt(guardado.fuente, 10) || 0)),
                contraste: guardado.contraste === true,
                subrayar: guardado.subrayar === true
            };
        } catch (error) {
            return { fuente: 0, contraste: false, subrayar: false };
        }
    }

    function guardarPreferencias(preferencias) {
        try {
            window.localStorage.setItem(CLAVE_A11Y, JSON.stringify(preferencias));
        } catch (error) {
            /* Sin almacenamiento disponible la preferencia dura solo mientras la página siga abierta. */
        }
    }

    function aplicarPreferencias(preferencias) {
        NIVELES.forEach(function (clase) { raiz.classList.remove(clase); });
        raiz.classList.add(NIVELES[preferencias.fuente]);
        raiz.classList.toggle('a11y-contrast', preferencias.contraste);
        raiz.classList.toggle('a11y-subrayar', preferencias.subrayar);
        document.querySelectorAll('[data-a11y="contraste"]').forEach(function (boton) {
            boton.setAttribute('aria-pressed', String(preferencias.contraste));
        });
        document.querySelectorAll('[data-a11y="subrayar"]').forEach(function (boton) {
            boton.setAttribute('aria-pressed', String(preferencias.subrayar));
        });
        document.querySelectorAll('[data-a11y="mas"]').forEach(function (boton) {
            boton.setAttribute('aria-disabled', String(preferencias.fuente === 2));
        });
        document.querySelectorAll('[data-a11y="menos"]').forEach(function (boton) {
            boton.setAttribute('aria-disabled', String(preferencias.fuente === 0));
        });
        document.querySelectorAll('[data-a11y-nivel]').forEach(function (aviso) {
            aviso.textContent = 'Texto al ' + PORCENTAJES[preferencias.fuente];
        });
        refrescarTema();
    }

    /* Tema claro, oscuro o automático. tema.js ya lo aplicó en el <head>; aquí se marcan los botones y
       se vuelve a aplicar cuando cambia la elección, el alto contraste o la configuración del sistema. */
    var NOMBRES_TEMA = { claro: 'claro', oscuro: 'oscuro', auto: 'automático' };

    function refrescarTema() {
        var tema = window.sgrTema;
        if (!tema) { return; }
        var actual = tema.leer();
        var oscuro = tema.aplicar(actual);
        document.querySelectorAll('[data-tema]').forEach(function (boton) {
            boton.setAttribute('aria-pressed', String(boton.getAttribute('data-tema') === actual));
        });
        document.querySelectorAll('[data-tema-boton]').forEach(function (boton) {
            boton.setAttribute('aria-label', 'Tema: ' + NOMBRES_TEMA[actual]);
            var uso = boton.querySelector('use');
            if (uso) {
                var base = uso.getAttribute('href').split('#')[0];
                uso.setAttribute('href', base + (actual === 'auto' ? '#i-tema-auto' : (oscuro ? '#i-luna' : '#i-sol')));
            }
        });
    }

    function iniciarTema() {
        var tema = window.sgrTema;
        if (!tema) { return; }
        document.querySelectorAll('[data-tema]').forEach(function (boton) {
            boton.addEventListener('click', function () {
                tema.guardar(boton.getAttribute('data-tema'));
                refrescarTema();
            });
        });
        if (tema.sistema) {
            if (tema.sistema.addEventListener) {
                tema.sistema.addEventListener('change', refrescarTema);
            } else if (tema.sistema.addListener) {
                tema.sistema.addListener(refrescarTema);
            }
        }
        refrescarTema();
    }

    function iniciarAccesibilidad() {
        var preferencias = leerPreferencias();
        aplicarPreferencias(preferencias);
        document.querySelectorAll('[data-requiere-js]').forEach(function (elemento) {
            elemento.hidden = false;
        });
        document.querySelectorAll('[data-a11y]').forEach(function (boton) {
            boton.addEventListener('click', function () {
                var accion = boton.getAttribute('data-a11y');
                if (accion === 'mas') { preferencias.fuente = Math.min(2, preferencias.fuente + 1); }
                if (accion === 'menos') { preferencias.fuente = Math.max(0, preferencias.fuente - 1); }
                if (accion === 'contraste') { preferencias.contraste = !preferencias.contraste; }
                if (accion === 'subrayar') { preferencias.subrayar = !preferencias.subrayar; }
                if (accion === 'reiniciar') { preferencias = { fuente: 0, contraste: false, subrayar: false }; }
                aplicarPreferencias(preferencias);
                guardarPreferencias(preferencias);
            });
        });
        /* El botón del pie abre la misma barra: al abrirse, lleva la vista y el foco a ella. */
        var panel = document.getElementById('panel-accesibilidad');
        if (panel) {
            panel.addEventListener('shown.bs.collapse', function () {
                if (panel.getAttribute('data-enfocar') === 'si') {
                    panel.removeAttribute('data-enfocar');
                    window.scrollTo({ top: 0, behavior: movimientoReducido ? 'auto' : 'smooth' });
                    var primero = panel.querySelector('button');
                    if (primero) { primero.focus({ preventScroll: true }); }
                }
            });
            document.querySelectorAll('[data-a11y-desde-pie]').forEach(function (boton) {
                boton.addEventListener('click', function () { panel.setAttribute('data-enfocar', 'si'); });
            });
        }
    }

    /* Encabezado fijo que se compacta y gana sombra al bajar más de 8 px. */
    function iniciarEncabezado() {
        var encabezado = document.querySelector('[data-encabezado]');
        if (!encabezado) { return; }
        var pendiente = false;
        function revisar() {
            encabezado.classList.toggle('is-compact', window.scrollY > 8);
            pendiente = false;
        }
        window.addEventListener('scroll', function () {
            if (!pendiente) {
                pendiente = true;
                window.requestAnimationFrame(revisar);
            }
        }, { passive: true });
        revisar();
    }

    function estaALaVista(elemento) {
        var caja = elemento.getBoundingClientRect();
        return caja.top < window.innerHeight * 0.92 && caja.bottom > 0;
    }

    function observar(elementos, alAparecer) {
        var observador = new IntersectionObserver(function (entradas) {
            entradas.forEach(function (entrada) {
                if (entrada.isIntersecting) {
                    alAparecer(entrada.target);
                    observador.unobserve(entrada.target);
                }
            });
        }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
        elementos.forEach(function (elemento) { observador.observe(elemento); });
    }

    /* Aparición al bajar: solo se ocultan los elementos que todavía no están a la vista. */
    function iniciarApariciones() {
        if (movimientoReducido || !hayObservador) { return; }
        /* En las pantallas internas, cada bloque principal también aparece al bajar. */
        document.querySelectorAll('main .panel:not(.reveal), main .cifras-panel:not(.reveal)').forEach(function (elemento) {
            if (!elemento.closest('.reveal, .panel-hero, .panel-aside')) { elemento.classList.add('reveal'); }
        });
        var pendientes = [];
        document.querySelectorAll('.reveal').forEach(function (elemento) {
            if (estaALaVista(elemento)) { return; }
            var hermanos = Array.prototype.filter.call(elemento.parentElement.children, function (hijo) {
                return hijo.classList.contains('reveal');
            });
            var posicion = Math.min(hermanos.indexOf(elemento), 5);
            elemento.style.setProperty('--retraso', (posicion * 70) + 'ms');
            elemento.classList.add('reveal-pendiente');
            pendientes.push(elemento);
        });
        observar(pendientes, function (elemento) { elemento.classList.add('is-visible'); });

        var lineas = document.querySelectorAll('[data-linea-tiempo]');
        lineas.forEach(function (lista) { lista.classList.add('linea-tiempo-pendiente'); });
        observar(Array.prototype.slice.call(lineas), function (lista) { lista.classList.add('is-visible'); });

        var pasos = document.querySelectorAll('[data-linea-pasos]');
        pasos.forEach(function (lista) { lista.classList.add('linea-pendiente'); });
        observar(Array.prototype.slice.call(pasos), function (lista) { lista.classList.add('is-visible'); });
    }

    /* Cifras que cuentan de 0 a su valor. El valor final ya está en el HTML y el lector de pantalla lee ese. */
    function iniciarConteos() {
        var cifras = Array.prototype.slice.call(document.querySelectorAll('[data-contar]'));
        if (!cifras.length || movimientoReducido || !hayObservador || !window.requestAnimationFrame) { return; }
        cifras.forEach(function (cifra) {
            var final = parseFloat(cifra.getAttribute('data-contar'));
            var decimales = parseInt(cifra.getAttribute('data-decimales'), 10) || 0;
            if (isNaN(final)) { return; }
            var formato = { minimumFractionDigits: decimales, maximumFractionDigits: decimales };
            var textoFinal = cifra.textContent;
            function contar() {
                var inicio = null;
                function paso(momento) {
                    if (inicio === null) { inicio = momento; }
                    var avance = Math.min((momento - inicio) / 900, 1);
                    var suavizado = 1 - Math.pow(1 - avance, 3);
                    cifra.textContent = (final * suavizado).toLocaleString('es-CL', formato);
                    if (avance < 1) {
                        window.requestAnimationFrame(paso);
                    } else {
                        cifra.textContent = textoFinal;
                    }
                }
                window.requestAnimationFrame(paso);
                /* Respaldo: si el navegador pausa los cuadros de animación, el valor final igual queda a la vista. */
                window.setTimeout(function () { cifra.textContent = textoFinal; }, 1200);
            }
            observar([cifra], contar);
        });
    }

    /* Barras de avance que se llenan desde 0 en 700 ms al aparecer. */
    function iniciarBarras() {
        if (movimientoReducido || !hayObservador) { return; }
        var barras = Array.prototype.slice.call(document.querySelectorAll('.progress, .barra-avance'));
        barras.forEach(function (barra) { barra.classList.add('barra-pendiente'); });
        observar(barras, function (barra) { barra.classList.add('is-visible'); });
    }

    /* Anillos de cumplimiento de los paneles: se llenan desde 0 al aparecer. Sin JavaScript se ven llenos. */
    function iniciarAnillos() {
        if (movimientoReducido || !hayObservador) { return; }
        var anillos = Array.prototype.slice.call(document.querySelectorAll('.anillo'));
        anillos.forEach(function (anillo) { anillo.classList.add('anillo-pendiente'); });
        observar(anillos, function (anillo) { anillo.classList.add('is-visible'); });
    }

    /* Tubo de trabajo: «Tablero» o «Lista». La elección se recuerda en este navegador. */
    function iniciarVistaTablero() {
        var tablero = document.querySelector('[data-tablero]');
        var botones = document.querySelectorAll('[data-vista]');
        if (!tablero || !botones.length) { return; }
        function aplicar(vista) {
            tablero.classList.toggle('es-lista', vista === 'lista');
            botones.forEach(function (boton) {
                boton.setAttribute('aria-pressed', boton.getAttribute('data-vista') === vista ? 'true' : 'false');
            });
        }
        var guardada = null;
        try { guardada = window.localStorage.getItem('sgr-vista-tubo'); } catch (error) { guardada = null; }
        aplicar(guardada === 'lista' ? 'lista' : 'tablero');
        botones.forEach(function (boton) {
            boton.addEventListener('click', function () {
                var vista = boton.getAttribute('data-vista');
                aplicar(vista);
                try { window.localStorage.setItem('sgr-vista-tubo', vista); } catch (error) { /* sin almacenamiento: solo esta visita */ }
            });
        });
    }

    /* Si el formulario vuelve con errores, el foco va al primer campo con error. */
    function iniciarFocoEnError() {
        var campo = document.querySelector('main .is-invalid, main [aria-invalid="true"]');
        var destino = campo;
        if (campo && !/^(INPUT|SELECT|TEXTAREA)$/.test(campo.tagName)) {
            destino = campo.querySelector('input, select, textarea') || document.querySelector('[data-resumen-errores]');
        }
        if (!destino) { destino = document.querySelector('[data-resumen-errores]'); }
        if (!destino) { return; }
        destino.focus({ preventScroll: true });
        destino.scrollIntoView({ block: 'center', behavior: movimientoReducido ? 'auto' : 'smooth' });
    }

    /* Nombre del archivo elegido en la zona de evidencia. */
    function iniciarArchivos() {
        document.querySelectorAll('input[type="file"][data-nombre-archivo]').forEach(function (entrada) {
            var aviso = document.getElementById(entrada.getAttribute('data-nombre-archivo'));
            var zona = entrada.closest('.zona-archivo');
            entrada.addEventListener('change', function () {
                var nombres = Array.prototype.map.call(entrada.files || [], function (archivo) { return archivo.name; });
                if (aviso) { aviso.textContent = nombres.length ? 'Archivo elegido: ' + nombres.join(', ') : ''; }
                if (zona) { zona.classList.toggle('con-archivo', nombres.length > 0); }
            });
        });
    }

    /* Mostrar u ocultar la contraseña sin cambiar el name ni el id del campo. */
    function iniciarVerClave() {
        document.querySelectorAll('[data-ver-clave]').forEach(function (boton) {
            var campo = document.getElementById(boton.getAttribute('data-ver-clave'));
            if (!campo) { return; }
            var uso = boton.querySelector('use');
            var base = uso ? uso.getAttribute('href').split('#')[0] : '';
            boton.hidden = false;
            boton.addEventListener('click', function () {
                var mostrar = campo.type === 'password';
                campo.type = mostrar ? 'text' : 'password';
                boton.setAttribute('aria-pressed', String(mostrar));
                boton.setAttribute('aria-label', mostrar ? 'Ocultar contraseña' : 'Mostrar contraseña');
                if (uso) { uso.setAttribute('href', base + (mostrar ? '#i-ojo-no' : '#i-ojo')); }
                campo.focus();
            });
        });
    }

    /* Preguntas frecuentes: sin JavaScript las respuestas se ven abiertas; aquí se pliegan y el
       collapse de Bootstrap las abre y cierra con sus atributos data-bs-*. */
    function iniciarPlegables() {
        if (!window.bootstrap || !window.bootstrap.Collapse) { return; }
        document.querySelectorAll('[data-plegable]').forEach(function (respuesta) {
            respuesta.classList.add('collapse');
            document.querySelectorAll('[aria-controls="' + respuesta.id + '"]').forEach(function (boton) {
                boton.setAttribute('aria-expanded', 'false');
                boton.classList.add('collapsed');
            });
        });
    }

    /* Territorio: el esquema, los botones de delegación y las tarjetas comparten «data-delegacion».
       Al pasar el mouse o enfocar uno se resaltan los otros; al hacer clic se baja a la tarjeta y queda
       seleccionada. Sin JavaScript los enlaces llevan igual a cada tarjeta (#delegacion-…). */
    function iniciarTerritorio() {
        var territorio = document.querySelector('[data-territorio]');
        if (!territorio) { return; }
        var enlaces = territorio.querySelectorAll('a[data-delegacion]');
        var tarjetas = territorio.querySelectorAll('article[data-delegacion]');

        function delMismo(slug) {
            return territorio.querySelectorAll('[data-delegacion="' + slug + '"]');
        }
        function resaltar(slug, activo) {
            delMismo(slug).forEach(function (elemento) { elemento.classList.toggle('is-activa', activo); });
        }
        function seleccionar(slug, desplazar) {
            var tarjeta = null;
            tarjetas.forEach(function (actual) {
                var es = actual.getAttribute('data-delegacion') === slug;
                actual.classList.toggle('is-seleccionada', es);
                if (es) { tarjeta = actual; }
            });
            if (!tarjeta) { return; }
            enlaces.forEach(function (enlace) {
                if (enlace.getAttribute('data-delegacion') === slug) {
                    enlace.setAttribute('aria-current', 'true');
                } else {
                    enlace.removeAttribute('aria-current');
                }
            });
            if (desplazar) {
                tarjeta.scrollIntoView({ block: 'center', behavior: movimientoReducido ? 'auto' : 'smooth' });
                tarjeta.focus({ preventScroll: true });
                try { window.history.replaceState(null, '', '#' + tarjeta.id); } catch (error) { /* sin historial: igual queda marcada */ }
            }
        }

        territorio.querySelectorAll('[data-delegacion]').forEach(function (elemento) {
            var slug = elemento.getAttribute('data-delegacion');
            elemento.addEventListener('mouseenter', function () { resaltar(slug, true); });
            elemento.addEventListener('mouseleave', function () { resaltar(slug, false); });
            elemento.addEventListener('focusin', function () { resaltar(slug, true); });
            elemento.addEventListener('focusout', function () { resaltar(slug, false); });
        });
        enlaces.forEach(function (enlace) {
            enlace.addEventListener('click', function (evento) {
                evento.preventDefault();
                seleccionar(enlace.getAttribute('data-delegacion'), true);
            });
        });
        var inicial = window.location.hash.replace('#delegacion-', '');
        if (inicial && inicial !== window.location.hash) { seleccionar(inicial, false); }
    }

    function iniciar() {
        iniciarPlegables();
        iniciarAccesibilidad();
        iniciarTema();
        iniciarEncabezado();
        iniciarApariciones();
        iniciarConteos();
        iniciarBarras();
        iniciarAnillos();
        iniciarVistaTablero();
        iniciarFocoEnError();
        iniciarArchivos();
        iniciarVerClave();
        iniciarTerritorio();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', iniciar);
    } else {
        iniciar();
    }
}());
