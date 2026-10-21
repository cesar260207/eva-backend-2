from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from .models import Actividad, Cargo, Catalogo, Compromiso, Delegacion, Evidencia, Funcionario, ItemMedible, Meta, Periodo, Rol
from .permisos import ADMINISTRADOR, ROLES_DEL_SISTEMA


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


class ActividadForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        perfil = getattr(user, 'perfil', None)
        if perfil and perfil.delegacion_id and perfil.rol in {'funcionario', 'delegado'}:
            self.fields['delegacion'].queryset = Delegacion.objects.filter(pk=perfil.delegacion_id, activa=True)
        else:
            self.fields['delegacion'].queryset = Delegacion.objects.filter(activa=True)
        if self.instance.pk:
            # Al editar se conserva la delegación actual aunque luego se haya desactivado.
            self.fields['delegacion'].queryset |= Delegacion.objects.filter(pk=self.instance.delegacion_id)

    class Meta:
        model = Actividad
        fields = ['delegacion', 'fecha', 'tipo_atencion', 'descripcion', 'accion', 'item_medicion', 'contacto', 'telefono']
        widgets = {'fecha': forms.DateInput(attrs={'type': 'date'}), 'descripcion': forms.Textarea(attrs={'rows': 3}), 'accion': forms.Textarea(attrs={'rows': 3})}


class EvidenciaForm(forms.ModelForm):
    class Meta:
        model = Evidencia
        fields = ['archivo', 'comentario']
        widgets = {'comentario': forms.Textarea(attrs={'rows': 2})}


class CompromisoForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        perfil = getattr(user, 'perfil', None)
        if perfil and perfil.delegacion_id and perfil.rol in {'funcionario', 'delegado'}:
            self.fields['delegacion'].queryset = Delegacion.objects.filter(pk=perfil.delegacion_id, activa=True)
            self.fields['responsable'].queryset = self.fields['responsable'].queryset.filter(pk=user.pk)
        else:
            self.fields['delegacion'].queryset = Delegacion.objects.filter(activa=True)

    class Meta:
        model = Compromiso
        fields = ['delegacion', 'responsable', 'solicitante', 'territorio', 'eje', 'descripcion', 'fecha_comprometida', 'estado', 'observacion']
        widgets = {'fecha_comprometida': forms.DateInput(attrs={'type': 'date'}), 'descripcion': forms.Textarea(attrs={'rows': 3}), 'observacion': forms.Textarea(attrs={'rows': 2})}
