from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import Actividad, Cargo, Catalogo, Compromiso, Delegacion, Evidencia, Funcionario, ItemMedible, Meta, Periodo, Rol, VersionOptimistaMixin
from .permisos import ADMINISTRADOR, ROLES_DEL_SISTEMA, funcionario_de, puede_ver_todo


class FormularioBootstrap:
    """Agrega las clases de Bootstrap a los widgets de un formulario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            widget = campo.widget
            if isinstance(widget, forms.CheckboxInput):
                clase = 'form-check-input'
            elif isinstance(widget, forms.Select):
                clase = 'form-select'
            else:
                clase = 'form-control'
            widget.attrs['class'] = f"{widget.attrs.get('class', '')} {clase}".strip()


class DelegacionForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Delegacion
        fields = ['nombre', 'ambito', 'enfasis', 'estado']
        labels = {'ambito': 'Ámbito', 'enfasis': 'Énfasis', 'estado': 'Delegación activa'}
        widgets = {'enfasis': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['enfasis'].required = False


class CargoForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ['nombre', 'vigencia']
        labels = {'vigencia': 'Cargo vigente'}


class RolForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Rol
        fields = ['nombre_rol']
        labels = {'nombre_rol': 'Nombre del rol'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.nombre_rol in ROLES_DEL_SISTEMA:
            self.fields['nombre_rol'].disabled = True
            self.fields['nombre_rol'].help_text = 'Es un rol del sistema: los permisos lo consultan por su nombre y no se renombra.'


class FuncionarioForm(FormularioBootstrap, forms.ModelForm):
    """Alta y edición de un Funcionario junto con su cuenta de acceso y sus roles."""

    campos_sin_auditar = ('password', 'password_confirm')

    username = forms.CharField(max_length=150, label='Nombre de usuario', help_text='Es también el identificador institucional.', widget=forms.TextInput(attrs={'autocomplete': 'username'}))
    email = forms.EmailField(required=False, label='Correo electrónico', widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    roles = forms.ModelMultipleChoiceField(queryset=Rol.objects.all(), label='Roles', help_text='Mantén Ctrl presionado para elegir más de uno.')
    password = forms.CharField(required=False, label='Contraseña', widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}), help_text='Obligatoria al crear. Déjala vacía al editar para conservar la actual.')
    password_confirm = forms.CharField(required=False, label='Confirmar contraseña', widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))

    class Meta:
        model = Funcionario
        fields = ['nombre', 'cargo', 'delegacion', 'estado']
        labels = {'cargo': 'Cargo', 'delegacion': 'Delegación', 'estado': 'Cuenta activa'}
        help_texts = {'delegacion': 'Déjala vacía para roles de alcance global (administrador, coordinador).'}

    field_order = ['username', 'nombre', 'email', 'cargo', 'delegacion', 'roles', 'estado', 'password', 'password_confirm']

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor = actor
        # Solo cargos vigentes y delegaciones activas; al editar se conserva la actual aunque se haya desactivado.
        self.fields['cargo'].queryset = Cargo.objects.filter(Q(vigencia=True) | Q(pk=self.instance.cargo_id))
        self.fields['delegacion'].queryset = Delegacion.objects.filter(Q(estado=True) | Q(pk=self.instance.delegacion_id))
        if self.instance.pk:
            usuario = self.instance.usuario
            self.fields['username'].initial = usuario.username
            self.fields['email'].initial = usuario.email
            self.fields['roles'].initial = self.instance.roles.all()
        else:
            self.fields['password'].required = True
            self.fields['password_confirm'].required = True

    def clean_username(self):
        username = self.cleaned_data['username']
        usuarios = User.objects.filter(username__iexact=username)
        funcionarios = Funcionario.objects.filter(identificador_institucional__iexact=username)
        if self.instance.pk:
            usuarios = usuarios.exclude(pk=self.instance.usuario_id)
            funcionarios = funcionarios.exclude(pk=self.instance.pk)
        if usuarios.exists() or funcionarios.exists():
            raise forms.ValidationError('Ya existe una cuenta con este nombre de usuario.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        if password != cleaned_data.get('password_confirm'):
            self.add_error('password_confirm', 'Las contraseñas no coinciden.')
        if password:
            usuario = User(username=cleaned_data.get('username', ''), first_name=cleaned_data.get('nombre', ''))
            try:
                validate_password(password, usuario)
            except ValidationError as error:
                self.add_error('password', error)
        if self.instance.pk and self.actor and self.instance.usuario_id == self.actor.pk:
            if cleaned_data.get('estado') is False:
                self.add_error('estado', 'No puedes desactivar tu propia cuenta.')
            roles = cleaned_data.get('roles')
            if roles is not None and self.instance.roles.filter(nombre_rol=ADMINISTRADOR).exists() and not any(rol.nombre_rol == ADMINISTRADOR for rol in roles):
                self.add_error('roles', 'No puedes quitarte el rol administrador.')
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        datos = self.cleaned_data
        funcionario = super().save(commit=False)
        usuario = self.instance.usuario if self.instance.pk else User()
        usuario.username = datos['username']
        usuario.first_name = datos['nombre'][:150]
        usuario.email = datos['email']
        usuario.is_active = datos['estado']
        if datos.get('password'):
            usuario.set_password(datos['password'])
        usuario.save()
        funcionario.usuario = usuario
        funcionario.identificador_institucional = usuario.username
        funcionario.save()
        funcionario.roles.set(datos['roles'])
        return funcionario


class CatalogoForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Catalogo
        fields = ['codigo', 'nombre', 'tipo', 'subtipo', 'area', 'activo']
        labels = {'codigo': 'Código', 'activo': 'Elemento activo'}
        help_texts = {'codigo': 'Debe ser único en todo el catálogo.'}


class PeriodoForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Periodo
        fields = ['nombre', 'fecha_inicio', 'fecha_termino', 'umbral_minimo']
        labels = {'nombre': 'Nombre del período', 'fecha_inicio': 'Fecha de inicio', 'fecha_termino': 'Fecha de término', 'umbral_minimo': 'Umbral colectivo (%)'}
        help_texts = {'umbral_minimo': 'Porcentaje mínimo para considerar cumplida la meta colectiva (RN-006).'}
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_termino': forms.DateInput(attrs={'type': 'date'}),
            'umbral_minimo': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': '0.01'}),
        }

    def clean_umbral_minimo(self):
        valor = self.cleaned_data['umbral_minimo']
        if not 0 <= valor <= 100:
            raise forms.ValidationError('El umbral debe estar entre 0 y 100 %.')
        return valor


class ItemMedibleForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = ItemMedible
        fields = ['cargo', 'periodo', 'nombre', 'servicio', 'ponderacion']
        labels = {'ponderacion': 'Ponderación (%)'}
        help_texts = {'ponderacion': 'Las ponderaciones de un cargo en un período deben sumar 100 % (RN-001).'}
        widgets = {'ponderacion': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': '0.01'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['periodo'].queryset = Periodo.objects.exclude(estado='cerrado')
        if self.instance.pk:
            # Un ítem no cambia de cargo ni de período una vez creado.
            self.fields['cargo'].disabled = True
            self.fields['periodo'].disabled = True
            self.fields['periodo'].queryset = Periodo.objects.all()


class MetaForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Meta
        fields = ['item', 'funcionario', 'valor_objetivo', 'unidad', 'ponderador']
        labels = {'item': 'Ítem medible', 'valor_objetivo': 'Valor objetivo', 'ponderador': 'Ponderador (%)'}
        help_texts = {'valor_objetivo': 'Debe ser mayor que cero (RN-002).', 'ponderador': 'Peso de la meta en el cumplimiento colectivo.'}
        widgets = {
            'valor_objetivo': forms.NumberInput(attrs={'min': 0.01, 'step': '0.01'}),
            'ponderador': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].queryset = ItemMedible.objects.exclude(periodo__estado='cerrado').select_related('cargo', 'periodo')
        self.fields['funcionario'].queryset = Funcionario.objects.filter(Q(estado=True) | Q(pk=self.instance.funcionario_id))
        if self.instance.pk:
            self.fields['item'].disabled = True
            self.fields['item'].queryset = ItemMedible.objects.select_related('cargo', 'periodo')


class VersionOptimistaForm:
    """Campo oculto `version` para el bloqueo optimista (RF-034): si otro usuario guardó antes, se rechaza."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['version'] = forms.IntegerField(widget=forms.HiddenInput, initial=self.instance.version)

    def clean(self):
        cleaned_data = super().clean()
        version = cleaned_data.get('version')
        if self.instance.pk and version is not None and version != self.instance.version:
            raise ValidationError(VersionOptimistaMixin.MENSAJE_CONCURRENCIA)
        return cleaned_data


class ActividadForm(VersionOptimistaForm, FormularioBootstrap, forms.ModelForm):
    def __init__(self, *args, user=None, compromisos=None, **kwargs):
        super().__init__(*args, **kwargs)
        funcionario = funcionario_de(user) if user else None
        ve_todo = bool(user) and puede_ver_todo(user)
        delegaciones, items = Q(estado=True), Q(periodo__estado='abierto')
        if funcionario and not ve_todo:
            # Quien tiene delegación registra en la suya, y solo sobre los ítems de su cargo.
            if funcionario.delegacion_id:
                delegaciones &= Q(pk=funcionario.delegacion_id)
            items &= Q(cargo_id=funcionario.cargo_id)
        # Al editar se conservan los valores actuales aunque luego dejen de estar disponibles.
        self.fields['delegacion'].queryset = Delegacion.objects.filter(delegaciones | Q(pk=self.instance.delegacion_id))
        self.fields['item'].queryset = ItemMedible.objects.filter(items | Q(pk=self.instance.item_id)).select_related('cargo', 'periodo')
        self.fields['catalogo'].queryset = Catalogo.objects.filter(Q(tipo='atencion', activo=True) | Q(pk=self.instance.catalogo_id))
        self.fields['catalogo'].label_from_instance = lambda elemento: elemento.nombre
        self.fields['compromiso'].queryset = (compromisos if compromisos is not None else Compromiso.objects.all()).select_related('delegacion')
        for campo in ('item', 'catalogo', 'fecha'):
            self.fields[campo].required = True
        self.fields['fecha'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M']
        if not self.instance.pk:
            self.fields['fecha'].initial = timezone.localtime().replace(second=0, microsecond=0)

    class Meta:
        model = Actividad
        fields = ['delegacion', 'item', 'catalogo', 'fecha', 'solicitud_problema', 'accion', 'contacto_nombre', 'contacto_telefono', 'compromiso']
        labels = {
            'item': 'Ítem de medición', 'catalogo': 'Tipo de atención', 'fecha': 'Fecha y hora',
            'solicitud_problema': 'Solicitud o problema', 'accion': 'Acción ejecutada',
            'contacto_nombre': 'Nombre de contacto', 'contacto_telefono': 'Teléfono de contacto', 'compromiso': 'Compromiso vinculado (opcional)',
        }
        help_texts = {'item': 'Solo ítems de períodos abiertos. La fecha debe caer dentro del período del ítem.'}
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'solicitud_problema': forms.Textarea(attrs={'rows': 3}),
            'accion': forms.Textarea(attrs={'rows': 3}),
        }


class EvidenciaForm(FormularioBootstrap, forms.ModelForm):
    comentario = forms.CharField(required=False, label='Comentario', widget=forms.Textarea(attrs={'rows': 2}))

    class Meta:
        model = Evidencia
        fields = ['archivo_vinculo']
        labels = {'archivo_vinculo': 'Archivo'}
        help_texts = {'archivo_vinculo': 'Formatos permitidos: JPG, PNG o PDF.'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['archivo_vinculo'].required = True


class CompromisoForm(VersionOptimistaForm, FormularioBootstrap, forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        funcionario = funcionario_de(user) if user else None
        ve_todo = bool(user) and puede_ver_todo(user)
        delegaciones, responsables = Q(estado=True), Q(estado=True)
        if funcionario and funcionario.delegacion_id and not ve_todo:
            delegaciones &= Q(pk=funcionario.delegacion_id)
            responsables = Q(pk=funcionario.pk)
        self.fields['delegacion'].queryset = Delegacion.objects.filter(delegaciones | Q(pk=self.instance.delegacion_id))
        self.fields['funcionario_responsable'].queryset = Funcionario.objects.filter(responsables | Q(pk=self.instance.funcionario_responsable_id))
        self.fields['item'].queryset = ItemMedible.objects.exclude(periodo__estado='cerrado').select_related('cargo', 'periodo')
        for campo in ('funcionario_responsable', 'origen'):
            self.fields[campo].required = True
        self.fields['origen'].initial = 'externo'
        if self.instance.pk:
            # El estado cambia con las acciones de la agenda, que dejan su historial.
            del self.fields['estado']

    class Meta:
        model = Compromiso
        fields = ['delegacion', 'funcionario_responsable', 'origen', 'solicitante', 'territorio', 'eje', 'descripcion', 'fecha_comprometida', 'area_apoyo', 'item', 'estado', 'observacion']
        labels = {'funcionario_responsable': 'Responsable', 'area_apoyo': 'Área de apoyo', 'item': 'Ítem medible (opcional)'}
        widgets = {'fecha_comprometida': forms.DateInput(attrs={'type': 'date'}), 'descripcion': forms.Textarea(attrs={'rows': 3}), 'observacion': forms.Textarea(attrs={'rows': 2})}
