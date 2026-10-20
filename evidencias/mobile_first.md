# Pruebas Mobile-First - version final

> Family Health MF · cierre tecnico · punto 8

- **URL evaluada:** https://familyhealthmf-production.up.railway.app
- **Resoluciones:** 360, 390, 768 y 1280 px
- **Combinaciones ejecutadas (resolucion x pantalla):** 36
- **Con desbordamiento horizontal injustificado:** 0

La medicion se realizo con Playwright controlando Microsoft Edge sobre la
version desplegada. `overflow_horizontal_px` es la diferencia real entre
`scrollWidth` del documento y el ancho del viewport; se considera correcto
un valor <= 2 px.

| Resolucion | Perfil | Pantalla | Overflow (px) | Botones | Alto minimo boton (px) | Campos | Tablas | Modales | Resultado | Captura |
|---|---|---|---|---|---|---|---|---|---|---|
| 360x800 | publico | acceso-login | 0 | 3 | 20 | 3 | 0 | 0 | **PASS** | `mobile/publico_acceso-login_360x800.png` |
| 360x800 | cliente | dashboard-cliente | 0 | 15 | 16 | 0 | 0 | 0 | **PASS** | `mobile/cliente_dashboard-cliente_360x800.png` |
| 360x800 | cliente | listado-reservas-cliente | 0 | 14 | 30 | 0 | 0 | 0 | **PASS** | `mobile/cliente_listado-reservas-cliente_360x800.png` |
| 360x800 | cliente | formulario-reserva | 0 | 18 | 20 | 0 | 0 | 0 | **PASS** | `mobile/cliente_formulario-reserva_360x800.png` |
| 360x800 | cliente | catalogo-refrescos | 0 | 73 | 28 | 1 | 0 | 0 | **PASS** | `mobile/cliente_catalogo-refrescos_360x800.png` |
| 360x800 | admin | dashboard-admin | 0 | 15 | 16 | 0 | 0 | 0 | **PASS** | `mobile/admin_dashboard-admin_360x800.png` |
| 360x800 | admin | listado-reservas-admin | 0 | 17 | 28 | 0 | 0 | 0 | **PASS** | `mobile/admin_listado-reservas-admin_360x800.png` |
| 360x800 | admin | productos | 0 | 226 | 26 | 2 | 0 | 0 | **PASS** | `mobile/admin_productos_360x800.png` |
| 360x800 | admin | espacios | 0 | 9 | 36 | 1 | 0 | 0 | **PASS** | `mobile/admin_espacios_360x800.png` |
| 390x844 | publico | acceso-login | 0 | 3 | 20 | 3 | 0 | 0 | **PASS** | `mobile/publico_acceso-login_390x844.png` |
| 390x844 | cliente | dashboard-cliente | 0 | 15 | 16 | 0 | 0 | 0 | **PASS** | `mobile/cliente_dashboard-cliente_390x844.png` |
| 390x844 | cliente | listado-reservas-cliente | 0 | 14 | 30 | 0 | 0 | 0 | **PASS** | `mobile/cliente_listado-reservas-cliente_390x844.png` |
| 390x844 | cliente | formulario-reserva | 0 | 18 | 20 | 0 | 0 | 0 | **PASS** | `mobile/cliente_formulario-reserva_390x844.png` |
| 390x844 | cliente | catalogo-refrescos | 0 | 73 | 28 | 1 | 0 | 0 | **PASS** | `mobile/cliente_catalogo-refrescos_390x844.png` |
| 390x844 | admin | dashboard-admin | 0 | 15 | 16 | 0 | 0 | 0 | **PASS** | `mobile/admin_dashboard-admin_390x844.png` |
| 390x844 | admin | listado-reservas-admin | 0 | 17 | 28 | 0 | 0 | 0 | **PASS** | `mobile/admin_listado-reservas-admin_390x844.png` |
| 390x844 | admin | productos | 0 | 226 | 26 | 2 | 0 | 0 | **PASS** | `mobile/admin_productos_390x844.png` |
| 390x844 | admin | espacios | 0 | 9 | 36 | 1 | 0 | 0 | **PASS** | `mobile/admin_espacios_390x844.png` |
| 768x1024 | publico | acceso-login | 0 | 3 | 20 | 3 | 0 | 0 | **PASS** | `mobile/publico_acceso-login_768x1024.png` |
| 768x1024 | cliente | dashboard-cliente | 0 | 15 | 15 | 0 | 0 | 0 | **PASS** | `mobile/cliente_dashboard-cliente_768x1024.png` |
| 768x1024 | cliente | listado-reservas-cliente | 0 | 14 | 30 | 0 | 0 | 0 | **PASS** | `mobile/cliente_listado-reservas-cliente_768x1024.png` |
| 768x1024 | cliente | formulario-reserva | 0 | 18 | 20 | 0 | 0 | 0 | **PASS** | `mobile/cliente_formulario-reserva_768x1024.png` |
| 768x1024 | cliente | catalogo-refrescos | 0 | 73 | 28 | 1 | 0 | 0 | **PASS** | `mobile/cliente_catalogo-refrescos_768x1024.png` |
| 768x1024 | admin | dashboard-admin | 0 | 15 | 16 | 0 | 0 | 0 | **PASS** | `mobile/admin_dashboard-admin_768x1024.png` |
| 768x1024 | admin | listado-reservas-admin | 0 | 17 | 28 | 0 | 0 | 0 | **PASS** | `mobile/admin_listado-reservas-admin_768x1024.png` |
| 768x1024 | admin | productos | 0 | 226 | 26 | 2 | 0 | 0 | **PASS** | `mobile/admin_productos_768x1024.png` |
| 768x1024 | admin | espacios | 0 | 9 | 36 | 1 | 0 | 0 | **PASS** | `mobile/admin_espacios_768x1024.png` |
| 1280x800 | publico | acceso-login | 0 | 3 | 20 | 3 | 0 | 0 | **PASS** | `mobile/publico_acceso-login_1280x800.png` |
| 1280x800 | cliente | dashboard-cliente | 0 | 15 | 16 | 0 | 0 | 0 | **PASS** | `mobile/cliente_dashboard-cliente_1280x800.png` |
| 1280x800 | cliente | listado-reservas-cliente | 0 | 14 | 30 | 0 | 0 | 0 | **PASS** | `mobile/cliente_listado-reservas-cliente_1280x800.png` |
| 1280x800 | cliente | formulario-reserva | 0 | 18 | 20 | 0 | 0 | 0 | **PASS** | `mobile/cliente_formulario-reserva_1280x800.png` |
| 1280x800 | cliente | catalogo-refrescos | 0 | 73 | 28 | 1 | 0 | 0 | **PASS** | `mobile/cliente_catalogo-refrescos_1280x800.png` |
| 1280x800 | admin | dashboard-admin | 0 | 15 | 16 | 0 | 0 | 0 | **PASS** | `mobile/admin_dashboard-admin_1280x800.png` |
| 1280x800 | admin | listado-reservas-admin | 0 | 17 | 28 | 0 | 0 | 0 | **PASS** | `mobile/admin_listado-reservas-admin_1280x800.png` |
| 1280x800 | admin | productos | 0 | 226 | 26 | 2 | 0 | 0 | **PASS** | `mobile/admin_productos_1280x800.png` |
| 1280x800 | admin | espacios | 0 | 9 | 36 | 1 | 0 | 0 | **PASS** | `mobile/admin_espacios_1280x800.png` |

## Comandos de reproduccion

```powershell
cd c:\Family_Health_MF\tests\e2e
node mobile_first.js
```
