/*
 * SGR · tema claro u oscuro. Se carga en el <head>, sin defer y antes del CSS, para poner
 * data-bs-theme en <html> antes de que se dibuje la página (así no parpadea en blanco).
 * También aplica las preferencias de accesibilidad guardadas, por la misma razón.
 * Opciones del tema: «claro», «oscuro» o «auto» (sigue al sistema). El alto contraste manda sobre el tema.
 * El resto del comportamiento (botones, cambios del sistema) está en sgr.js.
 */
(function () {
    'use strict';

    var raiz = document.documentElement;
    var CLAVE = 'sgr-tema';
    var OPCIONES = ['claro', 'oscuro', 'auto'];
    var sistema = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

    function leer() {
        var guardado = null;
        try { guardado = window.localStorage.getItem(CLAVE); } catch (error) { guardado = null; }
        return OPCIONES.indexOf(guardado) === -1 ? 'auto' : guardado;
    }

    function guardar(tema) {
        try { window.localStorage.setItem(CLAVE, tema); } catch (error) { /* sin almacenamiento: dura mientras la página siga abierta */ }
    }

    function aplicar(tema) {
        var oscuro = !raiz.classList.contains('a11y-contrast') &&
            (tema === 'oscuro' || (tema === 'auto' && !!sistema && sistema.matches));
        raiz.setAttribute('data-bs-theme', oscuro ? 'dark' : 'light');
        return oscuro;
    }

    /* Preferencias de accesibilidad guardadas por sgr.js (misma clave y formato). */
    try {
        var a11y = JSON.parse(window.localStorage.getItem('sgr-accesibilidad') || '{}') || {};
        var fuente = Math.min(2, Math.max(0, parseInt(a11y.fuente, 10) || 0));
        if (fuente) {
            raiz.classList.remove('a11y-font-0');
            raiz.classList.add('a11y-font-' + fuente);
        }
        if (a11y.contraste === true) { raiz.classList.add('a11y-contrast'); }
        if (a11y.subrayar === true) { raiz.classList.add('a11y-subrayar'); }
    } catch (error) { /* sin preferencias guardadas */ }

    aplicar(leer());

    window.sgrTema = { leer: leer, guardar: guardar, aplicar: aplicar, sistema: sistema };
}());
