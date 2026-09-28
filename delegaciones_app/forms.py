from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Actividad, CatalogoItem, Compromiso, Delegacion, Evidencia, PerfilUsuario, PeriodoMedicion


class DelegacionForm(forms.ModelForm):
    class Meta:
        model = Delegacion
        fields = ['nombre', 'territorio', 'enfasis', 'activa']
        widgets = {'enfasis': forms.Textarea(attrs={'rows': 4})}


class CatalogoItemForm(forms.ModelForm):
    class Meta:
        model = CatalogoItem
        fields = ['categoria', 'codigo', 'nombre', 'area', 'activo']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PerfilUsuarioForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label='Nombre de usuario', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'username'}))
    first_name = forms.CharField(max_length=150, required=False, label='Nombre', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'given-name'}))
    last_name = forms.CharField(max_length=150, required=False, label='Apellidos', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'family-name'}))
    email = forms.EmailField(required=False, label='Correo electrónico', widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}))
    password = forms.CharField(required=False, label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}), help_text='Obligatoria al crear. Déjala vacía al editar para conservar la actual.')
    password_confirm = forms.CharField(required=False, label='Confirmar contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}))
    usuario_activo = forms.BooleanField(required=False, label='Cuenta activa', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = PerfilUsuario
        fields = ['rol', 'delegacion', 'cargo']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'delegacion': forms.Select(attrs={'class': 'form-select'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {'rol': 'Rol', 'delegacion': 'Delegación', 'cargo': 'Cargo'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        usuario = self.instance.usuario if self.instance.pk else None
        if usuario:
            self.fields['username'].initial = usuario.username
            self.fields['first_name'].initial = usuario.first_name
            self.fields['last_name'].initial = usuario.last_name
            self.fields['email'].initial = usuario.email
            self.fields['usuario_activo'].initial = usuario.is_active
        else:
            self.fields['password'].required = True
            self.fields['password_confirm'].required = True

    def clean_username(self):
        username = self.cleaned_data['username']
        usuarios = User.objects.filter(username__iexact=username)
        if self.instance.pk:
            usuarios = usuarios.exclude(pk=self.instance.usuario_id)
        if usuarios.exists():
            raise forms.ValidationError('Ya existe una cuenta con este nombre de usuario.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password != password_confirm:
            self.add_error('password_confirm', 'Las contraseñas no coinciden.')
        if password:
            usuario = User(
                username=cleaned_data.get('username', ''),
                first_name=cleaned_data.get('first_name', ''),
                last_name=cleaned_data.get('last_name', ''),
            )
            try:
                validate_password(password, usuario)
            except ValidationError as error:
                self.add_error('password', error)
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        perfil = super().save(commit=False)
        usuario = perfil.usuario if self.instance.pk else User()
        usuario.username = self.cleaned_data['username']
        usuario.first_name = self.cleaned_data['first_name']
        usuario.last_name = self.cleaned_data['last_name']
        usuario.email = self.cleaned_data['email']
        usuario.is_active = self.cleaned_data['usuario_activo']
        if self.cleaned_data.get('password'):
            usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
            perfil.usuario = usuario
            perfil.save()
        return perfil


class PeriodoMedicionForm(forms.ModelForm):
    class Meta:
        model = PeriodoMedicion
        fields = ['nombre', 'inicio', 'termino', 'estado', 'version_parametros', 'umbral_colectivo', 'maximo_cumplimiento']
        labels = {
            'nombre': 'Nombre del período',
            'inicio': 'Fecha de inicio',
            'termino': 'Fecha de término',
            'estado': 'Estado',
            'version_parametros': 'Versión de parámetros',
            'umbral_colectivo': 'Umbral colectivo (%)',
            'maximo_cumplimiento': 'Máximo de cumplimiento (%)',
        }
        help_texts = {
            'umbral_colectivo': 'Porcentaje mínimo para considerar cumplida la meta colectiva.',
            'maximo_cumplimiento': 'Límite superior aplicado al cálculo de cumplimiento.',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'termino': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'version_parametros': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'umbral_colectivo': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'step': '0.01'}),
            'maximo_cumplimiento': forms.NumberInput(attrs={'class': 'form-control', 'min': 0.01, 'step': '0.01'}),
        }

    def clean_umbral_colectivo(self):
        valor = self.cleaned_data['umbral_colectivo']
        if valor < 0 or valor > 100:
            raise forms.ValidationError('El umbral debe estar entre 0 y 100%.')
        return valor

    def clean_maximo_cumplimiento(self):
        valor = self.cleaned_data['maximo_cumplimiento']
        if valor <= 0:
            raise forms.ValidationError('El máximo de cumplimiento debe ser mayor que cero.')
        return valor


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


class EvidenciaMantenedorForm(forms.ModelForm):
    """Alta y edición desde el mantenedor de Evidencias. A diferencia de
    EvidenciaForm, elige la actividad y ofrece la revisión solo a quien valida."""

    def __init__(self, *args, puede_validar=False, **kwargs):
        super().__init__(*args, **kwargs)
        if puede_validar:
            self.fields['aprobada'].widget.choices = [('unknown', 'Pendiente de revisión'), ('true', 'Aprobada'), ('false', 'Rechazada')]
        else:
            del self.fields['aprobada']

    class Meta:
        model = Evidencia
        fields = ['actividad', 'archivo', 'comentario', 'aprobada']
        labels = {'aprobada': 'Revisión'}
        help_texts = {
            'archivo': 'Formatos permitidos: JPG, PNG o PDF.',
            'aprobada': 'Al cambiar la revisión queda registrado quién la realizó.',
        }
        widgets = {
            'actividad': forms.Select(attrs={'class': 'form-select'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'aprobada': forms.NullBooleanSelect(attrs={'class': 'form-select'}),
        }


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
