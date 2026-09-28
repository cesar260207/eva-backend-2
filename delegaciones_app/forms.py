from django import forms

from .models import Actividad, CatalogoItem, Compromiso, Delegacion, Evidencia


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
