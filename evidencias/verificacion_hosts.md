# Verificacion del control ALLOWED_HOSTS (cierre SEC-10)

> Family Health MF - cierre tecnico de la version final (bloque 3)

- **URL evaluada:** https://familyhealthmf-production.up.railway.app
- **Fecha/hora (UTC):** 2026-11-19T14:16:18+00:00
- **`ALLOWED_HOSTS` de produccion:** `familyhealthmf-production.up.railway.app,.up.railway.app,.railway.app`
- **Veredicto:** **CUMPLE**

## Por que SEC-10 no se resuelve solo con una peticion externa

El borde (proxy) de Railway enruta por la cabecera `Host`: si el `Host` es
desconocido, el borde responde **404 "Application not found"** y la peticion
nunca alcanza a Django. Ademas, con `USE_X_FORWARDED_HOST=True`, el borde
reescribe `X-Forwarded-Host`, por lo que tampoco se puede persistir un host
falso por esa via. Por eso la comprobacion se completa con dos evidencias.

## Evidencia 1 - Externa (comportamiento del borde)

| ID | Caso | Cabeceras enviadas | HTTP | Interpretacion |
|---|---|---|---|---|
| E1 | Host no autorizado (test actual SEC-10) | `Host: host-no-autorizado.test` | 404 | bloqueado por el borde (no enrutado) |
| E2 | X-Forwarded-Host no autorizado | `X-Forwarded-Host: host-no-autorizado.test` | 200 | inyeccion neutralizada (respuesta identica al control) |
| E3 | X-Forwarded-Host con puerto | `X-Forwarded-Host: malo.test:8080` | 200 | inyeccion neutralizada (respuesta identica al control) |
| E4 | X-Forwarded-Host encadenado | `X-Forwarded-Host: familyhealthmf-production.up.railway.app, host-no-autorizado.test` | 200 | inyeccion neutralizada (respuesta identica al control) |
| E5 | Host valido (control positivo) | `Host: familyhealthmf-production.up.railway.app` | 200 | control: respuesta normal |

## Evidencia 2 - Local (aplicacion Django con la configuracion de produccion)

- **`ALLOWED_HOSTS` efectivo:** `['familyhealthmf-production.up.railway.app', '.up.railway.app', '.railway.app']`
- **Host no autorizado (`host-no-autorizado.test`) rechazado:** True
- **Host autorizado (`familyhealthmf-production.up.railway.app`) aceptado:** True

Cuando el `Host` no esta en `ALLOWED_HOSTS`, Django lanza `DisallowedHost`
y responde **HTTP 400**; si el host esta autorizado, la peticion se atiende.

## Lectura conjunta de las dos evidencias

- **E1:** un `Host` desconocido no es enrutado por el borde (no llega a la
  aplicacion), por lo que no puede procesarse una peticion con host falso.
- **E2-E4:** la inyeccion por `X-Forwarded-Host` devuelve la MISMA respuesta
  que el caso de control con host valido, es decir, la cabecera inyectada
  no tiene efecto (el borde la reescribe).
- **Evidencia local:** con la `ALLOWED_HOSTS` de produccion, Django
  RECHAZARIA ese host no autorizado (`DisallowedHost` -> HTTP 400). Por
  tanto, el HTTP 200 de E2-E4 solo es posible si Django recibio un host
  valido (la inyeccion fue neutralizada por el borde).

## Conclusion

El control SEC-10 **SE CUMPLE**
con dos capas de defensa:

1. **Borde (Railway):** una peticion con `Host` desconocido no es enrutada
   hacia la aplicacion; y `X-Forwarded-Host` es reescrito (no persistible).
2. **Aplicacion (Django):** con la `ALLOWED_HOSTS` de produccion, un host no
   autorizado es rechazado con `HTTP 400 (DisallowedHost)`.

## Reproduccion

```powershell
cd c:\Family_Health_MF
.venv\Scripts\python.exe tests\verificacion_hosts.py
```
