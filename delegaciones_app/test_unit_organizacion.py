"""Pruebas unitarias de la estructura organizacional y de la configuración de la medición: delegaciones, cargos, funcionarios,
catálogos, períodos, ítems, metas y parámetros. Las que no necesitan la base de datos usan SimpleTestCase."""
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .crud import datos_relacionados, texto_relacionados
from .forms import CatalogoForm, FuncionarioForm, PeriodoForm
from .models import (
    Actividad, Auditoria, Cargo, Catalogo, Delegacion, Funcionario, FuncionarioRol, ItemMedible, Meta, ParametroVersionado, Periodo, Rol,
)
from .pruebas_base import EscenarioBase, crear_funcionario


def un_periodo(nombre='Septiembre 2026', estado='borrador', inicio=date(2026, 9, 1), termino=date(2026, 9, 30), **cambios):
    return Periodo.objects.create(nombre=nombre, fecha_inicio=inicio, fecha_termino=termino, estado=estado, **cambios)


class DelegacionUnitTests(TestCase):
    """CU-26 Administración de delegaciones, usuarios y roles (RF-001)."""

    def test_el_nombre_de_la_delegacion_es_unico(self):
        """CU-26 Administración de delegaciones (RF-001). Dos delegaciones no pueden llamarse igual."""
        Delegacion.objects.create(nombre='Centro')
        with self.assertRaises(ValidationError) as error:
            Delegacion(nombre='Centro').full_clean()
        self.assertIn('nombre', error.exception.message_dict)

    def test_set_estado_activa_y_desactiva_sin_borrar(self):
        """CU-26 Administración de delegaciones (RF-001). Desactivar conserva el registro y su historial."""
        delegacion = Delegacion.objects.create(nombre='Rural')
        delegacion.set_estado(False)
        delegacion.refresh_from_db()
        self.assertFalse(delegacion.estado)
        delegacion.set_estado(True)
        delegacion.refresh_from_db()
        self.assertTrue(delegacion.estado)

    def test_asignar_funcionario_cambia_su_delegacion(self):
        """CU-26 Administración de delegaciones (RF-002). Asignar un funcionario actualiza su delegación."""
        centro, rural = Delegacion.objects.create(nombre='Centro'), Delegacion.objects.create(nombre='Rural')
        funcionario = crear_funcionario('asignado', 'funcionario', delegacion=centro).funcionario
        rural.asignar_funcionario(funcionario)
        funcionario.refresh_from_db()
        self.assertEqual(funcionario.delegacion, rural)


class PromedioPonderadoUnitTests(SimpleTestCase):
    """CU-18.1 Consolidar datos de delegación (RF-024, RF-029). Función pura, sin base de datos."""

    @staticmethod
    def _indicador(ponderador, ponderacion):
        return SimpleNamespace(meta=SimpleNamespace(ponderador=Decimal(ponderador)), ponderacion=Decimal(ponderacion))

    def test_sin_indicadores_el_promedio_es_cero(self):
        """CU-18.1 Consolidar datos de delegación (RF-024). Sin indicadores no hay división por cero."""
        self.assertEqual(Delegacion.promedio_ponderado([]), Decimal('0.00'))

    def test_pondera_cada_meta_por_su_ponderador(self):
        """CU-18.1 Consolidar datos de delegación (RF-024). 60 % de la meta al 100 % y 40 % al 50 % dan 80 %."""
        indicadores = [self._indicador('60', '60'), self._indicador('40', '20')]
        self.assertEqual(Delegacion.promedio_ponderado(indicadores), Decimal('80.00'))


class CargoUnitTests(TestCase):
    """CU-04 Administración de funciones por cargo (RF-003, RF-006)."""

    def setUp(self):
        self.cargo = Cargo.objects.create(nombre='Profesional')
        self.periodo = un_periodo()
        self.item = ItemMedible.objects.create(cargo=self.cargo, periodo=self.periodo, nombre='Atención', ponderacion=40)

    def test_verificar_vigencia_refleja_el_estado_del_cargo(self):
        """CU-04 Administración de funciones por cargo (RF-003). Un cargo retirado no está vigente."""
        self.assertTrue(self.cargo.verificar_vigencia())
        self.cargo.vigencia = False
        self.assertFalse(self.cargo.verificar_vigencia())

    def test_actualizar_ponderaciones_guarda_un_valor_valido(self):
        """CU-04.1 Validar reglas de configuración (RF-006). Una ponderación que respeta el 100 % se guarda."""
        self.cargo.actualizar_ponderaciones(self.item, '70')
        self.item.refresh_from_db()
        self.assertEqual(self.item.ponderacion, Decimal('70.00'))

    def test_actualizar_ponderaciones_rechaza_un_item_de_otro_cargo(self):
        """CU-04.1 Validar reglas de configuración (RF-006). El ítem debe pertenecer al cargo."""
        otro = Cargo.objects.create(nombre='Técnico')
        with self.assertRaises(ValidationError):
            otro.actualizar_ponderaciones(self.item, '50')

    def test_actualizar_ponderaciones_bloquea_una_suma_superior_a_100(self):
        """CU-04.2 Bloquear guardado por ponderación inválida (RF-006). Más de 100 % no se guarda."""
        ItemMedible.objects.create(cargo=self.cargo, periodo=self.periodo, nombre='Operativos', ponderacion=50)
        with self.assertRaises(ValidationError):
            self.cargo.actualizar_ponderaciones(self.item, '60')
        self.item.refresh_from_db()
        self.assertEqual(self.item.ponderacion, Decimal('40.00'))


class FuncionarioUnitTests(TestCase):
    """CU-26 Administración de delegaciones, usuarios y roles (RF-002)."""

    def test_reasignar_cargo_vigente(self):
        """CU-26 Administración de usuarios (RF-002). Un funcionario puede pasar a un cargo vigente."""
        funcionario = crear_funcionario('reasignado', 'funcionario').funcionario
        nuevo = Cargo.objects.create(nombre='Coordinación')
        funcionario.reasignar_cargo(nuevo)
        funcionario.refresh_from_db()
        self.assertEqual(funcionario.cargo, nuevo)

    def test_reasignar_a_un_cargo_no_vigente_se_rechaza(self):
        """CU-26 Administración de usuarios (RF-002). No se reasigna a un cargo retirado."""
        funcionario = crear_funcionario('rechazado', 'funcionario').funcionario
        retirado = Cargo.objects.create(nombre='Antiguo', vigencia=False)
        with self.assertRaises(ValidationError):
            funcionario.reasignar_cargo(retirado)
        funcionario.refresh_from_db()
        self.assertNotEqual(funcionario.cargo, retirado)

    def test_el_identificador_institucional_es_unico(self):
        """CU-26 Administración de usuarios (RF-002). Dos funcionarios no comparten identificador."""
        crear_funcionario('repetido', 'funcionario')
        otro = crear_funcionario('distinto', 'funcionario').funcionario
        otro.identificador_institucional = 'repetido'
        with self.assertRaises(ValidationError):
            otro.full_clean()


class FuncionarioFormUnitTests(TestCase):
    """CU-26 Administración de delegaciones, usuarios y roles (RF-002): validaciones del formulario de funcionarios."""

    def setUp(self):
        self.cargo = Cargo.objects.create(nombre='Profesional')
        self.delegacion = Delegacion.objects.create(nombre='Centro')
        self.rol = Rol.objects.get(nombre_rol='funcionario')

    def _datos(self, **cambios):
        datos = {
            'username': 'ana.perez', 'nombre': 'Ana Pérez', 'email': 'ana@laserena.cl', 'cargo': self.cargo.pk,
            'delegacion': self.delegacion.pk, 'roles': [self.rol.pk], 'estado': 'on',
            'password': 'Clave-segura-2026', 'password_confirm': 'Clave-segura-2026',
        }
        datos.update(cambios)
        return datos

    def test_un_alta_valida_crea_cuenta_funcionario_y_roles(self):
        """CU-26 Administración de usuarios (RF-002). El alta crea la cuenta, el funcionario y sus roles."""
        formulario = FuncionarioForm(self._datos())
        self.assertTrue(formulario.is_valid(), formulario.errors)
        funcionario = formulario.save()
        self.assertEqual(funcionario.identificador_institucional, 'ana.perez')
        self.assertTrue(funcionario.usuario.check_password('Clave-segura-2026'))
        self.assertEqual(list(funcionario.roles.all()), [self.rol])

    def test_un_nombre_de_usuario_repetido_se_rechaza(self):
        """CU-26 Administración de usuarios (RF-002). Sin cuentas duplicadas, sin distinguir mayúsculas."""
        crear_funcionario('Ana.Perez', 'funcionario')
        formulario = FuncionarioForm(self._datos())
        self.assertFalse(formulario.is_valid())
        self.assertIn('username', formulario.errors)

    def test_las_contrasenas_deben_coincidir(self):
        """CU-26 Administración de usuarios (RF-002, RNF-004). La confirmación debe ser igual."""
        formulario = FuncionarioForm(self._datos(password_confirm='Otra-clave-2026'))
        self.assertFalse(formulario.is_valid())
        self.assertIn('password_confirm', formulario.errors)

    def test_una_contrasena_debil_se_rechaza(self):
        """CU-26 Administración de usuarios (RF-002, RNF-004). Se aplican los validadores de contraseña."""
        formulario = FuncionarioForm(self._datos(password='12345678', password_confirm='12345678'))
        self.assertFalse(formulario.is_valid())
        self.assertIn('password', formulario.errors)

    def test_al_crear_la_contrasena_es_obligatoria(self):
        """CU-26 Administración de usuarios (RF-002). Sin contraseña no hay alta."""
        formulario = FuncionarioForm(self._datos(password='', password_confirm=''))
        self.assertFalse(formulario.is_valid())
        self.assertIn('password', formulario.errors)

    def test_no_se_ofrecen_cargos_retirados_ni_delegaciones_inactivas(self):
        """CU-26 Administración de usuarios (RF-002). Las listas solo muestran opciones vigentes."""
        retirado = Cargo.objects.create(nombre='Antiguo', vigencia=False)
        inactiva = Delegacion.objects.create(nombre='Cerrada', estado=False)
        formulario = FuncionarioForm()
        self.assertNotIn(retirado, formulario.fields['cargo'].queryset)
        self.assertNotIn(inactiva, formulario.fields['delegacion'].queryset)

    def test_el_actor_no_puede_desactivar_su_propia_cuenta(self):
        """CU-26.1 Denegar acceso por ámbito (RF-002). Evita que el administrador se bloquee a sí mismo."""
        admin = crear_funcionario('admin-propio', 'administrador')
        formulario = FuncionarioForm(
            self._datos(username='admin-propio', roles=[Rol.objects.get(nombre_rol='administrador').pk], estado='', password='', password_confirm=''),
            instance=admin.funcionario, actor=admin,
        )
        self.assertFalse(formulario.is_valid())
        self.assertIn('estado', formulario.errors)


class CatalogoUnitTests(TestCase):
    """CU-27 Administración de catálogos (RF-004)."""

    def test_el_codigo_de_un_elemento_es_unico(self):
        """CU-27.1 Restringir elemento duplicado (RF-004). Un código repetido no se guarda."""
        Catalogo.objects.create(codigo='AT-1', nombre='Operativo', tipo='atencion')
        with self.assertRaises(ValidationError) as error:
            Catalogo(codigo='AT-1', nombre='Otro', tipo='atencion').full_clean()
        self.assertIn('codigo', error.exception.message_dict)

    def test_el_formulario_rechaza_un_codigo_duplicado(self):
        """CU-27.1 Restringir elemento duplicado (RF-004). El mantenedor informa el código repetido."""
        Catalogo.objects.create(codigo='AT-1', nombre='Operativo', tipo='atencion')
        formulario = CatalogoForm({'codigo': 'AT-1', 'nombre': 'Otro', 'tipo': 'atencion', 'activo': 'on'})
        self.assertFalse(formulario.is_valid())
        self.assertIn('codigo', formulario.errors)

    def test_el_tipo_debe_ser_uno_del_catalogo(self):
        """CU-27 Administración de catálogos (RF-004). Un tipo inventado no es válido."""
        formulario = CatalogoForm({'codigo': 'X-1', 'nombre': 'Algo', 'tipo': 'inventado', 'activo': 'on'})
        self.assertFalse(formulario.is_valid())
        self.assertIn('tipo', formulario.errors)

    def test_desactivar_oculta_el_elemento_pero_no_toca_los_registros_historicos(self):
        """CU-27 Administración de catálogos (RF-004). Los registros anteriores conservan el elemento desactivado."""
        elemento = Catalogo.objects.create(codigo='AT-2', nombre='Visita', tipo='atencion')
        autor = crear_funcionario('autor-cat', 'funcionario').funcionario
        delegacion = Delegacion.objects.create(nombre='Centro')
        periodo = un_periodo(estado='abierto')
        item = ItemMedible.objects.create(cargo=autor.cargo, periodo=periodo, nombre='Atención', ponderacion=100)
        actividad = Actividad.objects.create(
            funcionario_autor=autor, delegacion=delegacion, item=item, catalogo=elemento, fecha='2026-09-01T10:00:00-03:00',
            solicitud_problema='x', accion='y', codigo_verificador='EVD-CAT-1',
        )
        elemento.desactivar()
        actividad.refresh_from_db()
        self.assertEqual(actividad.catalogo, elemento)
        self.assertFalse(Catalogo.objects.get(pk=elemento.pk).activo)
        elemento.activar()
        self.assertTrue(Catalogo.objects.get(pk=elemento.pk).activo)


class PeriodoPuroUnitTests(SimpleTestCase):
    """CU-28 Administración de períodos (RF-005, RF-026, RF-027). Cálculos de fechas sin base de datos."""

    def setUp(self):
        self.periodo = Periodo(nombre='Septiembre', fecha_inicio=date(2026, 9, 1), fecha_termino=date(2026, 9, 30))

    def test_la_fecha_de_termino_no_puede_ser_anterior_al_inicio(self):
        """CU-28 Administración de períodos (RF-005). Un rango invertido se rechaza."""
        self.periodo.fecha_termino = date(2026, 8, 31)
        with self.assertRaises(ValidationError):
            self.periodo.clean()

    def test_un_dia_de_duracion_es_valido(self):
        """CU-28 Administración de períodos (RF-005). Inicio y término el mismo día es válido."""
        self.periodo.fecha_termino = date(2026, 9, 1)
        self.periodo.clean()

    def test_porcentaje_esperado_segun_los_dias_transcurridos(self):
        """CU-17.1 Calcular diferencia de avance (RF-026). RN-007: días transcurridos sobre días totales."""
        self.assertEqual(self.periodo.porcentaje_esperado(date(2026, 9, 15)), Decimal('50.00'))
        self.assertEqual(self.periodo.porcentaje_esperado(date(2026, 9, 30)), Decimal('100.00'))

    def test_porcentaje_esperado_no_pasa_de_los_limites(self):
        """CU-17.1 Calcular diferencia de avance (RF-026). Antes del inicio es 0 % y después del término 100 %."""
        self.assertEqual(self.periodo.porcentaje_esperado(date(2026, 8, 1)), Decimal('0.00'))
        self.assertEqual(self.periodo.porcentaje_esperado(date(2026, 12, 1)), Decimal('100.00'))

    def test_dias_restantes(self):
        """CU-28 Administración de períodos (RF-026). Días que faltan para el término."""
        self.assertEqual(self.periodo.calcular_dias_restantes(date(2026, 9, 25)), 5)
        self.assertEqual(self.periodo.calcular_dias_restantes(date(2026, 10, 5)), 0)

    def test_semaforo_verde_ambar_y_rojo(self):
        """CU-16.1 Calcular estado del semáforo (RF-027). RN-008 con esperado de 50 %."""
        dia = date(2026, 9, 15)
        self.assertEqual(self.periodo.calcular_semaforo(Decimal('50'), dia), 'verde')
        self.assertEqual(self.periodo.calcular_semaforo(Decimal('30'), dia), 'ambar')
        self.assertEqual(self.periodo.calcular_semaforo(Decimal('29.99'), dia), 'rojo')

    def test_umbral_colectivo(self):
        """CU-18 Resumen ejecutivo (RF-029). RN-006: el cumplimiento colectivo debe alcanzar el umbral."""
        self.periodo.umbral_minimo = Decimal('80')
        self.assertTrue(self.periodo.alcanza_umbral(Decimal('80')))
        self.assertFalse(self.periodo.alcanza_umbral(Decimal('79.99')))


class PeriodoUnitTests(TestCase):
    """CU-28 Administración de períodos (RF-005) y CU-28.1 Restricción por período cerrado (RN-013)."""

    def setUp(self):
        self.cargo = Cargo.objects.create(nombre='Profesional')
        self.admin = crear_funcionario('admin-periodo', 'administrador')

    def _periodo_con_items(self, *ponderaciones, estado='borrador'):
        periodo = un_periodo(estado=estado)
        for numero, ponderacion in enumerate(ponderaciones):
            ItemMedible.objects.create(cargo=self.cargo, periodo=periodo, nombre=f'Ítem {numero}', ponderacion=ponderacion)
        return periodo

    def test_guardar_calcula_los_dias_computables(self):
        """CU-28 Administración de períodos (RF-005). Septiembre tiene 30 días computables."""
        self.assertEqual(un_periodo().dias_computables, 30)

    def test_iniciar_periodo_exige_ponderaciones_que_sumen_100(self):
        """CU-28 Administración de períodos (RF-006). RN-001: cada cargo debe sumar exactamente 100 %."""
        periodo = self._periodo_con_items(60, 30)
        with self.assertRaises(ValidationError) as error:
            periodo.iniciar_periodo()
        self.assertIn('Profesional (90.00 %)', error.exception.messages[0])
        self.assertEqual(Periodo.objects.get(pk=periodo.pk).estado, 'borrador')

    def test_iniciar_periodo_con_100_pasa_a_abierto(self):
        """CU-28 Administración de períodos (RF-005). Con 100 % el período se abre."""
        periodo = self._periodo_con_items(60, 40)
        periodo.iniciar_periodo()
        self.assertEqual(Periodo.objects.get(pk=periodo.pk).estado, 'abierto')

    def test_solo_se_inicia_un_periodo_en_borrador(self):
        """CU-28 Administración de períodos (RF-005). Un período abierto no se inicia otra vez."""
        periodo = un_periodo(estado='abierto')
        with self.assertRaises(ValidationError):
            periodo.iniciar_periodo()

    def test_solo_se_cierra_un_periodo_abierto(self):
        """CU-28 Administración de períodos (RF-005). Un borrador no se cierra."""
        with self.assertRaises(ValidationError):
            un_periodo().cerrar_periodo()

    def test_cerrar_periodo_cambia_el_estado(self):
        """CU-28 Administración de períodos (RF-005). Al finalizar el ciclo el período se cierra."""
        periodo = un_periodo(estado='abierto')
        periodo.cerrar_periodo()
        self.assertEqual(Periodo.objects.get(pk=periodo.pk).estado, 'cerrado')

    def test_un_periodo_cerrado_no_se_modifica(self):
        """CU-28.1 Restricción por período cerrado (RF-038). RN-013: guardar un cerrado se rechaza."""
        periodo = un_periodo(estado='abierto')
        periodo.cerrar_periodo()
        periodo.nombre = 'Otro nombre'
        with self.assertRaises(ValidationError):
            periodo.save()
        with self.assertRaises(ValidationError):
            periodo.clean()
        self.assertEqual(Periodo.objects.get(pk=periodo.pk).nombre, 'Septiembre 2026')

    def test_un_periodo_cerrado_no_se_elimina(self):
        """CU-28.1 Restricción por período cerrado (RF-038). RN-013: tampoco se borra."""
        periodo = un_periodo(estado='abierto')
        periodo.cerrar_periodo()
        with self.assertRaises(ValidationError):
            periodo.delete()
        self.assertTrue(Periodo.objects.filter(pk=periodo.pk).exists())

    def test_reabrir_exige_un_motivo(self):
        """CU-28.1 Restricción por período cerrado (RF-036). Sin motivo no hay reapertura."""
        periodo = un_periodo(estado='abierto')
        periodo.cerrar_periodo()
        with self.assertRaises(ValidationError):
            periodo.reabrir_periodo('   ', self.admin)
        self.assertEqual(Periodo.objects.get(pk=periodo.pk).estado, 'cerrado')

    def test_reabrir_deja_auditoria_y_sube_la_version_de_parametros(self):
        """CU-28.1 Restricción por período cerrado (RF-036, RF-038). La reapertura es explícita y queda registrada."""
        periodo = un_periodo(estado='abierto')
        periodo.cerrar_periodo()
        periodo.reabrir_periodo('Corrección de una carga', self.admin)
        periodo.refresh_from_db()
        self.assertEqual((periodo.estado, periodo.version_parametros), ('abierto', 2))
        registro = Auditoria.objects.get(evento='reabrir_periodo')
        self.assertEqual(registro.entidad, 'Periodo')
        self.assertIn('Corrección de una carga', registro.valor_nuevo)

    def test_solo_se_reabre_un_periodo_cerrado(self):
        """CU-28.1 Restricción por período cerrado (RF-038). Un período abierto no se reabre."""
        with self.assertRaises(ValidationError):
            un_periodo(estado='abierto').reabrir_periodo('Motivo', self.admin)

    def test_el_formulario_rechaza_fechas_invertidas(self):
        """CU-28 Administración de períodos (RF-005). El mantenedor informa la fecha de término anterior."""
        formulario = PeriodoForm({'nombre': 'Octubre', 'fecha_inicio': '2026-10-31', 'fecha_termino': '2026-10-01', 'umbral_minimo': '80'})
        self.assertFalse(formulario.is_valid())
        self.assertIn('anterior al inicio', str(formulario.errors))

    def test_el_formulario_exige_un_umbral_entre_0_y_100(self):
        """CU-28 Administración de períodos (RF-007). RN-006: el umbral es un porcentaje."""
        for valor in ('-1', '100.01', '150'):
            formulario = PeriodoForm({'nombre': 'Octubre', 'fecha_inicio': '2026-10-01', 'fecha_termino': '2026-10-31', 'umbral_minimo': valor})
            self.assertFalse(formulario.is_valid(), valor)
            self.assertIn('umbral_minimo', formulario.errors, valor)
        formulario = PeriodoForm({'nombre': 'Octubre', 'fecha_inicio': '2026-10-01', 'fecha_termino': '2026-10-31', 'umbral_minimo': '100'})
        self.assertTrue(formulario.is_valid(), formulario.errors)


class ItemMedibleUnitTests(TestCase):
    """CU-04 Administración de funciones por cargo (RF-003, RF-006) y CU-28.1 para los ítems de un período cerrado."""

    def setUp(self):
        self.cargo = Cargo.objects.create(nombre='Profesional')
        self.periodo = un_periodo(estado='abierto')

    def _item(self, ponderacion, nombre='Atención', **cambios):
        return ItemMedible(cargo=self.cargo, periodo=self.periodo, nombre=nombre, ponderacion=Decimal(ponderacion), **cambios)

    def test_la_suma_exacta_de_100_es_valida(self):
        """CU-04.1 Validar reglas de configuración (RF-006). RN-001: 60 % más 40 % suman 100 %."""
        self._item(60, 'A').save()
        self._item(40, 'B').full_clean()

    def test_una_suma_superior_a_100_se_bloquea(self):
        """CU-04.2 Bloquear guardado por ponderación inválida (RF-006). RN-001: 60 % más 50 % no se guarda."""
        self._item(60, 'A').save()
        with self.assertRaises(ValidationError) as error:
            self._item(50, 'B').full_clean()
        self.assertIn('ponderacion', error.exception.message_dict)
        self.assertIn('110', str(error.exception))

    def test_la_ponderacion_no_puede_ser_negativa(self):
        """CU-04.2 Bloquear guardado por ponderación inválida (RF-006). Un porcentaje negativo es inválido."""
        with self.assertRaises(ValidationError) as error:
            self._item(-5).full_clean()
        self.assertIn('ponderacion', error.exception.message_dict)

    def test_al_editar_un_item_no_se_cuenta_a_si_mismo(self):
        """CU-04.1 Validar reglas de configuración (RF-006). Cambiar 60 % a 70 % con otro de 30 % es válido."""
        primero, segundo = self._item(60, 'A'), self._item(30, 'B')
        primero.save()
        segundo.save()
        primero.ponderacion = Decimal('70')
        primero.full_clean()

    def test_en_un_periodo_cerrado_no_se_crean_ni_modifican_items(self):
        """CU-28.1 Restricción por período cerrado (RF-038). RN-013 alcanza a los ítems del período."""
        item = self._item(100)
        item.save()
        self.periodo.cerrar_periodo()
        with self.assertRaises(ValidationError):
            self._item(10, 'Nuevo').save()
        item.ponderacion = Decimal('50')
        with self.assertRaises(ValidationError):
            item.save()
        with self.assertRaises(ValidationError):
            item.delete()


class MetaUnitTests(TestCase):
    """CU-05 Definición de metas (RF-007, RF-023)."""

    def setUp(self):
        self.cargo = Cargo.objects.create(nombre='Profesional')
        self.periodo = un_periodo(estado='abierto')
        self.item = ItemMedible.objects.create(cargo=self.cargo, periodo=self.periodo, nombre='Atención', ponderacion=100)
        self.funcionario = crear_funcionario('con-meta', 'funcionario', cargo=self.cargo).funcionario

    def _meta(self, valor, **cambios):
        return Meta(item=self.item, funcionario=self.funcionario, valor_objetivo=Decimal(valor), **cambios)

    def test_el_valor_objetivo_debe_ser_mayor_que_cero(self):
        """CU-05.2 Bloquear guardado por valor inválido (RF-007). RN-002: cero y negativos se rechazan."""
        for valor in ('0', '-3'):
            with self.assertRaises(ValidationError) as error:
                self._meta(valor).full_clean()
            self.assertIn('valor_objetivo', error.exception.message_dict, valor)

    def test_un_valor_objetivo_positivo_es_valido(self):
        """CU-05.1 Validar parámetros de meta (RF-007). El mínimo aceptado es 0,01."""
        self._meta('0.01').full_clean()
        self._meta('25').full_clean()

    def test_no_se_crea_una_meta_en_un_periodo_cerrado(self):
        """CU-05.3 Notificar período cerrado (RF-038). RN-013: los períodos cerrados no se modifican."""
        self.periodo.cerrar_periodo()
        with self.assertRaises(ValidationError) as error:
            self._meta('5').full_clean()
        self.assertIn('cerrado', str(error.exception))
        with self.assertRaises(ValidationError):
            self._meta('5').save()

    def test_evaluar_progreso_es_avance_sobre_meta_por_100(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-023). RN-004: 1 de 4 es 25 %, 1 de 3 es 33,33 %."""
        self.assertEqual(self._meta('4').evaluar_progreso(1), Decimal('25.00'))
        self.assertEqual(self._meta('3').evaluar_progreso(1), Decimal('33.33'))
        self.assertEqual(self._meta('2').evaluar_progreso(3), Decimal('150.00'))

    def test_actualizar_valor_objetivo_valida_antes_de_guardar(self):
        """CU-05.2 Bloquear guardado por valor inválido (RF-007). Un valor inválido no llega a la base."""
        meta = self._meta('5')
        meta.save()
        meta.actualizar_valor_objetivo('8')
        self.assertEqual(Meta.objects.get(pk=meta.pk).valor_objetivo, Decimal('8.00'))
        with self.assertRaises(ValidationError):
            meta.actualizar_valor_objetivo('0')
        self.assertEqual(Meta.objects.get(pk=meta.pk).valor_objetivo, Decimal('8.00'))


class ParametroUnitTests(TestCase):
    """CU-25 Modificar parámetros (RF-007, RF-038): parámetros versionados por período."""

    def setUp(self):
        self.periodo = un_periodo(estado='abierto')

    def test_obtener_parametro_devuelve_el_valor_o_el_defecto(self):
        """CU-25 Modificar parámetros (RF-007). Sin parámetro se usa el valor por defecto."""
        self.assertEqual(self.periodo.obtener_parametro('maximo_cumplimiento', '150'), '150')
        ParametroVersionado.objects.create(periodo=self.periodo, clave='maximo_cumplimiento', valor='120')
        self.assertEqual(self.periodo.obtener_parametro('maximo_cumplimiento', '150'), '120')

    def test_una_clave_no_se_repite_en_el_mismo_periodo(self):
        """CU-25 Modificar parámetros (RF-038). Cada período tiene su propio valor por clave."""
        ParametroVersionado.objects.create(periodo=self.periodo, clave='maximo_cumplimiento', valor='120')
        with self.assertRaises(ValidationError):
            ParametroVersionado(periodo=self.periodo, clave='maximo_cumplimiento', valor='130').full_clean()

    def test_cada_periodo_conserva_su_propio_valor(self):
        """CU-25 Modificar parámetros (RF-038). Cambiar un período no altera otro."""
        otro = un_periodo(nombre='Octubre 2026', inicio=date(2026, 10, 1), termino=date(2026, 10, 31), estado='abierto')
        ParametroVersionado.objects.create(periodo=self.periodo, clave='maximo_cumplimiento', valor='120')
        ParametroVersionado.objects.create(periodo=otro, clave='maximo_cumplimiento', valor='200')
        self.assertEqual(self.periodo.obtener_parametro('maximo_cumplimiento'), '120')
        self.assertEqual(otro.obtener_parametro('maximo_cumplimiento'), '200')

    def test_un_periodo_cerrado_conserva_sus_parametros(self):
        """CU-25 Modificar parámetros (RF-038). RN-013: los resultados cerrados no cambian."""
        parametro = ParametroVersionado.objects.create(periodo=self.periodo, clave='maximo_cumplimiento', valor='120')
        self.periodo.cerrar_periodo()
        parametro.valor = '999'
        with self.assertRaises(ValidationError):
            parametro.save()
        with self.assertRaises(ValidationError):
            ParametroVersionado.objects.create(periodo=self.periodo, clave='otra', valor='1')
        self.assertEqual(self.periodo.obtener_parametro('maximo_cumplimiento'), '120')

class EliminarEnMantenedoresTests(EscenarioBase, TestCase):
    """Eliminar en los mantenedores con campo de baja: se elimina sin datos relacionados; con ellos se desactiva."""

    def setUp(self):
        self.crear_escenario()
        self.admin = crear_funcionario('admin-elim', 'administrador', cargo=self.cargo)
        self.client.force_login(self.admin)

    def _url(self, slug, objeto):
        return reverse('mantenedor_eliminar', args=[slug, objeto.pk])

    def test_sin_datos_relacionados_se_elimina_con_auditoria(self):
        """CU-25 Mantener tablas maestras (RF-001, RF-003, RF-004). Delegación, cargo y catálogo sin uso se eliminan."""
        registros = {
            'delegaciones': Delegacion.objects.create(nombre='Temporal'),
            'cargos': Cargo.objects.create(nombre='Cargo sin uso'),
            'catalogo': Catalogo.objects.create(codigo='SIN-USO', nombre='Sin uso', tipo='servicio'),
        }
        for slug, objeto in registros.items():
            confirmacion = self.client.get(self._url(slug, objeto))
            self.assertContains(confirmacion, 'No tiene datos relacionados: se eliminará definitivamente.', msg_prefix=slug)
            self.assertContains(confirmacion, 'Confirmar eliminación', msg_prefix=slug)
            self.client.post(self._url(slug, objeto))
            self.assertFalse(type(objeto).objects.filter(pk=objeto.pk).exists(), slug)
            self.assertTrue(Auditoria.objects.filter(evento='eliminar', entidad=type(objeto).__name__, identificador_registro=str(objeto.pk)).exists(), slug)

    def test_con_datos_relacionados_se_desactiva_y_explica_la_razon(self):
        """CU-25 Mantener tablas maestras (RF-001, RF-003, RF-004). Con datos relacionados no se elimina: se desactiva y se dice por qué."""
        self.nueva_actividad()
        casos = (
            ('delegaciones', self.centro, 'estado', '1 actividad'),
            ('catalogo', self.catalogo, 'activo', '1 actividad'),
            ('cargos', self.cargo, 'vigencia', 'funcionarios'),
        )
        for slug, objeto, baja, motivo in casos:
            confirmacion = self.client.get(self._url(slug, objeto))
            self.assertContains(confirmacion, 'No se puede eliminar porque tiene datos relacionados', msg_prefix=slug)
            self.assertContains(confirmacion, motivo, msg_prefix=slug)
            self.assertContains(confirmacion, 'Confirmar desactivación', msg_prefix=slug)
            respuesta = self.client.post(self._url(slug, objeto), follow=True)
            self.assertContains(respuesta, 'No se eliminó porque tiene datos relacionados', msg_prefix=slug)
            objeto.refresh_from_db()
            self.assertFalse(getattr(objeto, baja), slug)

    def test_funcionario_sin_datos_se_elimina_con_su_cuenta(self):
        """CU-26 Administración de usuarios y roles (RF-002). Sin datos relacionados se eliminan el funcionario, su cuenta y sus roles."""
        usuario = crear_funcionario('sin-datos', 'funcionario', cargo=self.cargo, delegacion=self.centro)
        funcionario = usuario.funcionario
        self.assertContains(self.client.get(self._url('funcionarios', funcionario)), 'También se elimina su cuenta de acceso «sin-datos».')
        self.client.post(self._url('funcionarios', funcionario))
        self.assertFalse(Funcionario.objects.filter(pk=funcionario.pk).exists())
        self.assertFalse(User.objects.filter(pk=usuario.pk).exists())
        self.assertFalse(FuncionarioRol.objects.filter(funcionario_id=funcionario.pk).exists())

    def test_funcionario_que_trabajo_en_el_sistema_se_desactiva(self):
        """CU-26 Administración de usuarios y roles (RF-002). Quien registró actividades se desactiva con su cuenta: su trabajo se conserva."""
        self.nueva_actividad()
        respuesta = self.client.post(self._url('funcionarios', self.autor), follow=True)
        self.assertContains(respuesta, '1 actividad')
        self.autor.refresh_from_db()
        self.usuario_autor.refresh_from_db()
        self.assertEqual((self.autor.estado, self.usuario_autor.is_active), (False, False))

    def test_los_datos_relacionados_no_cuentan_lo_que_se_borra_junto(self):
        """CU-25 Mantener tablas maestras (RF-002). Los roles asignados se borran con el funcionario: no impiden eliminarlo."""
        self.assertEqual(datos_relacionados(self.verificador), [])
        self.nueva_actividad()
        self.assertEqual(datos_relacionados(self.autor), [('actividad', 1)])
        self.assertEqual(texto_relacionados(datos_relacionados(self.centro)), '1 funcionario, 1 actividad')

    def test_la_lista_ofrece_eliminar_en_activos_y_activar_en_inactivos(self):
        """CU-25 Mantener tablas maestras (RF-001). La fila activa dice «Eliminar» y la inactiva «Activar»."""
        Delegacion.objects.create(nombre='Cerrada', estado=False)
        lista = self.client.get(reverse('mantenedor_lista', args=['delegaciones']))
        self.assertContains(lista, '>Eliminar</a>')
        self.assertContains(lista, '>Activar</a>')
        self.assertNotContains(lista, '>Desactivar</a>')
