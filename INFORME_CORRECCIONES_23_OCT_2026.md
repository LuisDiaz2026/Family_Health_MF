# Correcciones localizadas sobre el commit base d46cd89

- `frontend/src/views/staff/ReservationsView.vue`: sustituido `confirm/` inexistente por `approve/`; la acción de completar usa el nuevo endpoint `complete/`; retirado el fallback PATCH que notificaba éxito aun cuando los campos `status` o `payment_status` eran de solo lectura.
- `backend/apps/reservations/views.py`: agregado `POST /api/v1/reservations/reservations/{id}/complete/` para personal autorizado; solo completa reservas confirmadas y registra `completed_at`.
- `backend/bootstrap_data.py`: sin contraseñas predeterminadas; exige `DEMO_PASS_*` cuando se habilita la siembra, que ahora es opt-in.
- `railway.json`: `RAILWAY_SEED_BOOTSTRAP=0` para evitar reinicializaciones de cuentas en despliegues normales.
- `docs/` y `EVIDENCIA_VERSION_FINAL.md`/`README.md`: aclaraciones de versión y correcciones académicas.

**Estado de validación (actualizado el 2026-10-24)**

- Las correcciones se **registraron en `main`** mediante el commit `0e46926` y se **publicaron** en GitHub (`58ebe58..0e46926`).
- El **despliegue en Railway quedó verificado** con dos comprobaciones que distinguen la revisión corregida: `POST /api/v1/reservations/reservations/{id}/complete/` responde **HTTP 401** (antes 404) y el chunk del personal servido contiene `/approve/` y `/complete/`, no `/confirm/`.
- Se repitió la **regresión local**: 44/44 pruebas aprobadas (32 unitarias + 12 integración) y `manage.py check` sin incidencias.
- **Pendiente:** la comprobación en navegador de confirmar, completar, cancelar y registrar pago sobre una reserva real, a cargo del responsable, y la rotación o desactivación de las cuentas de demostración preexistentes (siguen activas con sus contraseñas anteriores, porque el director las requiere para la revisión).
- La historia anterior permanece identificada por SHA; el ZIP corregido no era un `git archive` idéntico al commit base y queda sustituido por el árbol del commit `0e46926`.
