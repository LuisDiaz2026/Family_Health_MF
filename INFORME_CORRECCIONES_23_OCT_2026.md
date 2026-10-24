# Correcciones localizadas sobre el commit base d46cd89

- `frontend/src/views/staff/ReservationsView.vue`: sustituido `confirm/` inexistente por `approve/`; la acción de completar usa el nuevo endpoint `complete/`; retirado el fallback PATCH que notificaba éxito aun cuando los campos `status` o `payment_status` eran de solo lectura.
- `backend/apps/reservations/views.py`: agregado `POST /api/v1/reservations/reservations/{id}/complete/` para personal autorizado; solo completa reservas confirmadas y registra `completed_at`.
- `backend/bootstrap_data.py`: sin contraseñas predeterminadas; exige `DEMO_PASS_*` cuando se habilita la siembra, que ahora es opt-in.
- `railway.json`: `RAILWAY_SEED_BOOTSTRAP=0` para evitar reinicializaciones de cuentas en despliegues normales.
- `docs/` y `EVIDENCIA_VERSION_FINAL.md`/`README.md`: aclaraciones de versión y correcciones académicas.

**Estado de validación**: revisión estática y compilación sintáctica local; no se ha realizado una nueva ejecución integral de pruebas en Railway sobre estos cambios. Se requiere registrar un commit, desplegar, rotar o desactivar cualquier cuenta de demostración preexistente, validar el flujo administrativo real en navegador y repetir las suites. La historia anterior permanece identificada por SHA; este ZIP no es un `git archive` idéntico al commit base.
