> **Nota (Evaluación Sumativa #2):** este resumen describe la versión inicial del
> proyecto (Evaluación Sumativa #1), que leía datos desde `data/*.json`. Esa
> versión evolucionó: toda la persistencia ahora vive en una base de datos
> relacional (MySQL) a través de los modelos Django definidos en
> `delegaciones_app/models.py`, administrable desde Django Admin. Los archivos
> JSON se conservan solo como fuente de carga inicial para `seed_demo`. Ver
> `README.md` para el detalle actualizado de arquitectura e instalación.

# 📊 RESUMEN DEL PROYECTO - Gestión La Serena

## 1. ESTRUCTURA GENERAL

```
gestion_laserena/  (PROYECTO DJANGO - Contenedor Principal)
    ├── delegaciones_app/  (APP 1 - Gestión de Solicitudes)
    ├── gestion_app/       (APP 2 - Dashboard y Metas)
    ├── templates/         (HTML compartidos)
    ├── static/            (CSS, JS, Imágenes)
    ├── data/              (Datos en JSON)
    └── db.sqlite3         (Base de datos SQLite)
```

---

## 2. COMPONENTES PRINCIPALES

### 🏢 **GESTION_LASERENA** (Proyecto Principal)
**¿Qué es?** El contenedor/configuración central de todo Django

**Archivos importantes:**
- `settings.py` → Configuración del proyecto (INSTALLED_APPS, DATABASES, etc.)
- `urls.py` → Rutas principales que distribuyen a las apps
- `wsgi.py` → Servidor web
- `asgi.py` → Servidor asincrónico

**NO tiene:**
- Views propias
- Templates propios
- Modelos propios

**Es el "director de orquesta"** que coordina todo.

---

### 📋 **DELEGACIONES_APP** (Aplicación 1)
**¿Qué hace?** Gestiona solicitudes y delegaciones

**Funcionalidad:**
- Carga datos desde `solicitudes.json`
- Calcula estado automático de solicitudes
- Filtra por delegación

**Vistas (Pantallas):**
1. **index** → Página inicial con ejes y delegaciones
2. **solicitudes** → Listado completo de todas las solicitudes
3. **delegacion_detalle** → Solicitudes filtradas por delegación específica

**Rutas:**
```
GET /                              → index
GET /solicitudes/                  → solicitudes
GET /delegacion/<nombre>/          → delegacion_detalle
```

**Estados de Solicitud:**
- ✅ Realizado (verde)
- ⏳ En proceso (azul)
- ⚠️ Pendiente (amarillo)
- 🔴 Alerta Roja por Vencimiento (rojo - pasó fecha compromiso)

**Templates:**
- `delegaciones_app/index.html`
- `delegaciones_app/solicitudes.html`
- `delegaciones_app/delegacion_detalle.html`

---

### 📈 **GESTION_APP** (Aplicación 2)
**¿Qué hace?** Muestra dashboard, metas y desempeño de delegaciones

**Funcionalidad:**
- Carga datos desde `metas_delegaciones.json`
- Calcula porcentaje de cumplimiento
- Asigna colores por desempeño
- Calcula estadísticas generales

**Vistas (Pantallas):**
1. **dashboard** → Metas y cumplimiento de cada delegación
2. **semaforo** → Vista visual tipo semáforo
3. **resumen** → Estadísticas: promedio, mejor, crítico

**Rutas:**
```
GET /gestion/                      → dashboard
GET /gestion/semaforo/             → semaforo
GET /gestion/resumen/              → resumen
```

**Colores de Cumplimiento:**
- 🟢 Verde ≥80%
- 🟡 Amarillo ≥65%
- 🔴 Rojo <65%

**Templates:**
- `gestion_app/dashboard.html`
- `gestion_app/semaforo.html`
- `gestion_app/resumen.html`

---

## 3. DATOS DEL PROYECTO

### 📁 **Fuente de Datos**
Los datos están en archivos JSON (no en base de datos relacional):

**`data/solicitudes.json`**
```
Contiene:
- id
- delegacion (ej: Centro, Rural, etc.)
- estado (Realizado, En proceso, Pendiente)
- fecha_ingreso
- fecha_compromiso
- descripción
- eje
```

**`data/metas_delegaciones.json`**
```
Contiene:
- nombre_delegacion
- cumplimiento (porcentaje)
- ultimos_datos (fecha del último registro)
- meta
- indicador
```

---

## 4. ARQUITECTURA MVC

```
MODELO (Model)
  ↓
Datos en JSON (solicitudes.json, metas_delegaciones.json)
  ↓
VISTAS (View)
  ↓
delegaciones_app/views.py → procesa datos
gestion_app/views.py → procesa datos
  ↓
TEMPLATES (plantillas HTML)
  ↓
templates/delegaciones_app/*.html
templates/gestion_app/*.html
  ↓
Usuario ve en navegador
```

---

## 5. FLUJO DE NAVEGACIÓN

```
Usuario accede a http://127.0.0.1:8000/
    ↓
┌─────────────────────────────────────────────┐
│         PÁGINA DE INICIO                    │
│    (delegaciones_app/index.html)            │
│  - Muestra 4 ejes                           │
│  - Muestra 6 delegaciones                   │
└─────────────────────────────────────────────┘
    ↓
    ├─→ Usuario hace clic en "Solicitudes"
    │       ↓
    │   ┌─────────────────────────────────────────────┐
    │   │    LISTADO DE SOLICITUDES                   │
    │   │  (delegaciones_app/solicitudes.html)        │
    │   │  - Total de solicitudes                     │
    │   │  - Pendientes, En proceso, Alertas          │
    │   │  - Tabla con todos los datos                │
    │   └─────────────────────────────────────────────┘
    │       ↓
    │   Usuario elige una delegación
    │       ↓
    │   ┌─────────────────────────────────────────────┐
    │   │  DETALLE DE DELEGACIÓN                      │
    │   │ (delegaciones_app/delegacion_detalle.html)  │
    │   │ - Solo solicitudes de esa delegación        │
    │   └─────────────────────────────────────────────┘
    │
    └─→ Usuario accede a /gestion/
            ↓
        ┌─────────────────────────────────────────────┐
        │      DASHBOARD DE GESTIÓN                   │
        │    (gestion_app/dashboard.html)             │
        │  - Metas por delegación                     │
        │  - Cumplimiento (%)                         │
        │  - Colores (Verde/Amarillo/Rojo)            │
        └─────────────────────────────────────────────┘
            ↓
            ├─→ Ver Semáforo (/gestion/semaforo/)
            │   └─→ Vista visual tipo semáforo
            │
            └─→ Ver Resumen (/gestion/resumen/)
                └─→ Promedio, mejor, crítico
```

---

## 6. RESUMEN DE PANTALLAS

| Pantalla | App | Ruta | Función |
|----------|-----|------|---------|
| Inicio | delegaciones_app | `/` | Página principal |
| Solicitudes | delegaciones_app | `/solicitudes/` | Listado de todas las solicitudes |
| Detalle Delegación | delegaciones_app | `/delegacion/<nombre>/` | Solicitudes de una delegación |
| Dashboard | gestion_app | `/gestion/` | Metas y cumplimiento |
| Semáforo | gestion_app | `/gestion/semaforo/` | Vista visual |
| Resumen | gestion_app | `/gestion/resumen/` | Estadísticas generales |
| Admin | Django | `/admin/` | Panel administrativo |

---

## 7. TECNOLOGÍAS USADAS

- **Backend:** Django 6.1
- **Base de datos:** SQLite3
- **Frontend:** HTML, Bootstrap
- **Datos:** JSON (solicitudes.json, metas_delegaciones.json)
- **Python:** 3.13.14

---

## 8. FLUJO DE DATOS

```
ENTRADA DE DATOS
    ↓
JSON files (data/solicitudes.json, data/metas_delegaciones.json)
    ↓
PROCESAMIENTO
    ↓
views.py (delegaciones_app, gestion_app)
    - Carga JSON
    - Calcula estados/colores
    - Prepara contexto
    ↓
PRESENTACIÓN
    ↓
Templates HTML
    - Reciben contexto
    - Renderizan datos
    ↓
USUARIO VE
    ↓
Página HTML en navegador
```

---

## 9. CONFIGURACIÓN PRINCIPAL

### En `settings.py`:
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'delegaciones_app',      ← Registrada aquí
    'gestion_app',          ← Registrada aquí
]
```

### En `urls.py` (gestion_laserena):
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('delegaciones_app.urls')),    ← Rutas de delegaciones
    path('gestion/', include('gestion_app.urls')), ← Rutas de gestión
]
```

---

## 10. ¿CUÁNDO USA CADA APP?

**Usa DELEGACIONES_APP cuando:**
- Quieras ver solicitudes
- Necesites filtrar por delegación
- Quieras ver detalles de solicitudes

**Usa GESTION_APP cuando:**
- Quieras ver el progreso general
- Necesites analizar cumplimiento de metas
- Quieras un resumen ejecutivo

---

## 11. STATIC Y TEMPLATES

**Static** (`/static/`)
- `bootstrap/` → Framework CSS
- `images/` → Imágenes del proyecto

**Templates** (`/templates/`)
- `base.html` → Template base para todas las páginas
- `delegaciones_app/` → Templates específicas de delegaciones
- `gestion_app/` → Templates específicas de gestión

---

## ✅ RESUMEN EN UNA LÍNEA

**Gestión La Serena es un sistema Django que gestiona solicitudes de delegaciones (delegaciones_app) y monitorea el cumplimiento de metas (gestion_app) mediante un dashboard visual.**