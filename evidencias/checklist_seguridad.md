# Checklist de verificación de seguridad - Family Health MF

> Cierre técnico de la versión final · punto 11
>
> Verificación **no destructiva**: únicamente lecturas y peticiones HTTP seguras.
> No se modificaron ni eliminaron datos en producción.

## 1. Alcance y método

Se combinaron tres fuentes de evidencia:

1. **Revisión estática** de la configuración real: `backend/config/settings.py`,
   `railway.json`, `Dockerfile`, `.env.example`, `.gitignore`.
2. **Revisión estática del control de acceso**: `backend/apps/authentication/permissions.py`
   y los `permission_classes` declarados en cada `views.py`.
3. **Verificación dinámica HTTP** contra la versión desplegada, ejecutada por el script
   reproducible [verificacion_seguridad.py](../tests/verificacion_seguridad.py),
   cuya salida bruta quedó en `evidencias/_seguridad_raw.txt` y su resumen en
   `evidencias/verificacion_seguridad.json`.

Fecha de la verificación dinámica: **2026-10-20 (UTC)** · URL: `https://familyhealthmf-production.up.railway.app`

## 2. Resultados de la verificación dinámica (12 controles)

| ID | Control verificado | Esperado | Real | Resultado |
|---|---|---|---|---|
| SEC-01 | Servicio disponible (health check público) | HTTP 200 | HTTP 200 | CUMPLE |
| SEC-02 | HSTS presente en producción | `max-age` declarado | `max-age=31536000; includeSubDomains; preload` | CUMPLE |
| SEC-03 | `X-Content-Type-Options` | `nosniff` | `nosniff` | CUMPLE |
| SEC-04 | `X-Frame-Options` (clickjacking) | `DENY` o `SAMEORIGIN` | `DENY` | CUMPLE |
| SEC-05 | `Referrer-Policy` | `strict-origin-when-cross-origin` | `strict-origin-when-cross-origin` | CUMPLE |
| SEC-06 | Cabecera `Server` sin versiones sensibles | sin número de versión | `railway-hikari` | CUMPLE |
| SEC-07 | Errores sin trazas ni configuración | sin `Traceback` | HTTP 404, sin fugas | CUMPLE |
| SEC-08 | Recurso protegido sin token | HTTP 401 | HTTP 401 | CUMPLE |
| SEC-09 | Panel administrativo sin token | HTTP 401 | HTTP 401 | CUMPLE |
| SEC-10 | Solicitud con `Host` no autorizado | HTTP 400 | HTTP 404 (borde de Railway) + HTTP 400 (Django) | CUMPLE |
| SEC-11 | Mensaje de login uniforme (no revela si el usuario existe) | mismo mensaje | HTTP 401 vs 401, mensajes idénticos | CUMPLE |
| SEC-12 | Registro exige aceptar la política de privacidad | HTTP 400 | HTTP 400 | CUMPLE |

**Resumen dinámico: 12 de 12 controles cumplen.**

### Cierre de SEC-10 (doble evidencia)

SEC-10 no se resolvió con una sola petición externa, porque el **borde (proxy) de
Railway** enruta por la cabecera `Host`: si el `Host` es desconocido, el borde
responde **HTTP 404 "Application not found"** y la petición nunca alcanza a Django.
Además, con `USE_X_FORWARDED_HOST=True`, el borde **reescribe** `X-Forwarded-Host`,
por lo que tampoco puede persistirse un host falso por esa vía. El control se cerró
combinando **dos evidencias** (script reproducible
[verificacion_hosts.py](../tests/verificacion_hosts.py); resultados en
`evidencias/verificacion_hosts.md` y `evidencias/verificacion_hosts.json`):

1. **Externa (borde):** un `Host` desconocido no es enrutado (HTTP 404); y las
   inyecciones por `X-Forwarded-Host` (E2–E4) devuelven la MISMA respuesta que el
   caso de control con host válido (HTTP 200), es decir, son neutralizadas.
2. **Local (aplicación):** con la `ALLOWED_HOSTS` de producción, la aplicación
   **rechaza** un host no autorizado (`DisallowedHost` → **HTTP 400**) y **acepta**
   el host válido.

**Veredicto SEC-10: CUMPLE.** El host no autorizado queda bloqueado por dos capas
(borde + aplicación). El procedimiento y su reversión segura se detallan en la
sección 5.

## 3. Revisión estática de la configuración

| Control | Estado | Evidencia (archivo) | Detalle |
|---|---|---|---|
| `DEBUG=False` en producción | CUMPLE | `railway.json` (línea 26) y `backend/config/settings.py` | La variable `DJANGO_DEBUG` se fija en `False` para el despliegue. |
| `SECRET_KEY` fuera del repositorio | CUMPLE | `backend/config/settings.py` y `.gitignore` | Si `DEBUG=False` y no existe `DJANGO_SECRET_KEY`, la aplicación aborta con `RuntimeError`. El archivo `.env` está ignorado por Git. |
| Contraseñas hasheadas | CUMPLE | `settings.py` (`PASSWORD_HASHERS`) | Argon2 primero, con PBKDF2/BCrypt como alternativas. |
| JWT con algoritmo fuerte | CUMPLE | `settings.py` (`SIMPLE_JWT`) | `ALGORITHM = HS512`, `ISSUER = club-family-health`, `AUDIENCE = family-health-mf`, `LEEWAY = 10s`. |
| Rotación y blacklist de refresh token | CUMPLE | `settings.py` (`SIMPLE_JWT`) | `ROTATE_REFRESH_TOKENS = True` y `BLACKLIST_AFTER_ROTATION = True` con `rest_framework_simplejwt.token_blacklist` instalado. |
| Usuario inactivo no puede autenticarse | CUMPLE | `apps/authentication/serializers.py` | El login devuelve HTTP 400 con mensaje explícito cuando la cuenta está inactiva (verificado en `evidencias/validacion_railway.md`, caso RW04). |
| Limitación de tasa (throttling) | CUMPLE | `settings.py` (`DEFAULT_THROTTLE_RATES`) | `anon: 100/hour`, `user: 1000/hour`, `login: 10/minute`, `register: 5/hour`. |
| Bloqueo por intentos fallidos (Axes) | CUMPLE | `settings.py` (`AXES_*`) | `AXES_FAILURE_LIMIT=5`, `AXES_COOLOFF_TIME=15 min`, bloqueo por `username`, `ip_address` y `user_agent`. |
| Permisos por rol (RBAC) | CUMPLE | `apps/authentication/permissions.py` | Permisos explícitos `IsAdmin`, `IsReception`, `IsCafeteria`, `IsClient`, `IsAdminOrReception`, `IsAdminOrCafeteria`, `IsStaffOrReadOnly`, `IsAdminOrOwner`. |
| Redirección forzada a HTTPS | CUMPLE | `settings.py` | `SECURE_SSL_REDIRECT = True` cuando `DEBUG=False`. |
| Proxy TLS reconocido | CUMPLE | `settings.py` | `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` y `USE_X_FORWARDED_HOST = True`. |
| HSTS | CUMPLE | `settings.py` | `SECURE_HSTS_SECONDS = 31536000`, `INCLUDE_SUBDOMAINS` y `PRELOAD` activos. |
| Cookies seguras | CUMPLE | `settings.py` | `SESSION_COOKIE_SECURE` y `CSRF_COOKIE_SECURE` en `True` cuando `DEBUG=False`; `HTTPONLY=True`; `SAMESITE=Lax`. |
| Validación de contraseñas | CUMPLE | `settings.py` (`AUTH_PASSWORD_VALIDATORS`) | Longitud mínima 8, similitud con atributos del usuario, contraseñas comunes y numéricas. |
| CORS restringido en producción | CUMPLE | `settings.py` | `CORS_ALLOW_ALL_ORIGINS` sólo se activa con `DEBUG=True`; en producción se respetan `CORS_ALLOWED_ORIGINS`. |
| CSRF restringido | CUMPLE | `settings.py` | `CSRF_TRUSTED_ORIGINS` sólo contiene los orígenes declarados más el dominio de Railway. |
| Ausencia de secretos en el repositorio | CUMPLE | Búsqueda sobre el código | No se encontraron claves, tokens ni contraseñas embebidas en el código versionado. |
| Ausencia de secretos en el frontend | CUMPLE | `frontend/src/**` | El cliente consume la API por `VITE_API_URL`/ruta relativa; no contiene claves privadas. |

## 4. Hallazgos y acciones

| # | Hallazgo | Riesgo | Acción aplicada |
|---|---|---|---|
| H-01 | `DJANGO_ALLOWED_HOSTS` configurado como `*` en `railway.json`. | Medio (defensa en profundidad frente a *Host Header Injection*). | Se restringió al dominio efectivo más los comodines de Railway (sección 5). |
| H-02 | La comprobación SEC-10 quedó inconclusa porque el borde de Railway no enrutó la petición. | Bajo (el borde ya bloquea hosts desconocidos). | **Cerrado:** se repitió la comprobación con doble evidencia (borde + aplicación). Ver `evidencias/verificacion_hosts.md`. |
| H-03 | La auditoría (`AuditLog`) se registra internamente pero la API no expone un endpoint de lectura. | Informativo (trazabilidad). | Se documenta como limitación en el informe final; no se modifica la versión congelada. |

No se identificaron vulnerabilidades críticas ni se requirieron pruebas destructivas.

## 5. Restricción de `ALLOWED_HOSTS` aplicada

En `railway.json` se reemplazó el comodín por el dominio efectivo:

```json
"DJANGO_ALLOWED_HOSTS": "familyhealthmf-production.up.railway.app,.up.railway.app,.railway.app"
```

La restricción es segura porque `backend/config/settings.py` ya garantiza, además, la
inclusión del dominio público de Railway detectado en tiempo de ejecución y de los
comodines `.railway.app` y `.up.railway.app`. No se rompe el despliegue y se elimina
la aceptación indiscriminada de cualquier `Host`.

> **Estado de verificación: completada.** El health check responde HTTP 200 y el caso
> SEC-10 quedó cerrado con doble evidencia: el borde devuelve HTTP 404 para un `Host`
> desconocido y la aplicación rechaza un host no autorizado con HTTP 400 (ver
> `evidencias/verificacion_hosts.md`).
>
> **Reversión segura (si el despliegue fallara):** volver a establecer
> `DJANGO_ALLOWED_HOSTS` con el valor anterior en las variables del servicio en Railway.

## 6. Comandos de reproducción

```powershell
cd c:\Family_Health_MF
.venv\Scripts\python.exe tests\verificacion_seguridad.py
.venv\Scripts\python.exe tests\verificacion_hosts.py
```

Genera `evidencias/verificacion_seguridad.json` y `evidencias/_seguridad_raw.txt`.
El script `verificacion_hosts.py` cierra SEC-10 y genera
`evidencias/verificacion_hosts.json` y `evidencias/verificacion_hosts.md`.
