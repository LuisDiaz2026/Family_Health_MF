# Punto 12 — Base de Datos y Respaldo (evidencia real)

**Proyecto:** Family Health MF — Club Family Health (Maicao, La Guajira)
**Autor del trabajo de grado:** Luis Fermín Díaz Choles
**Entorno de la evidencia:** exclusivamente LOCAL / NO PRODUCTIVO
**Fecha y hora de la ejecución:** 2026-10-19 23:11–23:12 (America/Bogota, UTC-05:00)
**Salida bruta real de los comandos:** `evidencias/respaldo/prueba_respaldo_raw.txt`

> Nota: en ningún momento se accedió, modificó ni sobrescribió la base de datos de
> producción (PostgreSQL en Railway). Todo el ejercicio se realizó sobre copias
> locales del archivo SQLite de desarrollo.

---

## 1. Motor y ruta de la base de datos local (valor real obtenido)

Comando ejecutado (salida literal capturada en la evidencia bruta):

```
ENGINE= django.db.backends.sqlite3
NAME= C:\Family_Health_MF\backend\db.sqlite3
```

| Parámetro | Valor real |
|---|---|
| Motor (ENGINE) | `django.db.backends.sqlite3` (SQLite 3) |
| Nombre/ruta (NAME) | `C:\Family_Health_MF\backend\db.sqlite3` |
| Tamaño del archivo | 966.656 bytes (~944 KB) |
| Origen de la configuración | `backend/config/settings.py` → `DATABASES['default']`, resuelto en `DEBUG=True` a partir de `DB_ENGINE=sqlite3` y `DB_NAME=db.sqlite3` del archivo `.env` |

En desarrollo local el archivo `.env` define `DB_ENGINE=django.db.backends.sqlite3`
y **no** define `DATABASE_URL`; por eso Django resuelve la ruta relativa `db.sqlite3`
sobre `BASE_DIR` (`backend/`).

---

## 2. Motor de la base de datos de producción (Railway) y aclaración de acceso

- **Producción:** PostgreSQL (versión 16) en Railway, accedido mediante la variable
  de entorno `DATABASE_URL` que provee el plugin de PostgreSQL de Railway.
- Django selecciona el motor dinámicamente en `settings.py`: si `DATABASE_URL`
  empieza por `postgres*` y se está en producción (`DEBUG=False`), usa
  `dj_database_url.parse(...)` con el backend `django.db.backends.postgresql`
  (driver `psycopg2-binary`, declarado en `backend/requirements.txt`).
- **Aclaración importante:** la base PostgreSQL de producción **NO es accesible
  directamente desde este equipo local**. `DATABASE_URL` es un secreto que vive en
  el panel de Railway y no está versionado ni presente en el `.env` local
  (verificado: `DATABASE_URL` no está definida en `c:\Family_Health_MF\.env`).
  Por eso **no se ejecutó ningún `pg_dump`/`pg_restore` contra producción**.
- La base de datos de pruebas de la suite (`tests/run_suite.py`) es **SQLite en
  memoria** y no participa en esta evidencia.

Resumen de entornos:

| Entorno | Motor | Ubicación | Accesible desde local |
|---|---|---|---|
| Desarrollo (esta evidencia) | SQLite 3 | `backend\db.sqlite3` | Sí |
| Pruebas (suite) | SQLite en memoria | — | Sí (efímera) |
| Producción | PostgreSQL 16 | Railway (`DATABASE_URL`) | **No** (secreto en Railway) |

---

## 3. Conteo real de registros de la base local

Consultado con el intérprete del proyecto (`c:\Family_Health_MF\.venv\Scripts\python.exe`):

| Modelo | App | Registros |
|---|---|---:|
| Usuarios (`User`) | `apps.authentication` | 6 |
| Espacios (`Space`) | `apps.reservations` | 10 |
| Reservas (`Reservation`) | `apps.reservations` | 0 |
| Productos (`Product`) | `apps.refreshments` | 72 |

Estos valores constituyen la línea base contra la que se valida la restauración
(sección 5). El valor `reservas = 0` es el estado real actual de la base local.

---

## 4. Procedimiento de respaldo y restauración para SQLite

### 4.1 Respaldo (copia consistente del archivo)

SQLite almacena toda la base de datos en un único archivo, por lo que el respaldo
consiste en copiar el archivo de forma íntegra.

```powershell
# Respaldo de la base local de desarrollo
Copy-Item -Path "c:\Family_Health_MF\backend\db.sqlite3" `
          -Destination "c:\Family_Health_MF\evidencias\respaldo\respaldo_local_20261019.sqlite3" -Force
```

Alternativa con la utilidad oficial (si `sqlite3` está en el PATH):

```powershell
sqlite3 "c:\Family_Health_MF\backend\db.sqlite3" ".backup 'c:\Family_Health_MF\evidencias\respaldo\respaldo_local_20261019.sqlite3'"
```

### 4.2 Restauración (en mantenimiento, NUNCA sobre un archivo en uso)

```powershell
# 1) Detener el servidor de desarrollo para que el archivo no esté en uso.
# 2) Restaurar copiando el respaldo sobre la base destino:
Copy-Item -Path "c:\Family_Health_MF\evidencias\respaldo\respaldo_local_20261019.sqlite3" `
          -Destination "c:\Family_Health_MF\backend\db.sqlite3" -Force
```

Alternativa con la utilidad oficial:

```powershell
sqlite3 "c:\Family_Health_MF\backend\db.sqlite3" ".restore 'c:\Family_Health_MF\evidencias\respaldo\respaldo_local_20261019.sqlite3'"
```

> **En esta evidencia la restauración se validó SIN tocar `backend\db.sqlite3`**:
> el respaldo se copió a un archivo independiente (`restauracion_prueba.sqlite3`)
> y se apuntó Django a ese archivo mediante un script temporal que modifica
> `settings.DATABASES['default']['NAME']` antes de `django.setup()`
> (`evidencias/respaldo/_verificar_restauracion.py`). Así se demuestra que el
> respaldo **contiene los mismos datos** sin riesgo sobre el archivo original.

---

## 5. Resultado REAL de la prueba de restauración

### 5.1 Integridad (hashes SHA-256)

Los tres archivos fueron idénticos byte a byte:

| Archivo | SHA-256 |
|---|---|
| `backend\db.sqlite3` (original) | `04797918D97F7F6A60EA919287A25C496CB0C1CECCED6329EAA2AFE6CBFB7807` |
| `evidencias\respaldo\respaldo_local_20261019.sqlite3` (respaldo) | `04797918D97F7F6A60EA919287A25C496CB0C1CECCED6329EAA2AFE6CBFB7807` |
| `evidencias\respaldo\restauracion_prueba.sqlite3` (restaurado) | `04797918D97F7F6A60EA919287A25C496CB0C1CECCED6329EAA2AFE6CBFB7807` |

Además, los tres archivos tienen el mismo tamaño: 966.656 bytes.

### 5.2 Comparación de conteos

| Métrica | Base original (paso 2) | Base restaurada (paso 3d) | ¿Coinciden? |
|---|---:|---:|:---:|
| Usuarios | 6 | 6 | **SÍ** |
| Espacios | 10 | 10 | **SÍ** |
| Reservas | 0 | 0 | **SÍ** |
| Productos | 72 | 72 | **SÍ** |

Fecha y hora de la verificación: **2026-10-19 23:12:20 (UTC-05:00)**.

**Conclusión: la restauración es correcta. Los conteos del archivo restaurado
coinciden exactamente con los de la base original (SÍ) y los hashes SHA-256 son
idénticos, lo que demuestra integridad total del respaldo.**

### 5.3 Incidencia real encontrada y corregida (documentada)

El primer intento de verificación falló de forma real:

```
ModuleNotFoundError: No module named 'config'
EXITCODE_VERIF=1
```

**Causa:** al ejecutar el script, Python coloca como `sys.path[0]` la carpeta del
propio script (`evidencias\respaldo`) y **no** el directorio de trabajo, por lo que
no podía importar el paquete `config` del backend.

**Solución aplicada:** el script agrega explícitamente el directorio
`backend` a `sys.path` antes de `django.setup()`. Tras la corrección, la
verificación terminó con `EXITCODE_VERIF2=0` y con los conteos coincidentes.
Ambos intentos (el fallido y el exitoso) quedaron registrados en la evidencia bruta.

---

## 6. Procedimiento de respaldo y restauración para PostgreSQL en Railway (producción)

> Estos pasos se documentan a título de procedimiento recomendado. **No se
> ejecutaron en esta evidencia** porque la base de producción no es accesible
> directamente desde el equipo local y no se debe operar sobre producción sin
> autorización.

### 6.1 Respaldo (backup)

**Opción A — Panel de Railway (recomendada para el equipo del proyecto):**
1. Ingresar al proyecto en el panel de Railway → servicio **PostgreSQL**.
2. Abrir la pestaña de **Backups** y generar/descargar un respaldo, o usar la
   consola/`Connect` del servicio.
3. Guardar el respaldo en un medio externo cifrado (nunca en el repositorio).

**Opción B — `pg_dump` desde un equipo autorizado con acceso a la red/credenciales
(tomando `DATABASE_URL` del panel, nunca hardcodeada):**

```bash
# El valor de DATABASE_URL se toma del panel de Railway (variable secreta).
pg_dump "$DATABASE_URL" --no-owner --no-privileges --format=custom \
        --file="respaldo_prod_$(date +%Y%m%d).dump"
```

### 6.2 Restauración (solo en un entorno de prueba o con autorización explícita)

```bash
# Restaurar en una base DESTINO de prueba (NUNCA directo sobre producción sin autorización):
pg_restore --no-owner --no-privileges --dbname="$DATABASE_URL_PRUEBA" \
           "respaldo_prod_20261019.dump"
```

### 6.3 Reglas de seguridad obligatorias

- **NUNCA** restaurar sobre la base de producción sin autorización explícita del
  responsable del despliegue y sin haber hecho antes un respaldo del estado actual.
- **NUNCA** versionar `DATABASE_URL` ni las credenciales; viven solo en el panel de Railway.
- Probar siempre primero la restauración en un entorno aislado o duplicado.
- Cumplimiento Ley 1581/2012: los respaldos contienen datos personales y deben
  almacenarse cifrados y con control de acceso.

---

## 7. Limitaciones (qué NO se pudo probar y por qué)

1. **Restauración de PostgreSQL en producción:** no se ejecutó `pg_dump`/`pg_restore`
   contra Railway porque la base de producción **no es accesible directamente desde
   el equipo local** (no se dispone de las credenciales/red) y por la regla de **no
   tocar producción**. Solo se documentó el procedimiento.
2. **Acceso directo a la base de datos de producción:** verificado que
   `DATABASE_URL` no está en el `.env` local; se gestiona exclusivamente como secreto
   en el panel de Railway.
3. **Suite de pruebas:** usa SQLite **en memoria**, por lo que la restauración de
   archivo aquí descrita no aplica a ese entorno efímero.
4. **Reservas con valor 0:** la tabla de reservas está vacía en la base local
   (estado real), por lo que la verificación de esa tabla se hizo sobre 0 registros;
   aun así la comprobación 0 = 0 es válida.
5. **Sin prueba de restauración destructiva sobre el original:** por diseño y
   seguridad, `backend\db.sqlite3` **no fue modificado**; la restauración se validó
   sobre una copia independiente.

---

## 8. Archivos generados por esta evidencia

En `c:\Family_Health_MF\evidencias\respaldo\`:

| Archivo | Descripción |
|---|---|
| `respaldo_local_20261019.sqlite3` | Respaldo real de `backend\db.sqlite3` (966.656 bytes). |
| `restauracion_prueba.sqlite3` | Copia del respaldo usada para simular la restauración sin tocar el original. |
| `_verificar_restauracion.py` | Script temporal que apunta Django al archivo restaurado y compara conteos. |
| `prueba_respaldo_raw.txt` | Salida bruta real de todos los comandos. |

> **Nota:** no se eliminaron los archivos de respaldo ni el script de verificación,
> porque su presencia constituye la evidencia y permite reproducir el ejercicio.
> Todos están dentro de `evidencias\`, que no es producción.

---

## 9. Comandos exactos de reproducción (PowerShell)

Entorno previo (Git/Node no están en el PATH):

```powershell
$env:Path = "C:\Program Files\Git\cmd;C:\Program Files\nodejs;" + $env:Path
$raw = "c:\Family_Health_MF\evidencias\respaldo\prueba_respaldo_raw.txt"
New-Item -ItemType Directory -Force -Path "c:\Family_Health_MF\evidencias\respaldo" | Out-Null
cd c:\Family_Health_MF\backend
```

**Paso 1 — Motor y ruta de la base local:**

```powershell
& "c:\Family_Health_MF\.venv\Scripts\python.exe" -c "import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings');django.setup();from django.conf import settings;print('ENGINE=',settings.DATABASES['default']['ENGINE']);print('NAME=',settings.DATABASES['default']['NAME'])" *>> $raw
```

**Paso 2 — Conteo de registros:**

```powershell
& "c:\Family_Health_MF\.venv\Scripts\python.exe" -c "import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings');django.setup();from apps.authentication.models import User;from apps.reservations.models import Reservation,Space;from apps.refreshments.models import Product;print('usuarios=',User.objects.count());print('espacios=',Space.objects.count());print('reservas=',Reservation.objects.count());print('productos=',Product.objects.count())" *>> $raw
```

**Paso 3 — Respaldo, copia de restauración y hashes:**

```powershell
$db      = "c:\Family_Health_MF\backend\db.sqlite3"
$backup  = "c:\Family_Health_MF\evidencias\respaldo\respaldo_local_20261019.sqlite3"
$restore = "c:\Family_Health_MF\evidencias\respaldo\restauracion_prueba.sqlite3"
Copy-Item -Path $db       -Destination $backup  -Force
Copy-Item -Path $backup   -Destination $restore -Force
Get-FileHash -Algorithm SHA256 -Path $db,$backup,$restore | Format-List | Out-File -FilePath $raw -Append -Encoding utf8
```

**Paso 3d — Verificación de conteos sobre el archivo restaurado (sin tocar el original):**

```powershell
cd c:\Family_Health_MF\backend
& "c:\Family_Health_MF\.venv\Scripts\python.exe" "c:\Family_Health_MF\evidencias\respaldo\_verificar_restauracion.py" $restore *>> $raw
```

Salida esperada (real obtenida):

```
ARCHIVO_VERIFICADO= c:\Family_Health_MF\evidencias\respaldo\restauracion_prueba.sqlite3
RESTAURADO usuarios= 6
RESTAURADO espacios= 10
RESTAURADO reservas= 0
RESTAURADO productos= 72
```
