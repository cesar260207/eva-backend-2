"""Ejecuta la suite y genera el protocolo de pruebas de la Evaluación 3 con resultados, defectos e indicadores.

Salidas (se regeneran, no se editan a mano):
  docs/PROTOCOLO_PRUEBAS.md          protocolo completo: casos, resultados, defectos, reejecuciones, indicadores
  docs/TRAZABILIDAD.md               matriz requerimiento -> pantalla -> regla de negocio -> casos -> estado
  docs/resultados/protocolo_casos.csv, protocolo_defectos.csv, protocolo_indicadores.csv   (para gráficos del informe)
"""
import csv
import platform
import time
import unittest
from io import StringIO
from pathlib import Path

import django
from django.conf import settings
from django.core.management.base import BaseCommand
from django.test.runner import DiscoverRunner
from django.utils import timezone

from delegaciones_app import protocolo
from delegaciones_app.management.commands.plan_pruebas import ResultadoPorPrueba, _pruebas


def _celda(texto):
    return str(texto).replace('|', '\\|').replace('\n', ' ')


def _estado_de(resultados):
    if not resultados:
        return 'No ejecutado'
    if all(r == 'Aprobado' for r in resultados):
        return 'Aprobado'
    if any(r == 'No ejecutada' for r in resultados):
        return 'Bloqueado'
    return 'Fallido'


class Command(BaseCommand):
    help = 'Ejecuta las pruebas y genera docs/PROTOCOLO_PRUEBAS.md, docs/TRAZABILIDAD.md y los CSV del protocolo.'

    def add_arguments(self, parser):
        parser.add_argument('--salida', default=str(Path(settings.BASE_DIR) / 'docs'), help='Carpeta de salida.')

    def handle(self, *args, **opciones):
        salida = Path(opciones['salida'])
        (salida / 'resultados').mkdir(parents=True, exist_ok=True)
        runner = DiscoverRunner(verbosity=0, interactive=False)
        runner.setup_test_environment()
        suite = runner.build_suite(['delegaciones_app', 'gestion_app'])
        pruebas = list(_pruebas(suite))
        self.stdout.write(f'Ejecutando {len(pruebas)} pruebas...')
        bases = runner.setup_databases()
        inicio = time.monotonic()
        try:
            resultado = unittest.TextTestRunner(stream=StringIO(), resultclass=ResultadoPorPrueba, verbosity=0).run(suite)
        finally:
            runner.teardown_databases(bases)
            runner.teardown_test_environment()
        duracion = time.monotonic() - inicio
        por_prueba = {prueba.id(): resultado.resultados.get(prueba.id(), 'No ejecutada') for prueba in pruebas}
        fecha = f'{timezone.localdate():%d-%m-%Y}'
        fallidas = sum(1 for valor in por_prueba.values() if valor != 'Aprobado')
        ejecuciones = protocolo.EJECUCIONES + [{
            'numero': len(protocolo.EJECUCIONES) + 1, 'fecha': fecha, 'pruebas': len(por_prueba), 'fallidas': fallidas,
            'nota': f'Ejecución que generó este protocolo ({duracion:.0f} s).',
        }]
        casos = self._evaluar_casos(por_prueba, fecha)
        defectos = self._evaluar_defectos(por_prueba)
        indicadores = self._indicadores(casos, defectos)
        entorno = {
            'fecha': fecha, 'python': platform.python_version(), 'django': django.get_version(),
            'motor': settings.DATABASES['default']['ENGINE'].rsplit('.', 1)[-1], 'total': len(por_prueba), 'fallidas': fallidas,
        }
        # newline='\n': el Markdown generado usa LF también en Windows, como el resto del repositorio.
        (salida / 'PROTOCOLO_PRUEBAS.md').write_text(self._markdown(casos, defectos, indicadores, ejecuciones, entorno), encoding='utf-8', newline='\n')
        (salida / 'TRAZABILIDAD.md').write_text(self._trazabilidad(casos, fecha), encoding='utf-8', newline='\n')
        self._csv(salida / 'resultados', casos, defectos, indicadores)
        self.stdout.write(self.style.SUCCESS(
            f'Protocolo generado: {indicadores["Planificados"]} casos, {indicadores["Aprobados"]} aprobados, '
            f'{indicadores["Fallidos"]} fallidos; suite {len(por_prueba)} pruebas, {fallidas} con falla.'))

    def _evaluar_casos(self, por_prueba, fecha):
        casos = []
        for caso in protocolo.CASOS:
            fila = dict(caso)
            fila['responsable'] = protocolo.RESPONSABLE_POR_AREA.get(caso['area'], protocolo.POR_ASIGNAR)
            fila['defectos'] = [d['codigo'] for d in protocolo.DEFECTOS if d['caso'] == caso['codigo']]
            if caso['manual']:
                manual = protocolo.RESULTADOS_MANUALES.get(caso['codigo'])
                fila['estado'] = manual['estado'] if manual else 'No ejecutado'
                fila['obtenido'] = manual['obtenido'] if manual else 'Pendiente: caso manual, lo ejecuta el equipo en el entorno desplegado.'
                fila['fecha'] = manual.get('fecha', '-') if manual else '-'
                fila['evidencia'] = manual.get('evidencia', '-') if manual else '-'
            else:
                resultados = [por_prueba.get(prueba, 'No ejecutada') for prueba in caso['pruebas']]
                fila['estado'] = _estado_de(resultados)
                fallas = [p.rsplit('.', 1)[-1] for p, r in zip(caso['pruebas'], resultados) if r != 'Aprobado']
                fila['obtenido'] = ('Coincide con lo esperado: ' + f'{len(resultados)} de {len(resultados)} pruebas automáticas aprobadas.'
                                    if not fallas else 'No coincide. Pruebas con falla: ' + ', '.join(fallas))
                fila['fecha'] = fecha
                fila['evidencia'] = '; '.join(p.replace('delegaciones_app.', '') for p in caso['pruebas'])
            casos.append(fila)
        return casos

    def _evaluar_defectos(self, por_prueba):
        defectos = []
        for defecto in protocolo.DEFECTOS:
            fila = dict(defecto)
            resultados = [por_prueba.get(prueba, 'No ejecutada') for prueba in defecto['reejecucion']]
            fila['resultado_reejecucion'] = _estado_de(resultados)
            fila['estado'] = 'Corregido y verificado' if fila['resultado_reejecucion'] == 'Aprobado' else 'Abierto'
            defectos.append(fila)
        return defectos

    def _indicadores(self, casos, defectos):
        ejecutados = [c for c in casos if c['estado'] != 'No ejecutado']
        return {
            'Planificados': len(casos),
            'Ejecutados': len(ejecutados),
            'Aprobados': sum(1 for c in casos if c['estado'] == 'Aprobado'),
            'Fallidos': sum(1 for c in casos if c['estado'] == 'Fallido'),
            'Bloqueados': sum(1 for c in casos if c['estado'] == 'Bloqueado'),
            'No ejecutados (manuales pendientes)': sum(1 for c in casos if c['estado'] == 'No ejecutado'),
            'Defectos registrados': len(defectos),
            'Defectos corregidos': sum(1 for d in defectos if d['estado'] == 'Corregido y verificado'),
            'Casos reejecutados tras corrección': len({d['caso'] for d in defectos}),
            'Pruebas automáticas que respaldan casos': sum(len(c['pruebas']) for c in casos),
            'Requerimientos de la guía cubiertos': len({c['requerimiento'] for c in casos}),
        }

    def _markdown(self, casos, defectos, indicadores, ejecuciones, entorno):
        l = ['# Protocolo de pruebas del SGR (Evaluación 3)', '',
             f'Generado con `python manage.py protocolo_pruebas` el {entorno["fecha"]}. No se edita a mano: los datos de los casos, defectos '
             'y responsables están en `delegaciones_app/protocolo.py` y los resultados salen de ejecutar las pruebas automáticas.', '',
             '## 1. Entorno de ejecución', '', '| Campo | Valor |', '|---|---|',
             f'| Fecha | {entorno["fecha"]} |', f'| Python | {entorno["python"]} |', f'| Django | {entorno["django"]} |',
             f'| Base de datos de pruebas | {entorno["motor"]} (base temporal creada por el runner de Django) |',
             f'| Suite completa | {entorno["total"]} pruebas, {entorno["fallidas"]} con falla |', '',
             '## 2. Indicadores de cobertura y resultados', '', '| Indicador | Cantidad |', '|---|---|']
        l += [f'| {nombre} | {valor} |' for nombre, valor in indicadores.items()]
        l += ['', '### Cobertura por requerimiento de la guía', '', '| Requerimiento | Descripción | RF | Casos | Estado |', '|---|---|---|---|---|']
        for req, (descripcion, rf) in protocolo.REQUERIMIENTOS.items():
            propios = [c for c in casos if c['requerimiento'] == req]
            estado = 'Sin casos' if not propios else ('Aprobado' if all(c['estado'] == 'Aprobado' for c in propios) else
                                                     'Con pendientes' if all(c['estado'] in ('Aprobado', 'No ejecutado') for c in propios) else 'Con fallas')
            l.append(f'| {req} | {_celda(descripcion)} | {rf} | {", ".join(c["codigo"] for c in propios) or "-"} | {estado} |')
        l += ['', '## 3. Resumen de casos', '', '| Código | Nombre | Req. | Prioridad | Tipo | Perfil | Estado | Defecto |', '|---|---|---|---|---|---|---|---|']
        l += [f'| {c["codigo"]} | {_celda(c["nombre"])} | {c["requerimiento"]} | {c["prioridad"]} | {c["tipo"]} | {_celda(c["perfil"])} | {c["estado"]} | {", ".join(c["defectos"]) or "-"} |' for c in casos]
        l += ['', '## 4. Fichas de los casos de prueba']
        for c in casos:
            pasos = ' '.join(f'{i}. {p}' for i, p in enumerate(c['pasos'], 1))
            defecto = ', '.join(c['defectos']) or 'Ninguno'
            correccion = '; '.join(d['correccion'] for d in defectos if d['caso'] == c['codigo']) or '-'
            reejec = '; '.join(f'{d["codigo"]}: {d["resultado_reejecucion"]}' for d in defectos if d['caso'] == c['codigo']) or '-'
            l += ['', f'### {c["codigo"]} · {c["nombre"]}', '', '| Campo | Detalle |', '|---|---|',
                  f'| Código | {c["codigo"]} |', f'| Nombre | {_celda(c["nombre"])} |',
                  f'| Requerimiento asociado | {c["requerimiento"]}: {_celda(protocolo.REQUERIMIENTOS[c["requerimiento"]][0])} ({protocolo.REQUERIMIENTOS[c["requerimiento"]][1]}) |',
                  f'| Prioridad | {c["prioridad"]} |', f'| Tipo de prueba | {c["tipo"]}{" (manual)" if c["manual"] else " (automatizada)"} |',
                  f'| Precondiciones | {_celda(c["precondiciones"])} |', f'| Perfil de usuario | {_celda(c["perfil"])} |', f'| Datos de prueba | {_celda(c["datos"])} |',
                  f'| Pasos | {_celda(pasos)} |', f'| Resultado esperado | {_celda(c["esperado"])} |', f'| Resultado obtenido | {_celda(c["obtenido"])} |',
                  f'| Estado final | {c["estado"]} |', f'| Responsable | {c["responsable"]} |', f'| Fecha de ejecución | {c["fecha"]} |',
                  f'| Evidencia | {_celda(c["evidencia"])} |', f'| Defecto asociado | {defecto} |', f'| Corrección | {_celda(correccion)} |',
                  f'| Reejecución | {_celda(reejec)} |']
        l += ['', '## 5. Registro de defectos', '',
              '| Código | Caso | Fecha | Severidad | Detectado en | Descripción | Causa | Impacto | Corrección | Reejecución | Estado |',
              '|---|---|---|---|---|---|---|---|---|---|---|']
        l += [f'| {d["codigo"]} | {d["caso"]} | {d["fecha"]} | {d["severidad"]} | {_celda(d["detectado"])} | {_celda(d["descripcion"])} | {_celda(d["causa"])} | '
              f'{_celda(d["impacto"])} | {_celda(d["correccion"])} | {d["resultado_reejecucion"]} ({len(d["reejecucion"])} prueba/s) | {d["estado"]} |' for d in defectos]
        l += ['', '## 6. Pruebas actualizadas por cambio de requisito', '',
              'No son defectos: la guía de la Evaluación 3 cambió el comportamiento esperado y estas pruebas existentes se ajustaron para verificar el nuevo.', '',
              '| Prueba | Cambio de requisito |', '|---|---|']
        l += [f'| {_celda(prueba)} | {_celda(motivo)} |' for prueba, motivo in protocolo.CAMBIOS_DE_REQUISITO]
        l += ['', '## 7. Historial de ejecuciones de la suite completa', '', '| N.º | Fecha | Pruebas | Con falla | Observación |', '|---|---|---|---|---|']
        l += [f'| {e["numero"]} | {e["fecha"]} | {e["pruebas"]} | {e["fallidas"]} | {_celda(e["nota"])} |' for e in ejecuciones]
        l += ['', '## 8. Incidencias de configuración resueltas', '', '| Incidencia | Causa | Solución |', '|---|---|---|']
        l += [f'| {_celda(a)} | {_celda(b)} | {_celda(c)} |' for a, b, c in protocolo.INCIDENCIAS]
        l.append('')
        return '\n'.join(l)

    def _trazabilidad(self, casos, fecha):
        l = ['# Matriz de trazabilidad (Evaluación 3)', '',
             f'Generada con `python manage.py protocolo_pruebas` el {fecha}. Relaciona cada requerimiento de la guía con su pantalla, '
             'su regla de negocio, sus casos de prueba y su estado de implementación.', '',
             '| Requerimiento | Descripción | RF | Pantalla o ruta | Regla de negocio | Casos de prueba | Estado de implementación | Estado de pruebas |',
             '|---|---|---|---|---|---|---|---|']
        for req, (descripcion, rf) in protocolo.REQUERIMIENTOS.items():
            pantalla, regla = protocolo.PANTALLAS[req]
            propios = [c for c in casos if c['requerimiento'] == req]
            automaticos = [c for c in propios if not c['manual']]
            implementado = 'Implementado' if automaticos and all(c['estado'] == 'Aprobado' for c in automaticos) else 'Implementado con observaciones'
            pruebas = 'Aprobado' if propios and all(c['estado'] == 'Aprobado' for c in propios) else \
                ('Aprobado (manuales pendientes)' if all(c['estado'] in ('Aprobado', 'No ejecutado') for c in propios) else 'Con fallas')
            l.append(f'| {req} | {_celda(descripcion)} | {rf} | {_celda(pantalla)} | {_celda(regla)} | {", ".join(c["codigo"] for c in propios)} | {implementado} | {pruebas} |')
        l.append('')
        return '\n'.join(l)

    def _csv(self, carpeta, casos, defectos, indicadores):
        with open(carpeta / 'protocolo_casos.csv', 'w', newline='', encoding='utf-8-sig') as archivo:
            escritor = csv.writer(archivo, delimiter=';')
            escritor.writerow(['codigo', 'nombre', 'requerimiento', 'prioridad', 'tipo', 'area', 'manual', 'pruebas', 'estado', 'defectos'])
            for c in casos:
                escritor.writerow([c['codigo'], c['nombre'], c['requerimiento'], c['prioridad'], c['tipo'], c['area'], 'sí' if c['manual'] else 'no',
                                   len(c['pruebas']), c['estado'], ','.join(c['defectos'])])
        with open(carpeta / 'protocolo_defectos.csv', 'w', newline='', encoding='utf-8-sig') as archivo:
            escritor = csv.writer(archivo, delimiter=';')
            escritor.writerow(['codigo', 'caso', 'fecha', 'severidad', 'detectado', 'reejecucion', 'estado'])
            for d in defectos:
                escritor.writerow([d['codigo'], d['caso'], d['fecha'], d['severidad'], d['detectado'], d['resultado_reejecucion'], d['estado']])
        with open(carpeta / 'protocolo_indicadores.csv', 'w', newline='', encoding='utf-8-sig') as archivo:
            escritor = csv.writer(archivo, delimiter=';')
            escritor.writerow(['indicador', 'cantidad'])
            escritor.writerows(indicadores.items())
