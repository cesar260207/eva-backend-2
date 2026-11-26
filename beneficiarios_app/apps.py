from django.apps import AppConfig


class BeneficiariosAppConfig(AppConfig):
    """Inscripción de beneficiarios (menores) para las actividades municipales de infancia: Navidad, Día del Niño
    y Aniversario. Reemplaza el Google Form «Inscripción beneficiarios actividad fin de año - Infancias»."""

    name = 'beneficiarios_app'
    verbose_name = 'Beneficiarios de actividades de infancia'
