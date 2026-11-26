from django import forms
from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import (
    Actividad, Ajuste, Ausencia, Cargo, CasoSocial, Catalogo, Comentario, Compromiso, Delegacion, Evidencia, Funcionario, Hito, ItemMedible,
    MembresiaOrganizacion, Meta, Organizacion, ParametroVersionado, Periodo, ResponsableHito, Rol, SubtipoAtencion, Territorio, Vecino,
    VersionOptimistaMixin,
)
from .cuentas import generar_contrasena_temporal
from .rut import normalizar_rut
from .permisos import (
    ADMINISTRADOR, COORDINADOR, DELEGADO, PERFIL_ADMINISTRADOR, PERFIL_DELEGADO, PERFIL_FUNCIONARIO, PERFILES, ROLES_DEL_SISTEMA, ROLES_RETIRADOS, asignar_perfil,
    funcionario_de, perfil_sugerido, puede_ver_todo,
)


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
        if self.instance.pk and (self.instance.nombre_rol in ROLES_DEL_SISTEMA or self.instance.nombre_rol in ROLES_RETIRADOS):
            self.fields['nombre_rol'].disabled = True
            self.fields['nombre_rol'].help_text = 'Es un rol reservado y no se puede renombrar desde aquí.'

    def clean_nombre_rol(self):
        nombre = self.cleaned_data['nombre_rol']
        if nombre in ROLES_RETIRADOS:
            raise forms.ValidationError('Este rol fue retirado y no se puede crear ni restaurar manualmente.')
        return nombre


class FuncionarioForm(FormularioBootstrap, forms.ModelForm):
    """Alta y edición de un Funcionario junto con su cuenta de acceso, su perfil (grupo de Django) y sus roles."""

    campos_sin_auditar = ('password', 'password_confirm')

    username = forms.CharField(max_length=150, label='Nombre de usuario', help_text='Es también el identificador institucional.', widget=forms.TextInput(attrs={'autocomplete': 'username'}))
    email = forms.EmailField(required=False, label='Correo electrónico', widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    perfil = forms.ModelChoiceField(
        queryset=Group.objects.filter(name__in=PERFILES).order_by('name'), required=False, label='Perfil de acceso',
        empty_label='Según sus roles',
        help_text='Administrador: acceso total y gestión de usuarios. Coordinador: mantenedores operativos, transacciones y '
                  'revisión en todas las delegaciones. Delegado: revisa evidencias y trabaja su delegación. Profesional: '
                  'solo sus actividades, evidencias y tareas. Si lo dejas vacío, se deduce de los roles.',
    )
    roles = forms.ModelMultipleChoiceField(queryset=Rol.objects.all(), label='Roles', help_text='Mantén Ctrl presionado para elegir más de uno.')
    password = forms.CharField(
        required=False, label='Contraseña temporal', widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text='Opcional. Si la dejas vacía al crear la cuenta, el sistema genera una contraseña temporal segura y te la muestra '
                  'una sola vez. Toda contraseña asignada aquí es temporal: el funcionario debe cambiarla en su primer ingreso. '
                  'Al editar, déjala vacía para conservar la actual.',
    )
    password_confirm = forms.CharField(required=False, label='Confirmar contraseña temporal', widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    generar_temporal = forms.BooleanField(
        required=False, label='Restablecer con una contraseña temporal generada',
        help_text='Solo al editar: genera una contraseña temporal nueva y obliga a cambiarla en el próximo ingreso.',
    )

    class Meta:
        model = Funcionario
        fields = ['nombre', 'cargo', 'delegacion', 'estado']
        labels = {'cargo': 'Cargo', 'delegacion': 'Delegación', 'estado': 'Cuenta activa'}
        help_texts = {'delegacion': 'Déjala vacía para roles de alcance global (administrador, coordinador).'}

    field_order = ['username', 'nombre', 'email', 'cargo', 'delegacion', 'perfil', 'roles', 'estado', 'password', 'password_confirm', 'generar_temporal']
    campos_sin_auditar = ('password', 'password_confirm')

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
            self.fields['perfil'].initial = usuario.groups.filter(name__in=PERFILES).values_list('pk', flat=True).first()
        else:
            del self.fields['generar_temporal']
        self.contrasena_temporal = None

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
            perfil = cleaned_data.get('perfil')
            if perfil and perfil.name != PERFIL_ADMINISTRADOR and self.instance.usuario.groups.filter(name=PERFIL_ADMINISTRADOR).exists():
                self.add_error('perfil', 'No puedes quitarte el perfil Administrador.')
        self._validar_perfil_y_roles(cleaned_data)
        return cleaned_data

    def _validar_perfil_y_roles(self, cleaned_data):
        """El perfil no puede dar menos alcance que los roles: un administrador o coordinador
        con perfil Profesional tendría el alcance de su rol sin los permisos para usarlo."""
        perfil, roles = cleaned_data.get('perfil'), cleaned_data.get('roles')
        if not perfil or roles is None:
            return
        nombres = {rol.nombre_rol for rol in roles}
        if ADMINISTRADOR in nombres and perfil.name != PERFIL_ADMINISTRADOR:
            self.add_error('perfil', 'El rol administrador requiere el perfil Administrador.')
        elif COORDINADOR in nombres and perfil.name not in PERFILES[:2]:
            self.add_error('perfil', 'El rol coordinador requiere el perfil Coordinador o Administrador.')
        elif DELEGADO in nombres and perfil.name == PERFIL_FUNCIONARIO:
            self.add_error('perfil', 'El rol delegado revisa evidencias: requiere el perfil Delegado o uno superior.')
        elif perfil.name == PERFIL_DELEGADO and DELEGADO not in nombres:
            self.add_error('roles', 'El perfil Delegado requiere el rol delegado para revisar evidencias.')

    @transaction.atomic
    def save(self, commit=True):
        datos = self.cleaned_data
        funcionario = super().save(commit=False)
        usuario = self.instance.usuario if self.instance.pk else User()
        usuario.username = datos['username']
        usuario.first_name = datos['nombre'][:150]
        usuario.email = datos['email']
        usuario.is_active = datos['estado']
        nueva = datos.get('password')
        if not nueva and (not self.instance.pk or datos.get('generar_temporal')):
            # Contraseña temporal generada por el sistema: se muestra una sola vez a quien crea la cuenta.
            nueva = self.contrasena_temporal = generar_contrasena_temporal()
        if nueva:
            usuario.set_password(nueva)
            funcionario.debe_cambiar_contrasena = True
        usuario.save()
        funcionario.usuario = usuario
        funcionario.identificador_institucional = usuario.username
        funcionario.save()
        funcionario.roles.set(datos['roles'])
        asignar_perfil(usuario, datos.get('perfil') or perfil_sugerido({rol.nombre_rol for rol in datos['roles']}))
        return funcionario


class CatalogoForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Catalogo
        fields = ['codigo', 'nombre', 'tipo', 'subtipo', 'area', 'activo']
        labels = {'codigo': 'Código', 'activo': 'Elemento activo'}
        help_texts = {'codigo': 'Debe ser único en todo el catálogo.'}


class OrganizacionForm(FormularioBootstrap, forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.groups.filter(name=PERFIL_DELEGADO).exists() and not user.is_superuser:
            # Delegados verifican los registros de su ámbito; el resto de los datos los mantiene coordinación.
            for nombre in tuple(self.fields):
                if nombre != 'verificada':
                    self.fields.pop(nombre)

    class Meta:
        model = Organizacion
        fields = ['nombre', 'tipo', 'personalidad_juridica', 'domicilio', 'territorio', 'delegacion', 'unidad_territorial', 'verificada', 'observaciones', 'activa']
        labels = {
            'personalidad_juridica': 'Personalidad jurídica', 'verificada': 'Registro verificado', 'activa': 'Organización activa',
            'territorio': 'Territorio según el registro municipal', 'unidad_territorial': 'Territorio (unidad territorial)',
        }
        widgets = {'observaciones': forms.Textarea(attrs={'rows': 3})}


class ParametroVersionadoForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = ParametroVersionado
        fields = ['periodo', 'clave', 'valor', 'descripcion']
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 3})}


class PeriodoForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Periodo
        fields = ['nombre', 'fecha_inicio', 'fecha_termino', 'umbral_minimo']
        labels = {'nombre': 'Nombre del período', 'fecha_inicio': 'Fecha de inicio', 'fecha_termino': 'Fecha de término', 'umbral_minimo': 'Umbral colectivo (%)'}
        help_texts = {'umbral_minimo': 'Porcentaje mínimo para considerar cumplida la meta colectiva.'}
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
        fields = ['cargo', 'periodo', 'nombre', 'servicio', 'ponderacion', 'tipo_calculo']
        labels = {'ponderacion': 'Ponderación (%)'}
        help_texts = {'ponderacion': 'Las ponderaciones de un cargo en un período deben sumar 100 %.'}
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
        help_texts = {'valor_objetivo': 'Debe ser mayor que cero.', 'ponderador': 'Peso de la meta en el cumplimiento colectivo.'}
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


class AsignarDelegadoForm(FormularioBootstrap, forms.Form):
    """Coordinación: asigna un delegado a una delegación o lo cambia de delegación."""

    funcionario = forms.ModelChoiceField(queryset=Funcionario.objects.none(), label='Delegado')
    delegacion = forms.ModelChoiceField(queryset=Delegacion.objects.filter(estado=True), label='Delegación')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo funcionarios activos con el rol delegado; las delegaciones desactivadas no reciben delegados.
        self.fields['funcionario'].queryset = Funcionario.objects.filter(estado=True, roles__nombre_rol=DELEGADO).select_related('delegacion').distinct()
        self.fields['funcionario'].label_from_instance = lambda f: f'{f.nombre} · {f.delegacion or "sin delegación"}'

    def clean(self):
        cleaned_data = super().clean()
        funcionario, delegacion = cleaned_data.get('funcionario'), cleaned_data.get('delegacion')
        if funcionario and delegacion and funcionario.delegacion_id == delegacion.pk:
            raise forms.ValidationError(f'{funcionario.nombre} ya es delegado de {delegacion}.')
        return cleaned_data


class SelectConTipo(forms.Select):
    """Select cuyas opciones llevan data-tipo (el tipo de atención del subtipo), para filtrarlas en el navegador."""

    def __init__(self, attrs=None, tipos=None):
        super().__init__(attrs)
        self.tipos = tipos or {}

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        opcion = super().create_option(name, value, label, selected, index, subindex, attrs)
        clave = getattr(value, 'value', value)
        if clave in self.tipos:
            opcion['attrs']['data-tipo'] = str(self.tipos[clave])
        return opcion


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
        if not ve_todo:
            # Un perfil local sin delegación no puede escoger una delegación ni sus ítems.
            delegaciones &= Q(pk=funcionario.delegacion_id) if funcionario and funcionario.delegacion_id else Q(pk__in=[])
            items &= Q(cargo_id=funcionario.cargo_id) if funcionario else Q(pk__in=[])
        # Al editar se conservan los valores actuales aunque luego dejen de estar disponibles.
        self.fields['delegacion'].queryset = Delegacion.objects.filter(delegaciones | Q(pk=self.instance.delegacion_id))
        self.fields['item'].queryset = ItemMedible.objects.filter(items | Q(pk=self.instance.item_id)).select_related('cargo', 'periodo')
        self.fields['catalogo'].queryset = Catalogo.objects.filter(Q(tipo='atencion', activo=True) | Q(pk=self.instance.catalogo_id))
        self.fields['catalogo'].label_from_instance = lambda elemento: elemento.nombre
        subtipos = SubtipoAtencion.objects.filter(Q(activo=True) | Q(pk=self.instance.subtipo_atencion_id)).select_related('tipo')
        self.fields['subtipo_atencion'].queryset = subtipos
        self.fields['subtipo_atencion'].label_from_instance = lambda subtipo: subtipo.nombre
        # data-tipo en cada opción permite al navegador mostrar solo los subtipos del tipo de atención elegido.
        self.fields['subtipo_atencion'].widget = SelectConTipo(
            attrs={**self.fields['subtipo_atencion'].widget.attrs, 'data-filtra-por': 'catalogo'},
            tipos={subtipo.pk: subtipo.tipo_id for subtipo in subtipos},
        )
        self.fields['subtipo_atencion'].widget.choices = self.fields['subtipo_atencion'].choices
        hitos = Q(estado__in=('planificado', 'en_curso'))
        if not ve_todo:
            hitos &= Q(delegacion_id=funcionario.delegacion_id) if funcionario and funcionario.delegacion_id else Q(pk__in=[])
        self.fields['hito'].queryset = Hito.objects.filter(hitos | Q(pk=self.instance.hito_id))
        self.fields['compromiso'].queryset = (compromisos if compromisos is not None else Compromiso.objects.all()).select_related('delegacion')
        organizaciones = Q(activa=True)
        if not ve_todo:
            organizaciones &= Q(delegacion_id=funcionario.delegacion_id) if funcionario and funcionario.delegacion_id else Q(pk__in=[])
        self.fields['organizacion'].queryset = Organizacion.objects.filter(
            organizaciones | Q(pk=self.instance.organizacion_id)
        ).order_by('nombre')
        self.fields['tipo_accion'].required = False
        self.fields['tipo_accion'].initial = 'ejecucion'
        for campo in ('item', 'catalogo', 'fecha'):
            self.fields[campo].required = True
        self.fields['fecha'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M']
        if not self.instance.pk:
            self.fields['fecha'].initial = timezone.localtime().replace(second=0, microsecond=0)
        else:
            # Ingresar al Tubo es una decisión del registro; al modificar, la tarea ya vinculada se mantiene.
            del self.fields['ingresar_al_tubo']
            del self.fields['plazo_tubo']

    ingresar_al_tubo = forms.BooleanField(
        required=False, label='Ingresar al Tubo de seguimiento',
        help_text='Crea una tarea en el Tubo de la delegación con estos datos, para hacerle seguimiento. No es necesario si ya elegiste una tarea vinculada.',
    )
    plazo_tubo = forms.DateField(
        required=False, label='Plazo comprometido en el Tubo', widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Si lo dejas vacío, el plazo es 14 días después de la fecha de la actividad.',
    )

    def clean(self):
        cleaned_data = super().clean()
        delegacion = cleaned_data.get('delegacion')
        organizacion = cleaned_data.get('organizacion')
        if organizacion and delegacion and organizacion.delegacion_id != delegacion.pk:
            self.add_error('organizacion', 'La organización debe pertenecer a la delegación de la actividad.')
        subtipo, tipo = cleaned_data.get('subtipo_atencion'), cleaned_data.get('catalogo')
        if subtipo and tipo and subtipo.tipo_id != tipo.pk:
            self.add_error('subtipo_atencion', 'El subtipo debe pertenecer al tipo de atención elegido.')
        if cleaned_data.get('ingresar_al_tubo') and cleaned_data.get('compromiso'):
            self.add_error('ingresar_al_tubo', 'La actividad ya está vinculada a una tarea del Tubo.')
        plazo, fecha = cleaned_data.get('plazo_tubo'), cleaned_data.get('fecha')
        if plazo and fecha and plazo < timezone.localtime(fecha).date():
            self.add_error('plazo_tubo', 'El plazo no puede ser anterior a la fecha de la actividad.')
        return cleaned_data

    class Meta:
        model = Actividad
        fields = [
            'delegacion', 'lugar', 'item', 'catalogo', 'subtipo_atencion', 'fecha', 'solicitud_problema', 'accion', 'contacto_nombre',
            'contacto_telefono', 'organizacion', 'hito', 'tipo_accion', 'compromiso', 'gestion_interna',
        ]
        labels = {
            'gestion_interna': 'Gestión interna (el usuario es el delegado)', 'subtipo_atencion': 'Subtipo de atención (opcional)',
            'hito': 'Hito de la delegación (opcional)',
            'item': 'Ítem de medición', 'catalogo': 'Tipo de atención', 'fecha': 'Fecha y hora', 'lugar': 'Lugar (opcional)',
            'solicitud_problema': 'Solicitud o problema', 'accion': 'Acción ejecutada',
            'contacto_nombre': 'Nombre de contacto', 'contacto_telefono': 'Teléfono de contacto', 'compromiso': 'Tarea del tubo de trabajo vinculada (opcional)',
        }
        help_texts = {
            'lugar': 'Dónde se hizo, por ejemplo una sede vecinal, una calle o un sector.',
            'item': 'Solo ítems de períodos abiertos. La fecha debe caer dentro del período del ítem.',
            # Regla 1 de octubre: se guarda para el historial como «otra gestión», sin puntaje.
            'gestion_interna': 'Marcar si la actividad la pidió el delegado: queda como «otra gestión» y no suma puntaje. Con una tarea del tubo vinculada, manda el origen de la tarea.',
        }
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


class RevisionForm(FormularioBootstrap, forms.Form):
    """Decisión sobre las evidencias pendientes de una actividad: aprobar, o rechazar indicando el motivo (RN-009).
    La decisión llega en la URL del botón que se pulsó; el motivo, en el formulario."""

    DECISIONES = [('aprobar', 'Aprobar'), ('rechazar', 'Rechazar'), ('antecedentes', 'Solicitar más antecedentes')]
    MENSAJE_SIN_MOTIVO = 'El rechazo de una evidencia exige un motivo: quien registró la actividad lo necesita para corregirla.'
    MENSAJE_SIN_DETALLE = 'Para solicitar más antecedentes indica qué falta: quien registró la actividad lo necesita para completarla.'

    decision = forms.ChoiceField(choices=DECISIONES)
    observacion = forms.CharField(
        label='Motivo u observación', required=False, max_length=1000,
        widget=forms.Textarea(attrs={'class': 'mb-3', 'rows': 2, 'placeholder': 'Obligatorio para rechazar o solicitar más antecedentes'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('decision') == 'rechazar' and not cleaned_data.get('observacion'):
            self.add_error('observacion', self.MENSAJE_SIN_MOTIVO)
        if cleaned_data.get('decision') == 'antecedentes' and not cleaned_data.get('observacion'):
            self.add_error('observacion', self.MENSAJE_SIN_DETALLE)
        return cleaned_data


class CompromisoForm(VersionOptimistaForm, FormularioBootstrap, forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        funcionario = funcionario_de(user) if user else None
        ve_todo = bool(user) and puede_ver_todo(user)
        delegaciones, responsables = Q(estado=True), Q(estado=True)
        if not ve_todo:
            if funcionario:
                delegaciones &= Q(pk=funcionario.delegacion_id) if funcionario.delegacion_id else Q(pk__in=[])
                responsables = Q(pk=funcionario.pk)
            else:
                delegaciones &= Q(pk__in=[])
                responsables = Q(pk__in=[])
        self.fields['delegacion'].queryset = Delegacion.objects.filter(delegaciones | Q(pk=self.instance.delegacion_id))
        self.fields['funcionario_responsable'].queryset = Funcionario.objects.filter(responsables | Q(pk=self.instance.funcionario_responsable_id)).select_related('delegacion')
        self.fields['funcionario_responsable'].label_from_instance = lambda f: f'{f.nombre} · {f.delegacion or "sin delegación"}'
        if ve_todo:
            self.fields['funcionario_responsable'].label = 'Delegado responsable'
            self.fields['funcionario_responsable'].help_text = 'La coordinación asigna la tarea a un delegado de la delegación elegida.'
        self.fields['item'].queryset = ItemMedible.objects.exclude(periodo__estado='cerrado').select_related('cargo', 'periodo')
        organizaciones = Q(activa=True)
        if not ve_todo:
            organizaciones &= Q(delegacion_id=funcionario.delegacion_id) if funcionario and funcionario.delegacion_id else Q(pk__in=[])
        self.fields['organizacion'].queryset = Organizacion.objects.filter(
            organizaciones | Q(pk=self.instance.organizacion_id)
        ).order_by('nombre')
        for campo in ('funcionario_responsable', 'origen'):
            self.fields[campo].required = True
        self.fields['origen'].initial = 'externo'
        vecinos = Q(activo=True)
        if not ve_todo:
            vecinos &= Q(territorio__delegacion_id=funcionario.delegacion_id) if funcionario and funcionario.delegacion_id else Q(pk__in=[])
        self.fields['vecino'].queryset = Vecino.objects.filter(vecinos | Q(pk=self.instance.vecino_id)).select_related('territorio')
        self.fields['vecino'].required = False
        # Autocompletado: al elegir un vecino o escribir un RUT registrado, el navegador completa nombre y teléfono.
        self.fields['solicitante_rut'].widget.attrs.update({'data-autocompletar-rut': '1', 'placeholder': '12.345.678-5', 'autocomplete': 'off'})
        self.fields['vecino'].widget.attrs['data-autocompletar-vecino'] = '1'
        self.fields['tipo'].required = False
        self.fields['tipo'].initial = self.fields['tipo'].initial or 'solicitud'
        if self.instance.pk:
            # El estado cambia con las acciones de la agenda, que dejan su historial; el tipo de registro no cambia.
            del self.fields['estado']
            self.fields['tipo'].disabled = True

    def clean_solicitante_rut(self):
        return normalizar_rut(self.cleaned_data.get('solicitante_rut'))

    def clean_tipo(self):
        if self.instance.pk:
            return self.instance.tipo
        return self.cleaned_data.get('tipo') or 'solicitud'

    def clean(self):
        cleaned_data = super().clean()
        delegacion, responsable = cleaned_data.get('delegacion'), cleaned_data.get('funcionario_responsable')
        organizacion = cleaned_data.get('organizacion')
        if delegacion and responsable and responsable.delegacion_id and responsable.delegacion_id != delegacion.pk:
            self.add_error('funcionario_responsable', f'{responsable.nombre} pertenece a la delegación {responsable.delegacion}, no a {delegacion}.')
        if organizacion and delegacion and organizacion.delegacion_id != delegacion.pk:
            self.add_error('organizacion', 'La organización debe pertenecer a la delegación de la tarea.')
        return cleaned_data

    class Meta:
        model = Compromiso
        fields = [
            'tipo', 'delegacion', 'funcionario_responsable', 'origen', 'vecino', 'solicitante_rut', 'solicitante', 'solicitante_telefono', 'territorio',
            'organizacion', 'eje', 'descripcion', 'fecha_comprometida', 'area_apoyo', 'item', 'estado', 'observacion',
        ]
        labels = {
            'tipo': 'Tubo', 'funcionario_responsable': 'Responsable', 'area_apoyo': 'Área de apoyo', 'item': 'Ítem medible (opcional)',
            'vecino': 'Vecino registrado (opcional)', 'solicitante_rut': 'RUT del solicitante o remitente',
            'solicitante': 'Nombre del solicitante o remitente', 'solicitante_telefono': 'Teléfono del solicitante',
        }
        help_texts = {'vecino': 'Si el vecino ya está registrado, elígelo y sus datos se completan solos.'}
        widgets = {
            'fecha_comprometida': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'descripcion': forms.Textarea(attrs={'rows': 3}), 'observacion': forms.Textarea(attrs={'rows': 2}),
        }


def _limitar_a_delegacion_propia(campos, user):
    if not user or puede_ver_todo(user):
        return
    funcionario = funcionario_de(user)
    if not funcionario or not funcionario.delegacion_id:
        if 'funcionario' in campos:
            campos['funcionario'].queryset = Funcionario.objects.none()
        if 'delegacion' in campos:
            campos['delegacion'].queryset = Delegacion.objects.none()
        return
    if 'funcionario' in campos:
        campos['funcionario'].queryset = Funcionario.objects.filter(delegacion_id=funcionario.delegacion_id)
    if 'delegacion' in campos:
        campos['delegacion'].queryset = Delegacion.objects.filter(pk=funcionario.delegacion_id)


class AjusteForm(FormularioBootstrap, forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['respaldo'].required = True
        _limitar_a_delegacion_propia(self.fields, user)

    class Meta:
        model = Ajuste
        fields = ['tipo', 'origen', 'emisor', 'funcionario', 'delegacion', 'periodo', 'fecha', 'respaldo', 'observacion']
        widgets = {'fecha': forms.DateInput(attrs={'type': 'date'}), 'observacion': forms.Textarea(attrs={'rows': 3})}


class AusenciaForm(FormularioBootstrap, forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and not puede_ver_todo(user):
            funcionario = funcionario_de(user)
            if funcionario and funcionario.delegacion_id:
                self.fields['funcionario'].queryset = Funcionario.objects.filter(delegacion_id=funcionario.delegacion_id)
            else:
                self.fields['funcionario'].queryset = Funcionario.objects.none()

    class Meta:
        model = Ausencia
        fields = ['funcionario', 'periodo', 'tipo', 'desde', 'hasta', 'observacion']
        widgets = {
            'desde': forms.DateInput(attrs={'type': 'date'}),
            'hasta': forms.DateInput(attrs={'type': 'date'}),
            'observacion': forms.Textarea(attrs={'rows': 3}),
        }


class CasoSocialForm(FormularioBootstrap, forms.ModelForm):
    # Opciones sugeridas (datalist) para el subtipo de un informe social, según la hoja LISTA de la matriz.
    listas = {'subtipos-informe': list(CasoSocial.SUBTIPOS_INFORME)}
    ingresar_al_tubo = forms.BooleanField(
        required=False, label='Ingresar al Tubo de seguimiento',
        help_text='Crea una tarea en el Tubo de tu delegación para hacer seguimiento de esta gestión.',
    )
    plazo_tubo = forms.DateField(
        required=False, label='Plazo comprometido en el Tubo', widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Si lo dejas vacío, el plazo es 14 días desde hoy.',
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        funcionario = funcionario_de(user) if user else None
        vecinos = Q(activo=True)
        if user and not puede_ver_todo(user):
            vecinos &= Q(territorio__delegacion_id=funcionario.delegacion_id) if funcionario and funcionario.delegacion_id else Q(pk__in=[])
        self.fields['vecino'].queryset = Vecino.objects.filter(vecinos | Q(pk=self.instance.vecino_id))
        self.fields['vecino'].widget.attrs['data-autocompletar-vecino'] = '1'
        # Con un vecino elegido, nombre y teléfono se autocompletan: solo son obligatorios sin vecino (ver clean).
        self.fields['nombre_usuario'].required = False
        self.fields['telefono_usuario'].required = False
        if self.instance.pk and self.instance.compromiso_id:
            del self.fields['ingresar_al_tubo']
            del self.fields['plazo_tubo']
        # Con valor por defecto: si no se informan, la gestión ingresa hoy y sin reingresos del informe.
        self.fields['fecha_ingreso'].required = False
        self.fields['reingresos_informe'].required = False

    def clean_plazo_tubo(self):
        plazo = self.cleaned_data.get('plazo_tubo')
        if plazo and plazo < timezone.localdate():
            raise forms.ValidationError('El plazo no puede ser anterior a hoy.')
        return plazo

    def clean(self):
        cleaned_data = super().clean()
        vecino = cleaned_data.get('vecino')
        if vecino:
            cleaned_data['nombre_usuario'] = cleaned_data.get('nombre_usuario') or vecino.nombre_completo
            cleaned_data['telefono_usuario'] = cleaned_data.get('telefono_usuario') or vecino.telefono
        for campo in ('nombre_usuario', 'telefono_usuario'):
            if not cleaned_data.get(campo) and campo not in self.errors:
                self.add_error(campo, 'Este campo es obligatorio (o elige un vecino registrado que lo tenga).')
        if not cleaned_data.get('fecha_ingreso') and 'fecha_ingreso' not in self.errors:
            cleaned_data['fecha_ingreso'] = self.instance.fecha_ingreso or timezone.localdate()
        if cleaned_data.get('reingresos_informe') is None and 'reingresos_informe' not in self.errors:
            cleaned_data['reingresos_informe'] = self.instance.reingresos_informe or 0
        return cleaned_data

    class Meta:
        model = CasoSocial
        fields = [
            'vecino', 'nombre_usuario', 'telefono_usuario', 'etapa', 'tipo', 'subtipo', 'observacion',
            'fecha_ingreso', 'requiere_visita', 'fecha_programada_visita', 'fecha_visita', 'fecha_entrega_informe', 'reingresos_informe',
        ]
        labels = {
            'vecino': 'Vecino registrado (opcional)', 'nombre_usuario': 'Nombre del usuario', 'telefono_usuario': 'Teléfono del usuario',
            'etapa': 'Gestión n.º (1 a 3)', 'subtipo': 'Subtipo (sub atención)', 'fecha_ingreso': 'Fecha de ingreso',
            'requiere_visita': 'Requiere visita en terreno', 'fecha_programada_visita': 'Fecha programada de la visita',
            'fecha_visita': 'Fecha en que se hizo la visita', 'fecha_entrega_informe': 'Fecha de entrega del informe',
            'reingresos_informe': 'Reingresos del informe (0 a 2)',
        }
        help_texts = {
            'vecino': 'Si eliges un vecino registrado, su nombre y teléfono se completan solos.',
            'subtipo': 'En un informe social: Informe aporte económico, Informe aporte material o Informe institución.',
            'fecha_programada_visita': f'Plazo: hasta {CasoSocial.PLAZO_PROGRAMAR_VISITA} días desde el ingreso.',
            'fecha_visita': 'La visita debe hacerse el día programado.',
            'fecha_entrega_informe': f'Plazo: {CasoSocial.PLAZO_INFORME_TRAS_VISITA} días desde la visita y {CasoSocial.PLAZO_TOTAL_INFORME} desde el ingreso.',
        }
        widgets = {
            'observacion': forms.Textarea(attrs={'rows': 3}),
            'subtipo': forms.TextInput(attrs={'list': 'subtipos-informe'}),
            **{campo: forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d') for campo in (
                'fecha_ingreso', 'fecha_programada_visita', 'fecha_visita', 'fecha_entrega_informe')},
        }


class ComentarioForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']
        widgets = {'contenido': forms.Textarea(attrs={'rows': 3})}
        labels = {'contenido': 'Comentario'}



# Evaluación 3: mantenedores de territorios, vecinos, membresías, hitos y subtipos de atención.

def _delegaciones_del_usuario(user, actual_id=None):
    """Delegaciones activas que el usuario puede elegir: todas para coordinación; solo la propia para un perfil local."""
    delegaciones = Q(estado=True)
    if user and not puede_ver_todo(user):
        funcionario = funcionario_de(user)
        delegaciones &= Q(pk=funcionario.delegacion_id) if funcionario and funcionario.delegacion_id else Q(pk__in=[])
    return Delegacion.objects.filter(delegaciones | Q(pk=actual_id))


def _territorios_del_usuario(user, actual_id=None):
    territorios = Q(activo=True, delegacion__estado=True)
    if user and not puede_ver_todo(user):
        funcionario = funcionario_de(user)
        territorios &= Q(delegacion_id=funcionario.delegacion_id) if funcionario and funcionario.delegacion_id else Q(pk__in=[])
    return Territorio.objects.filter(territorios | Q(pk=actual_id)).select_related('delegacion')


class TerritorioForm(FormularioBootstrap, forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['delegacion'].queryset = _delegaciones_del_usuario(user, self.instance.delegacion_id)

    def clean_nombre(self):
        return ' '.join(self.cleaned_data['nombre'].split())

    class Meta:
        model = Territorio
        fields = ['nombre', 'delegacion', 'descripcion', 'activo']
        labels = {'nombre': 'Nombre del territorio', 'delegacion': 'Delegación', 'descripcion': 'Descripción', 'activo': 'Territorio activo'}
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 3})}


class VecinoForm(FormularioBootstrap, forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['territorio'].queryset = _territorios_del_usuario(user, self.instance.territorio_id)
        self.fields['rut'].widget.attrs.update({'placeholder': '12.345.678-5', 'autocomplete': 'off'})

    def clean_rut(self):
        rut = normalizar_rut(self.cleaned_data['rut'])
        if Vecino.objects.filter(rut=rut).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe un vecino registrado con este RUT.')
        return rut

    class Meta:
        model = Vecino
        fields = ['rut', 'nombres', 'apellidos', 'telefono', 'email', 'direccion', 'territorio', 'activo']
        labels = {'rut': 'RUT', 'telefono': 'Teléfono', 'email': 'Correo electrónico', 'direccion': 'Dirección', 'activo': 'Registro activo'}
        help_texts = {'rut': 'Con o sin puntos; se valida el dígito verificador.', 'territorio': 'La delegación del vecino es la de su territorio.'}


class MembresiaOrganizacionForm(FormularioBootstrap, forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        vecinos, organizaciones = Q(activo=True), Q(activa=True)
        if user and not puede_ver_todo(user):
            funcionario = funcionario_de(user)
            if funcionario and funcionario.delegacion_id:
                vecinos &= Q(territorio__delegacion_id=funcionario.delegacion_id)
                organizaciones &= Q(delegacion_id=funcionario.delegacion_id)
            else:
                vecinos = organizaciones = Q(pk__in=[])
        self.fields['vecino'].queryset = Vecino.objects.filter(vecinos | Q(pk=self.instance.vecino_id))
        self.fields['organizacion'].queryset = Organizacion.objects.filter(organizaciones | Q(pk=self.instance.organizacion_id)).order_by('nombre')

    class Meta:
        model = MembresiaOrganizacion
        fields = ['vecino', 'organizacion', 'cargo', 'fecha_inicio', 'fecha_termino']
        labels = {'organizacion': 'Organización comunitaria', 'cargo': 'Cargo', 'fecha_inicio': 'Desde', 'fecha_termino': 'Hasta (opcional)'}
        help_texts = {'cargo': 'Socio/a, o su cargo en la directiva. Presidente, vicepresidente, secretario y tesorero son únicos a la vez.'}
        widgets = {'fecha_inicio': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'), 'fecha_termino': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')}


def _etiqueta_responsable(funcionario):
    return f'{funcionario.nombre} · {funcionario.delegacion or "alcance global"}'


class HitoForm(FormularioBootstrap, forms.ModelForm):
    """Hito con un responsable principal y responsables de apoyo, guardados en ResponsableHito."""

    responsable_principal = forms.ModelChoiceField(queryset=Funcionario.objects.none(), label='Responsable principal')
    responsables_apoyo = forms.ModelMultipleChoiceField(
        queryset=Funcionario.objects.none(), required=False, label='Responsables de apoyo', help_text='Mantén Ctrl presionado para elegir más de uno.',
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['delegacion'].queryset = _delegaciones_del_usuario(user, self.instance.delegacion_id)
        self.fields['territorio'].queryset = _territorios_del_usuario(user, self.instance.territorio_id)
        funcionarios = Q(estado=True)
        if user and not puede_ver_todo(user):
            funcionario = funcionario_de(user)
            funcionarios &= Q(delegacion_id=funcionario.delegacion_id) if funcionario and funcionario.delegacion_id else Q(pk__in=[])
        candidatos = Funcionario.objects.filter(funcionarios).select_related('delegacion')
        for campo in ('responsable_principal', 'responsables_apoyo'):
            self.fields[campo].queryset = candidatos
            self.fields[campo].label_from_instance = _etiqueta_responsable
        if self.instance.pk:
            asignaciones = list(self.instance.asignaciones.all())
            self.fields['responsable_principal'].initial = next((a.funcionario_id for a in asignaciones if a.rol == 'principal'), None)
            self.fields['responsables_apoyo'].initial = [a.funcionario_id for a in asignaciones if a.rol == 'apoyo']

    def clean(self):
        cleaned_data = super().clean()
        delegacion = cleaned_data.get('delegacion')
        principal = cleaned_data.get('responsable_principal')
        apoyo = list(cleaned_data.get('responsables_apoyo') or [])
        if principal and delegacion and principal.delegacion_id not in (None, delegacion.pk):
            self.add_error('responsable_principal', f'{principal.nombre} pertenece a la delegación {principal.delegacion}, no a {delegacion}.')
        for funcionario in apoyo:
            if delegacion and funcionario.delegacion_id not in (None, delegacion.pk):
                self.add_error('responsables_apoyo', f'{funcionario.nombre} pertenece a la delegación {funcionario.delegacion}, no a {delegacion}.')
        if principal and principal in apoyo:
            self.add_error('responsables_apoyo', 'El responsable principal no se repite como apoyo.')
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        hito = super().save(commit=True)
        hito.asignaciones.all().delete()
        ResponsableHito.objects.create(hito=hito, funcionario=self.cleaned_data['responsable_principal'], rol='principal')
        for funcionario in self.cleaned_data.get('responsables_apoyo') or []:
            ResponsableHito.objects.create(hito=hito, funcionario=funcionario, rol='apoyo')
        return hito

    class Meta:
        model = Hito
        fields = ['nombre', 'descripcion', 'delegacion', 'territorio', 'fecha_programada', 'estado', 'fecha_realizacion']
        labels = {
            'delegacion': 'Delegación', 'territorio': 'Territorio (opcional)', 'fecha_programada': 'Fecha programada',
            'fecha_realizacion': 'Fecha de realización', 'descripcion': 'Descripción',
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'fecha_programada': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'fecha_realizacion': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }


class SubtipoAtencionForm(FormularioBootstrap, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].queryset = Catalogo.objects.filter(Q(tipo='atencion', activo=True) | Q(pk=self.instance.tipo_id))
        self.fields['tipo'].label_from_instance = lambda elemento: elemento.nombre

    class Meta:
        model = SubtipoAtencion
        fields = ['tipo', 'nombre', 'activo']
        labels = {'tipo': 'Tipo de atención', 'nombre': 'Nombre del subtipo', 'activo': 'Subtipo activo'}
