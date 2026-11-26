from django import forms
from django.db.models import Q
from django.utils import timezone

from delegaciones_app.forms import FormularioBootstrap
from delegaciones_app.models import Funcionario, Organizacion
from delegaciones_app.rut import es_rut_valido

from .alcance import unidades_de
from .models import Evento, Inscripcion, UnidadMunicipal, rut_canonico, validar_telefono


def mensaje_rut_duplicado(inscripcion):
    # Sin el nombre del menor: otra unidad solo necesita saber quién lo inscribió y cuándo.
    fecha = timezone.localtime(inscripcion.creado)
    return f'RUT ya ingresado por {inscripcion.unidad} el {fecha:%d-%m-%Y} para {inscripcion.evento}.'


def inscripcion_existente(evento, rut, excluir_pk=None):
    """Inscripción previa del mismo RUT en el evento, o None."""
    existente = Inscripcion.objects.select_related('unidad', 'evento').filter(evento=evento, rut=rut_canonico(rut))
    if excluir_pk:
        existente = existente.exclude(pk=excluir_pk)
    return existente.first()


class InscripcionForm(FormularioBootstrap, forms.ModelForm):
    # Más largo que el campo del modelo para aceptar «+56 9 1234 5678»; clean_telefono lo deja en 9 dígitos.
    telefono = forms.CharField(
        label='Teléfono de contacto', max_length=20, help_text='Celular de 9 dígitos (ej: 912345678).',
        widget=forms.TextInput(attrs={'inputmode': 'numeric', 'placeholder': '912345678'}),
    )

    class Meta:
        model = Inscripcion
        fields = ['evento', 'unidad', 'nombre', 'rut', 'rango_edad', 'genero', 'folio_rsh', 'tramo_rsh',
                  'organizacion', 'organizacion_otra', 'telefono']
        labels = {
            'evento': 'Actividad', 'unidad': 'Unidad municipal que ingresa la solicitud', 'nombre': 'Nombre del menor beneficiario',
            'rut': 'RUT del menor beneficiario', 'rango_edad': 'Rango de edad del menor', 'genero': 'Género del menor',
            'folio_rsh': 'N° de folio Cartola RSH en que está registrado el menor', 'tramo_rsh': 'Tramo del RSH (porcentaje en la Cartola)',
            'organizacion': 'JJ.VV. o agrupación que solicita', 'organizacion_otra': 'Otra agrupación (si no está en la lista)',
            'telefono': 'Teléfono de contacto',
        }
        help_texts = {
            'rut': 'Con o sin puntos, con guion (ej: 12345678-K). El sistema revisa el dígito verificador.',
            'organizacion': 'Elige la organización registrada; si no aparece, escríbela en el campo siguiente.',
        }
        widgets = {
            'rut': forms.TextInput(attrs={'autocomplete': 'off', 'placeholder': '12345678-K', 'data-verificar-rut': '1'}),
            'folio_rsh': forms.TextInput(attrs={'inputmode': 'numeric'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        instancia = self.instance
        self.fields['evento'].queryset = Evento.objects.filter(Q(inscripciones_abiertas=True) | Q(pk=instancia.evento_id))
        self.fields['evento'].empty_label = 'Elige'
        unidades = unidades_de(user) if user else UnidadMunicipal.objects.none()
        if instancia.pk:
            unidades = UnidadMunicipal.objects.filter(Q(pk__in=unidades.values('pk')) | Q(pk=instancia.unidad_id))
        self.fields['unidad'].queryset = unidades
        self.fields['unidad'].empty_label = 'Elige'
        if not instancia.pk:
            if len(unidades) == 1:
                self.fields['unidad'].initial = unidades[0].pk
            abiertos = list(self.fields['evento'].queryset[:2])
            if len(abiertos) == 1:
                self.fields['evento'].initial = abiertos[0].pk
        self.fields['organizacion'].queryset = Organizacion.objects.filter(Q(activa=True) | Q(pk=instancia.organizacion_id))
        self.fields['organizacion'].empty_label = 'Elige'
        self.fields['organizacion'].required = False
        self.fields['rut'].widget.attrs['data-excluir'] = instancia.pk or ''

    def clean_nombre(self):
        return ' '.join(self.cleaned_data['nombre'].split())

    def clean_rut(self):
        rut = self.cleaned_data['rut']
        if not es_rut_valido(rut):
            raise forms.ValidationError('El RUT no es válido: revisa los números y el dígito verificador.')
        return rut_canonico(rut)

    def clean_telefono(self):
        telefono = ''.join(c for c in self.cleaned_data['telefono'] if c.isdigit())
        if telefono.startswith('56') and len(telefono) == 11:
            telefono = telefono[2:]
        validar_telefono(telefono)
        return telefono

    def clean_folio_rsh(self):
        return self.cleaned_data['folio_rsh'].strip().replace('.', '')

    def clean_organizacion_otra(self):
        return ' '.join(self.cleaned_data.get('organizacion_otra', '').split())

    def clean(self):
        datos = super().clean()
        evento, rut = datos.get('evento'), datos.get('rut')
        if evento and not evento.inscripciones_abiertas:
            self.add_error('evento', f'Las inscripciones para {evento} están cerradas.')
        if evento and rut:
            previa = inscripcion_existente(evento, rut, excluir_pk=self.instance.pk)
            if previa:
                self.add_error('rut', mensaje_rut_duplicado(previa))
        if not datos.get('organizacion') and not datos.get('organizacion_otra'):
            self.add_error('organizacion', 'Indica la JJ.VV. o agrupación que solicita (de la lista o escrita en «Otra agrupación»).')
        if datos.get('organizacion'):
            datos['organizacion_otra'] = ''
        return datos


class ImportarForm(FormularioBootstrap, forms.Form):
    """Datos comunes a toda la planilla: actividad, unidad y la JJ.VV. que la entregó."""

    evento = forms.ModelChoiceField(label='Actividad', queryset=Evento.objects.none(), empty_label='Elige')
    unidad = forms.ModelChoiceField(label='Unidad municipal que ingresa la solicitud', queryset=UnidadMunicipal.objects.none(), empty_label='Elige')
    organizacion = forms.ModelChoiceField(
        label='JJ.VV. o agrupación que entrega la planilla', queryset=Organizacion.objects.none(), required=False, empty_label='Elige',
        help_text='Se usa en las filas que no traen la columna «JJ.VV. o agrupación».')
    organizacion_otra = forms.CharField(label='Otra agrupación (si no está en la lista)', max_length=255, required=False)
    archivo = forms.FileField(label='Planilla Excel (.xlsx)', help_text='Máximo 2 MB y 2.000 filas. Descarga la plantilla para el formato.',
                              widget=forms.ClearableFileInput(attrs={'accept': '.xlsx'}))
    solo_revisar = forms.BooleanField(label='Solo revisar (no guardar nada)', required=False, initial=True,
                                      help_text='Muestra qué filas tienen errores. Desmárcalo para inscribir las filas válidas.')

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['evento'].queryset = Evento.objects.filter(inscripciones_abiertas=True)
        unidades = unidades_de(user) if user else UnidadMunicipal.objects.none()
        self.fields['unidad'].queryset = unidades
        if len(unidades) == 1:
            self.fields['unidad'].initial = unidades[0].pk
        abiertos = list(self.fields['evento'].queryset[:2])
        if len(abiertos) == 1:
            self.fields['evento'].initial = abiertos[0].pk
        self.fields['organizacion'].queryset = Organizacion.objects.filter(activa=True)

    def clean_archivo(self):
        from .importacion import MAX_BYTES
        archivo = self.cleaned_data['archivo']
        if not archivo.name.lower().endswith('.xlsx'):
            raise forms.ValidationError('El archivo debe ser una planilla Excel .xlsx (si es .xls o .csv, guárdalo como .xlsx).')
        if archivo.size > MAX_BYTES:
            raise forms.ValidationError('El archivo supera los 2 MB.')
        return archivo


class EventoForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['tipo', 'anio', 'descripcion', 'inscripciones_abiertas']
        labels = {'inscripciones_abiertas': 'Inscripciones abiertas'}


class UnidadForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = UnidadMunicipal
        fields = ['nombre', 'delegacion', 'funcionarios', 'activa']
        labels = {'delegacion': 'Delegación territorial enlazada', 'funcionarios': 'Funcionarios asignados', 'activa': 'Unidad activa'}
        help_texts = {
            'delegacion': 'Los funcionarios de esta delegación inscriben a nombre de la unidad sin asignarlos uno por uno.',
            'funcionarios': 'Para unidades sin delegación (Gabinete, DIDECO, Depto. de la Familia). Mantén Ctrl para elegir varios.',
        }
        widgets = {'funcionarios': forms.SelectMultiple(attrs={'size': 10})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['funcionarios'].queryset = Funcionario.objects.filter(estado=True).order_by('nombre')
