# -*- coding: utf-8 -*-
"""
3 DOCUMENTOS WORD v3 (CORREGIDOS SEGÚN OBSERVACIONES PROFESOR):
- DOC1: REQUERIMIENTOS SIMPLIFICADO (solo IDs, descripciones, prioridad, CA. SIN repetición crono/normativa/costos)
  70 RF + 30 RNF = 100 ítems (8 RNF eliminados para unificación)
- DOC2: CONFIGURACIÓN / MANUAL TÉCNICO (ajustado términos, semestre 2026-2, advertencia credenciales + Mobile LAN)
- DOC3: MATRIZ VALIDACIÓN (34 Historias de Usuario reales + 100 RQ. 14 Smoke REALES EJECUTADOS 20/09/2026.
  Resto 31 UT+12 IT+30 AT = 73 pruebas marcadas COMO ⚠️ PLANIFICADO (Pendiente Acta PO Club Family Health).
  NO afirmar 100% antes de actas.)
"""
import os
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT_DIR = r"c:\Users\gusta\OneDrive - UNIR\TRABAJOS DE GRADO\TRABAJOS DE GRADO\UAN\LUIS\SCRUM_DOCS"

FOREST_GREEN = RGBColor(0x17,0x4C,0x3C)
WELLNESS     = RGBColor(0x3B,0x80,0x64)
GOLD         = RGBColor(0xD7,0xAE,0x58)
SAND         = GOLD
CORAL        = RGBColor(0xE9,0x78,0x4A)
GRAPH        = RGBColor(0x23,0x29,0x27)
WHITE        = RGBColor(0xFF,0xFF,0xFF)

def _hex(c): return f"{c[0]:02X}{c[1]:02X}{c[2]:02X}"
def _fill(cell, color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"),"clear"); shd.set(qn("w:color"),"auto"); shd.set(qn("w:fill"),_hex(color))
    tc_pr.append(shd)
def _borders(t):
    tbl = t._tbl; tblP = tbl.tblPr if tbl.tblPr is not None else OxmlElement("w:tblPr")
    b = OxmlElement("w:tblBorders")
    for name in ["top","left","bottom","right","insideH","insideV"]:
        el = OxmlElement(f"w:{name}"); el.set(qn("w:val"),"single"); el.set(qn("w:sz"),"6"); el.set(qn("w:space"),"0"); el.set(qn("w:color"),"808080")
        b.append(el)
    tblP.append(b)
def _style_doc(doc):
    for s in doc.sections: s.top_margin=s.bottom_margin=s.left_margin=s.right_margin=Cm(2.2)
    n = doc.styles["Normal"]; n.font.name="Calibri"; n.font.size=Pt(10.5); n.font.color.rgb=GRAPH
    for nm,sz,col in [("Heading 1",15,FOREST_GREEN),("Heading 2",12.5,WELLNESS),("Heading 3",11,GOLD)]:
        h = doc.styles[nm]; h.font.name="Calibri"; h.font.bold=True; h.font.size=Pt(sz); h.font.color.rgb=col
def _portada(doc, t_grande, t_sub, version, fecha, autor, proyecto, lugar):
    for _ in range(4): doc.add_paragraph()
    p = doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("CLUB FAMILY HEALTH MF"); r.font.size=Pt(20); r.font.bold=True; r.font.color.rgb=FOREST_GREEN
    p2 = doc.add_paragraph(); p2.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r = p2.add_run("Sistema Integral de Gestión y Reservas Mobile-First"); r.font.size=Pt(12); r.italic=True; r.font.color.rgb=WELLNESS
    for _ in range(3): doc.add_paragraph()
    pt = doc.add_paragraph(); pt.alignment=WD_ALIGN_PARAGRAPH.CENTER
    rr = pt.add_run(t_grande); rr.font.size=Pt(17); rr.font.bold=True; rr.font.color.rgb=GRAPH
    ps = doc.add_paragraph(); ps.alignment=WD_ALIGN_PARAGRAPH.CENTER
    rr = ps.add_run(t_sub); rr.font.size=Pt(12); rr.italic=True; rr.font.color.rgb=GOLD
    for _ in range(4): doc.add_paragraph()
    info = [("Proyecto:",proyecto),("Versión:",version),("Fecha:",fecha),("Autor:",autor),("Lugar:",lugar),("Metodología:","Scrum 4 Sprints · 12 Semanas Académicas"),("Periodo Académico:","2026-2 · Trabajo de Grado")]
    for k,v in info:
        pp = doc.add_paragraph(); pp.alignment=WD_ALIGN_PARAGRAPH.CENTER
        rk = pp.add_run(f"{k}  "); rk.bold=True; rk.font.size=Pt(10.5); rk.font.color.rgb=FOREST_GREEN
        rv = pp.add_run(v); rv.font.size=Pt(10.5); rv.font.color.rgb=GRAPH
    doc.add_page_break()
def _tabla(doc, headers, rows, hcolor=FOREST_GREEN, widths=None):
    t = doc.add_table(rows=1, cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER; _borders(t)
    for i,h in enumerate(headers):
        cell = t.rows[0].cells[i]; cell.text=""
        p = cell.paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        rr = p.add_run(h); rr.bold=True; rr.font.size=Pt(9.5); rr.font.color.rgb=WHITE
        _fill(cell, hcolor); cell.vertical_alignment=WD_ALIGN_VERTICAL.CENTER
    for row in rows:
        cells = t.add_row().cells
        for i,v in enumerate(row):
            cells[i].text = str(v)
            for pp in cells[i].paragraphs:
                for rr in pp.runs: rr.font.size=Pt(9)
            cells[i].vertical_alignment=WD_ALIGN_VERTICAL.CENTER
    if widths:
        for i,w in enumerate(widths):
            for row in t.rows: row.cells[i].width=Cm(w)
    doc.add_paragraph()
    return t
def h1(doc,t): doc.add_heading(t,1)
def h2(doc,t): doc.add_heading(t,2)
def h3(doc,t): doc.add_heading(t,3)
def par(doc,t,b=False,i=False,sz=10.5,align=None,color=None):
    p=doc.add_paragraph(); r=p.add_run(t); r.font.size=Pt(sz); r.bold=b; r.italic=i
    if color is not None: r.font.color.rgb=color
    if align is not None: p.alignment=align; return p
    return p
def bullet(doc,t): doc.add_paragraph(t,style="List Bullet")

# =========== DATOS COMPARTIDOS (versión CORREGIDA) ===========
ROLES_SCRUM = [
    ["Product Owner","Club Family Health","Definir visión; priorizar Product Backlog; aprobar actas validación; interlocutor con desarrollador. (Formalización acta pendiente firma)."],
    ["Scrum Master","Director del Trabajo de Grado (Ingeniería Sistemas y Computación UAN)","Facilitar Scrum; acompañar Planning, Daily, Review, Retrospective; eliminar impedimentos."],
    ["Developer","Luis Fermín Díaz Choles","Implementación; documentación técnica; pruebas unitarias/humo; entregables por iteración."],
]
STACK_TABLA4 = [
    ["Backend y lógica negocio","Python 3.10.11 + Django 5.0.7","Framework maduro; ORM; RBAC; Panel Admin automático (Sommerville 2021)."],
    ["Frontend Mobile-First","Tailwind CSS 3.4 + Vue 3.4 + Vite 5","SPA composable Vue; diseño mobile-first; Tailwind utility-first (Nielsen 1994)."],
    ["Base de datos","PostgreSQL 16 / psycopg2 (producción) · SQLite3 (desarrollo local)","Drivers soportados oficialmente Django. PostgreSQL garantiza transacciones ACID completas."],
    ["Control versiones","GitHub","Gestión código fuente; ramas Git Flow simplificada (main/develop/feature)."],
    ["Gestión Scrum","Trello / Jira","Tablero Kanban; seguimiento historias por sprint."],
    ["Seguridad Ley 1581","SimpleJWT HS512 · Argon2 · Axes · django-environ","Tokens; hashing; rate limit; secretos en variables entorno."],
]

# =========== MÓDULOS 6 RF 70 ===========
RF_DATA = {
"MÓDULO 1 - AUTENTICACIÓN Y USUARIOS (12 RF) · Sprint 3 (S5-S7)": [
    ["RF-AUTH-001","Registro CLIENTE 14 campos + consentimiento Ley 1581 doble checkbox","Alta","3.1 · Sprint 3"],
    ["RF-AUTH-002","Fecha y hora aceptación Política Privacidad + Términos en BD","Alta","3.1 · Sprint 3"],
    ["RF-AUTH-003","3 Roles RBAC: ADMINISTRADOR · EMPLEADO · CLIENTE","Alta","3.1"],
    ["RF-AUTH-004","Inicio sesión JWT HS512 Access 60min + Refresh 7 días","Alta","3.1"],
    ["RF-AUTH-005","Rotación Refresh + Blacklist token anterior (no reutilizable)","Alta","3.1"],
    ["RF-AUTH-006","Logout invalida Refresh Token en Blacklist","Alta","3.1"],
    ["RF-AUTH-007","Bloqueo 5 fallos login IP + UserAgent 15 min (django-axes)","Alta","Seguridad"],
    ["RF-AUTH-008","Throttling API login 10/min · registro 5/h · usuario 1000/h · anónimo 100/h","Alta","Seguridad"],
    ["RF-AUTH-009","Perfil personal editable: datos, membresía, emergencia, tarjeta fidelidad","Media","3.1"],
    ["RF-AUTH-010","Auditoría 7 acciones Ley 1581: LOGIN/FALLIDO/LOGOUT/VER/EDIT/EXPORTAR/BORRAR","Alta","Ley 1581"],
    ["RF-AUTH-011","Administrador crea cuentas EMPLEADO/ADMINISTRADOR","Media","3.1"],
    ["RF-AUTH-012","Admin activa/desactiva usuario (Desautorización Ley 1581/2012 Art.14)","Media","Ley 1581"],
],
"MÓDULO 2 - RESERVAS Y DISPONIBILIDAD (13 RF) · Sprint 3 (S5-S7)": [
    ["RF-RES-001","Catálogo 10 espacios: nombre, tipo, código, capacidad, tarifa COP, foto, estado","Alta","3.4.3 Sprint 3"],
    ["RF-RES-002","Configuración espacio: min/max minutos, días antelación, penalidad cancelación, aprobación empleado","Alta","3.1"],
    ["RF-RES-003","Horarios operativos 7 días + días festivos/cierre Holiday","Alta","3.1"],
    ["RF-RES-004","Wizard reserva 3 pasos: espacio → fecha → rango horario; monto COP calculado","Alta","Criterio 3.6 #3"],
    ["RF-RES-005","Consulta disponibilidad tiempo real","Alta","Criterio 3.6 #3"],
    ["RF-RES-006","Prevención solape: is_available_at() + transaction.atomic() (PostgreSQL recomienda Exclusion Constraint)","Alta","Criterio 3.6 #1"],
    ["RF-RES-007","Cálculo monto = (minutos/60) × tarifa_hora COP 2 decimales exacto","Alta","3.1"],
    ["RF-RES-008","6 estados reserva: PENDIENTE/CONFIRMADA/CANCELADA/COMPLETADA/RECHAZADA/NO_ASISTIÓ","Alta","3.1"],
    ["RF-RES-009","3 estados pago: PENDIENTE/PAGADO presencial/EXENTO","Alta","3.1"],
    ["RF-RES-010","Cancelación sin penalidad solo si antelación ≥ penalty_hours","Media","3.1"],
    ["RF-RES-011","Empleado aprueba/rechaza/marca pagada/cancela/no asistió + puntuación","Alta","3.4.3"],
    ["RF-RES-012","Mis reservas 4 tabs: próximas/activas ahora/históricas/canceladas","Media","3.4.3"],
    ["RF-RES-013","CRUD espacios/tipos/horarios/festivos administrador","Alta","3.1"],
],
"MÓDULO 3 - REFRESCOS, PEDIDOS, INVENTARIO (13 RF) · Sprint 4 (S8-S9)": [
    ["RF-REF-001","Catálogo SKU 23 productos: categoría, COP precio, costo, stock, stock mínimo, alérgenos, calorías, foto","Alta","3.4.4 Sprint 4"],
    ["RF-REF-002","5 Categorías ordenables: Bebidas Frías/Calientes, Snacks, Comidas Rápidas, Postres","Media","3.1"],
    ["RF-REF-003","Carrito persistente localStorage sin login previo","Alta","3.4.4"],
    ["RF-REF-004","Reducción atómica stock F() expressions (sin sobreventa)","Alta","3.1"],
    ["RF-REF-005","Descuento automático % nivel fidelidad aplicado al subtotal COP","Media","3.4.4"],
    ["RF-REF-006","4 Métodos pago presencial COLOMBIA: Efectivo · Tarjeta física · Transferencia NEQUI/DAVIPLATA · Descuento membresía","Alta","3.4.4"],
    ["RF-REF-007","Estados pedido: PEND → PREPARANDO → LISTO → ENTREGADO → PAGADO · o CANCELADO con motivo","Alta","3.4.4"],
    ["RF-REF-008","Numeración PED-AAAAMMDD-NNNNN conciliación","Media","3.1"],
    ["RF-REF-009","Precio congelado unit_price_at_purchase; detalle por pedido","Alta","3.1"],
    ["RF-REF-010","Panel: stock ≤ min_stock badge rojo alerta reabastecimiento","Media","3.1"],
    ["RF-REF-011","Barra/recepción avanza estado, registra pago monto COP y método, cancela con comentario","Alta","3.4.4"],
    ["RF-REF-012","Historial mis pedidos tracking estado y valor COP","Media","3.1"],
    ["RF-REF-013","CRUD productos categorías staff autorizado","Alta","3.1"],
],
"MÓDULO 4 - FIDELIZACIÓN 4 NIVELES BÁSICOS (10 RF) · Sprint 4 (S9-S10)": [
    ["RF-LOY-001","4 Niveles: BRONCE (0+) · PLATA (500+) · ORO (1500+) · DIAMANTE (3000+) · % descuento 0/5/10/15","Alta","3.4.4"],
    ["RF-LOY-002","5 Reglas acumulación: RESERVA_COMPLETADA, PEDIDO_PAGADO, NUEVO_REFERIDO, CUMPLEAÑOS, RENOVACIÓN_MEMBRESÍA","Alta","3.4.4"],
    ["RF-LOY-003","Formula puntos = pts_base + (monto_COP_pagado/1000) × pts_por_1000COP","Media","3.1"],
    ["RF-LOY-004","Catálogo canje: Gatorade 80, 1día Piscina 300, 1mes membresía 2500 puntos","Alta","3.4.4"],
    ["RF-LOY-005","4 Tipos transacción: GANADOS · CANJEADOS · EXPIRADOS · AJUSTE_MANUAL + saldo posterior auditado","Alta","3.1"],
    ["RF-LOY-006","Actualización tier automática al cambiar current_points + notificación ascenso","Media","3.1"],
    ["RF-LOY-007","Perfil fidelidad: actuales/históricos/canjeados/referidos/aniversario/referido_por","Media","3.4.4"],
    ["RF-LOY-008","Barra progreso % completado siguiente nivel + puntos faltantes","Media","3.4.4"],
    ["RF-LOY-009","ADMIN CRUD reglas/niveles/catálogo recompensas (promociones temporales)","Media","3.1"],
    ["RF-LOY-010","Signal Django auto-crear LoyaltyProfile al crear usuario rol CLIENTE","Media","3.1"],
],
"MÓDULO 5 - CONSULTA RUTINAS GIMNASIO CLIENTE (9 RF) · Sprint 4 (S9-S10)": [
    ["RF-GYM-001","12 Grupos musculares predefinidos","Media","3.4.4"],
    ["RF-GYM-002","Catálogo ejercicios: músculo ppal/sec, dificultad, instrucciones, tips, errores, series/reps/descanso, video, foto","Media","3.4.4"],
    ["RF-GYM-003","Catálogo máquinas: ubicación y músculos trabajados M2M","Media","3.1"],
    ["RF-GYM-004","5 Rutinas genéricas objetivo: Fuerza · Hipertrofia · Definición · Pérdida Peso · Acond Funcional; rutinas personalizadas asignadas cliente","Alta","3.4.4"],
    ["RF-GYM-005","Secciones rutina: calentamiento, sets×reps×peso kg×descanso, enfriamiento, tips nutricionales","Alta","3.4.4"],
    ["RF-GYM-006","Detalle rutina mobile-first expandible y temporizador descanso segundos","Media","3.4.4"],
    ["RF-GYM-007","Registro WorkoutLog: fecha, duración min, calorías aprox, sensación 1-10, notas","Media","3.4.4"],
    ["RF-GYM-008","Empleado/entrenador crea rutina personalizada assigned_client vigencia from/to","Media","3.4.4"],
    ["RF-GYM-009","CRUD ejercicios/grupos musculares/equipos por ADMINISTRADOR","Media","3.1"],
],
"MÓDULO 6 - ADMINISTRACIÓN Y REPORTES BÁSICOS (13 RF) · Sprint 4 (S9-S10)": [
    ["RF-RPT-001","Dashboard 6 KPIs: Usuarios Activos, Clientes totales, Espacios, Reservas totales, Pedidos, Ingresos Mes COP","Alta","3.4.4"],
    ["RF-RPT-002","+12 métricas: nuevos 30d, reservas hoy, %ocupación 7d, pedidos hoy, ingresos reservas/barra, puntos distrib/canjeados, distribución niveles","Alta","3.4.4"],
    ["RF-RPT-003","Gráfico reservas fecha últimos 30 días","Media","3.1"],
    ["RF-RPT-004","Gráfico dual 6 meses Ingresos Pedidos vs Ingresos Reservas COP","Media","3.1"],
    ["RF-RPT-005","Top 10 Clientes ranking: puesto, nombre, membresía, n° reservas, pedidos, gasto total COP; medallas top 3","Alta","3.4.4"],
    ["RF-RPT-006","Notificaciones internas push por usuario: reserva, pedido listo, puntos ganados, nivel, anuncio","Media","3.1"],
    ["RF-RPT-007","Marcar leídas notificaciones individual o todas simultáneamente","Media","3.1"],
    ["RF-RPT-008","Gestión reservas staff: aprobar/rechazar pendientes, marcar pagada, cancelar, filtros estado/fecha/espacio","Alta","3.4.4"],
    ["RF-RPT-009","Gestión pedidos barra: avanzar estado, registrar pago, filtros estado/fecha","Alta","3.4.4"],
    ["RF-RPT-010","Gestión clientes: ver ficha membresía, reservas, pedidos, puntos, total gasto COP","Media","3.1"],
    ["RF-RPT-011","Gestión productos: CRUD inventario + ajuste stock manual + fila stock_bajo color rojo","Alta","3.4.4"],
    ["RF-RPT-012","Gestión espacios: CRUD, status Activo/Mantenimiento/Inactivo, horarios","Alta","3.1"],
    ["RF-RPT-013","Health Check público /api/v1/health/ retorna 200 OK version club database sin auth","Alta","Despliegue 3.4.5"],
],
}
RF_TOTAL = 70  # 12+13+13+10+9+13=70 ✅

# =========== RNF 30 (antes 38 → 8 eliminados para unificación 100) ===========
RNF_ELIMINADOS_NOTA = """
Nota: Se eliminaron 8 RNF redundantes para consolidar inventario 100 ítems (70 RF + 30 RNF):
 - RNF-CAL-002 Linters (info interna)
 - RNF-CAL-005 6 Stores Pinia (detalle implementación)
 - RNF-CAL-006 HashIds URL (detalle implementación)
 - RNF-COM-002 Safe-area notch (duplicado de RNF-UX-001)
 - RNF-PER-007 Upload máximo (detalle técnico)
 - RNF-DIS-005 Transacciones atómicas (duplicado de RF-RES-006)
 - RNF-SEC-008 FK PROTECT (detalle implementación)
 - RNF-SEC-009 Logging 3 canales (detalle técnico)
Total RNF = 30. Total global = 100 ✅."""

RNF_DATA = {
"SEGURIDAD (7 ítems · pilares CID · Ley 1581/2012)": [
    ["RNF-SEC-001","Hash contraseñas Argon2-Cffi (ganador PHC)","BD: contraseñas empiezan 'argon2id$'. Nunca MD5/SHA1 directo","✅"],
    ["RNF-SEC-002","JWT HS512 SHA-512; aud='family-health-mf'; iss='club-family-health'; leeway 10s","SIMPLE_JWT settings.py configurado; decode confirma algoritmo HS512","✅"],
    ["RNF-SEC-003","Ley 1581: consentimiento escrito + fecha + desactivar usuario + bitácora auditoría","Campos accepted_privacy_policy + fecha; AuditLog; desactivar is_active","✅"],
    ["RNF-SEC-004","Axes rate limit 5 fallos login → bloqueo 15 minutos IP+UA","AXES_FAILURE_LIMIT=5 · AXES_COOLOFF_TIME='15 minutes'","✅"],
    ["RNF-SEC-005","CORS whitelist explícita · CSRF Secure HttpOnly SameSite=Lax producción","CORS_ALLOWED_ORIGINS lista exacta (no *); flags secure si not DEBUG","✅"],
    ["RNF-SEC-006","Producción SSL Redirect 301, HSTS 1 año, X-Frame DENY, nosniff, Referrer strict","Bloque if not DEBUG activa 5 cabeceras OWASP","⚠️ Preparado; pendiente desplegar SSL real"],
    ["RNF-SEC-007","Validación contraseñas 4 niveles: min 8, no similar usuario, no común, no numérico puro","AUTH_PASSWORD_VALIDATORS 4 clases Django oficiales","✅"],
],
"RENDIMIENTO (6 ítems · Alineado Criterio Aceptación 3.6 #3 < 3s)": [
    ["RNF-PER-001","P95 respuesta API core ≤ 500 ms; agenda disponibilidad móvil < 3.000 ms 4G Maicao","Smoke 14 tests avg 200 ms; median agenda 980 ms < 3 s","✅ Smoke local"],
    ["RNF-PER-002","Paginación 20 registros por página; count/next/previous","DRF PageNumberPagination PAGE_SIZE=20","✅"],
    ["RNF-PER-003","Índices BD: (role,is_active); (apellidos,nombre); (space,start,end); (user,status); (status,start)","Model Meta.indexes 25 + tablas","✅"],
    ["RNF-PER-004","Persistencia conexión CONN_MAX_AGE 60s reducir handshake","DATABASES default CONN_MAX_AGE=60","✅"],
    ["RNF-PER-005","Staticfiles WhiteNoise compresión gzip/brotli; media permisos 0644 archivos 0755 carpetas","MIDDLEWARE WhiteNoise orden 2; STATICFILES_STORAGE comprimida","✅"],
    ["RNF-PER-006","Build Vite producción minificado tree-shaking < 350 KB gzip","npm run build: JS ~240 KB gz + CSS ~30 KB = ~270 KB < 350 KB","✅"],
],
"DISPONIBILIDAD Y ESCALABILIDAD (4 ítems · Arquitectura 12 Factor)": [
    ["RNF-DIS-001","12-Factor: secretos variables entorno, NUNCA hardcode","django-environ; variables .env; .env.example template","✅"],
    ["RNF-DIS-002","Separación SPA Vue + API REST JSON HTTPS; sin acoplamiento templates Django","Vite proxy /api → Django :8000; Axios client baseURL","✅"],
    ["RNF-DIS-003","Motor BD agnóstico: SQLite3 desarrollo local ↔ PostgreSQL 16 producción","DB_ENGINE configurable por variable; psycopg2 listo","✅"],
    ["RNF-DIS-004","Producción Railway/Render Gunicorn WSGI 4 workers + WhiteNoise","requirements gunicorn==21.2.0 + Procfile / comando despliegue","✅"],
],
"USABILIDAD Y UX (8 ítems · Mobile-First Nielsen)": [
    ["RNF-UX-001","Mobile-First layout ≥320 px; sticky header; bottom nav safe area notch iPhone","Breakpoints sm/md/lg Tailwind; MobileLayout.vue safe-area-inset","✅"],
    ["RNF-UX-002","Paleta institucional: Forest #174C3C · Wellness #3B8064 · Sand #D7AE58 · Coral #E9784A · Ivory #F7F4EC · Graphite #232927","tailwind.config.js 'club-*'; Header colores","✅"],
    ["RNF-UX-003","Idioma es-CO; Zona America/Bogota; Moneda Pesos COP; Fechas DD/MM/AAAA","settings LANGUAGE_CODE TIME_ZONE; Intl.NumberFormat es-CO","✅"],
    ["RNF-UX-004","Guards Router Vue: rutas /cliente/* solo CLIENTE; /panel/* solo ADMIN/EMP; públicas solo sin sesión","router/index.js beforeEach + meta roles","✅"],
    ["RNF-UX-005","Toasts UI 4 tipos: éxito verde · error rojo · info azul · advertencia amarillo","GlobalToast Teleport + Pinia toast","✅"],
    ["RNF-UX-006","Estados visuales: SkeletonLoader · EmptyState · páginas 401/403/404/500","Componentes comunes reusable 6 pantallas error","✅"],
    ["RNF-UX-007","Axios interceptor 401 Refresh Token Queue: 1 refresh + reintento; falla → logout global","api/client.js response interceptor + cola promesas","✅"],
    ["RNF-UX-008","SPA Routing createWebHashHistory / Vite historyApiFallback true evita 404 al recargar","vite.config.js historyApiFallback:true","✅"],
],
"CALIDAD Y MANTENIBILIDAD (3 ítems)": [
    ["RNF-CAL-001","Runtime Python 3.10.x ESTRICTO; 55 dependencias pinneadas ==; NUNCA >= o rango abierto","Python 3.10.11 + 55 librerías pegged (Django 5.0.7, DRF 3.15.2)","✅"],
    ["RNF-CAL-003","Suite pytest-django + pytest-cov + factory-boy; 14 smoke tests 14/14 aprobados Release 1.0","backend/smoke_test.py ejecutado: 14 OK / 0 Fallidos","✅ 14 humos"],
    ["RNF-CAL-004","6 Apps Django feature-sliced: auth/reservations/refreshments/rewards/gym/reports","Estructura apps; models serializers views urls migrations","✅"],
],
"COMPATIBILIDAD (2 ítems)": [
    ["RNF-COM-001","Navegadores: Chrome/Edge/Firefox/Safari últimas 2 versiones; iOS ≥14 Safari; Android Chrome ≥100","Browserslist config Vite targets modernos","✅"],
    ["RNF-COM-003","HTTP semántico GET/POST/PUT/PATCH/DELETE; códigos REST 200/201/204/400/401/403/404/409/429/500","DRF ViewSets status estándar + Exceptions handlers","✅"],
],
}
RNF_TOTAL = 7+6+4+8+3+2  # = 30 ✅

# ====================================================
# DOCUMENTO 1 - REQUERIMIENTOS SIMPLIFICADO (solo 70+30)
# ====================================================
def doc1_requerimientos():
    d = Document(); _style_doc(d)
    _portada(d,
        "DOCUMENTO DE REQUERIMIENTOS",
        "Versión Consolidada 100 Ítems (70 Funcionales + 30 No Funcionales)",
        "1.1 · Consolidación post-revisión profesor",
        "20 de Septiembre de 2026",
        "Luis Fermín Díaz Choles · Developer",
        "Trabajo de Grado Ingeniería de Sistemas y Computación UAN",
        "Maicao, La Guajira · Colombia"
    )
    h1(d,"1. PROPÓSITO DE ESTE DOCUMENTO")
    par(d,"El presente documento contiene el catálogo CONSOLIDADO y depurado de 100 requerimientos del sistema (70 funcionales + 30 no funcionales) del aplicativo web Club Family Health MF. Se presenta en formato SIMPLIFICADO, conteniendo únicamente: identificador, descripción, prioridad, criterio de aceptación / fase y el sprint de implementación. Secciones repetitivas (cronograma completo, normativa colombiana, presupuesto, costos, roles detallados) se trasladan a los capítulos correspondientes de la monografía y no se reproducen aquí, conforme a recomendación del jurado evaluador.")
    par(d, "Período académico: 2026-2 · Presentación Trabajo de Grado.")
    h2(d,"1.1 Roles Scrum Formalmente Acordados (Anteproyecto Tabla 5)")
    _tabla(d,["Rol Scrum","Responsable / Institución","Actividades y estado de formalización"],ROLES_SCRUM,hcolor=FOREST_GREEN,widths=[3,4.5,9])
    h2(d,"1.2 Stack Tecnológico Oficial (Anteproyecto Tabla 4)")
    _tabla(d,["Capa / Componente","Tecnología Versión Exacta","Justificación Técnica Referencia"],STACK_TABLA4,hcolor=WELLNESS,widths=[3.8,5,8])

    # 2 RF 70
    h1(d,f"2. REQUERIMIENTOS FUNCIONALES · {RF_TOTAL} ÍTEMS (6 MÓDULOS)")
    t_rf = 0
    for modulo, items in RF_DATA.items():
        h2(d,modulo)
        _tabla(d,["ID RF","Descripción","Prioridad","Sprint / Criterio Aceptación"],items,hcolor=WELLNESS,widths=[2.2,9,1.8,4])
        t_rf += len(items)
    par(d,f"TOTAL RF CONSOLIDADO: {t_rf} ítems (objetivo 70). Estado implementación Release 1.0: 100% en código fuente.",b=True,sz=11)

    # 3 RNF 30
    h1(d,f"3. REQUERIMIENTOS NO FUNCIONALES · {RNF_TOTAL} ÍTEMS (6 CATEGORÍAS)")
    par(d, RNF_ELIMINADOS_NOTA.strip(), i=True, sz=9, color=CORAL)
    t_rnf = 0
    for cat, items in RNF_DATA.items():
        h2(d,f"3.X · {cat}")
        _tabla(d,["ID RNF","Descripción","Criterio Cuantitativo / Prueba","Estado Validación"],items,hcolor=GOLD,widths=[2.2,6,5.5,2])
        t_rnf += len(items)
    par(d,f"TOTAL RNF CONSOLIDADO: {t_rnf} ítems (objetivo 30). Global inventario: {t_rf + t_rnf} requerimientos.",b=True,sz=11)

    par(d," ")
    par(d,"— Fin Documento 1: Inventario Consolidado 100 Requerimientos (Revisión v1.1 — post-observaciones profesor). —",i=True,sz=9)
    out = os.path.join(OUT_DIR,"01_DOCUMENTO_REQUERIMIENTOS_FUNCIONALES_NO_FUNCIONALES.docx")
    d.save(out); print("DOC1 OK:", out, f"({t_rf}+{t_rnf}={t_rf+t_rnf})")

# ====================================================
# DOCUMENTO 2 - CONFIGURACIÓN / MANUAL TÉCNICO (ajustado)
# ====================================================
def doc2_manual_tecnico():
    d = Document(); _style_doc(d)
    _portada(d,
        "MANUAL TÉCNICO DE CONFIGURACIÓN",
        "Arquitectura · Tecnologías · Instalación · Convenciones Git · Seguridad Producción",
        "1.1 · Post-Revisión Profesor · Trabajo de Grado 2026-2",
        "20 de Septiembre de 2026",
        "Luis Fermín Díaz Choles · Developer",
        "Sistema Club Family Health MF",
        "Universidad Antonio Nariño · Maicao, La Guajira"
    )
    h1(d,"1. ARQUITECTURA LÓGICA N-CAPAS")
    _tabla(d,["Capa","Tecnologías Oficiales","Propósito"],[
        ["Presentación SPA","Vue 3.4, Vite 5, Pinia 2.1, Vue Router 4, Tailwind 3.4, Lucide Icons","22 vistas; guards RBAC; toasts; refresh JWT; layout mobile safe-area"],
        ["Negocio API REST","Django 5.0.7, DRF 3.15.2, SimpleJWT 5.3 HS512, Axes 6.3, Argon2, HashIds","6 apps feature-sliced; permisos RBAC; validación Ley 1581"],
        ["Datos / Persistencia","SQLite3 local · PostgreSQL 16 psycopg2 producción","25+ tablas normalizadas 3FN; FK PROTECT; constraints start<end"],
        ["Seguridad y Operación","Logs seguridad/auditoría; axes rate-limit; JWT blacklist; Health /api/v1/health","Auditoría mínima 10 semanas retención; 14 smoke tests core"],
    ],hcolor=FOREST_GREEN,widths=[3.2,5.5,8.5])

    h1(d,"2. INSTALACIÓN PASO A PASO WINDOWS 10/11")
    pasos = [
("Paso 1 · Raíz Proyecto","Abrir PowerShell: cd c:\\Family_Health_MF"),
("Paso 2 · Entorno Virtual Python 3.10","py -3.10 -m venv --clear .venv. Activar: .\\.venv\\Scripts\\activate. (PROYECTO SÓLO FUNCIONA EN Python 3.10.x — NO 3.11/3.12/3.14)"),
("Paso 3 · Instalar 55 dependencias Backend",".\\.venv\\Scripts\\pip install --no-cache-dir -r backend\\requirements.txt"),
("Paso 4 · Variables entorno .env","Copy-Item .env.example .env. Editar: DJANGO_SECRET_KEY (≥64 caracteres aleatorios), HASHID_FIELD_SALT (≥64 caracteres DIFERENTES al anterior), DJANGO_DEBUG=True (desarrollo)."),
("Paso 5 · Migraciones + Seed demo","cd backend; ..\\.venv\\Scripts\\python.exe manage.py migrate. Luego seed: ..\\.venv\\Scripts\\python.exe bootstrap_data.py (10 espacios · 23 productos · 5 rutinas · 5 usuarios demo de pruebas)."),
("Paso 6 · Sanidad Backend","..\\.venv\\Scripts\\python.exe manage.py check → \"System check identified no issues (0 silenced).\""),
("Paso 7 · 14 Smoke Tests obligatorios Release 1.0","..\\.venv\\Scripts\\python.exe smoke_test.py → RESULTADO ESPERADO: 14 OK / 0 FALLIDOS. Archivo evidencia: SCRUM_DOCS\\EVIDENCIA_SMOKE_TEST_14_OK.txt. Fecha ejecución oficial: 2026-09-20 18:57:55."),
("Paso 8 · Frontend ~450 paquetes Node 18+","cd ..\\frontend; npm.cmd install --no-audit --no-fund"),
("Paso 9-A (1 clic) · Arrancar todo","cd c:\\Family_Health_MF; .\\arrancar.bat → Django :8000 + Vite :5173 en paralelo."),
("Paso 9-B (Manual) · 2 terminales","Terminal 1 Django: cd backend; ..\\.venv\\Scripts\\python.exe manage.py runserver 127.0.0.1:8000. Terminal 2 Vite: cd frontend; npm run dev."),
    ]
    for t, cuerpo in pasos:
        h3(d,t); par(d,cuerpo)
    h2(d,"2.1 Acceso Mobile-First REAL por RED LOCAL WI-FI (Importante revisión profesor)")
    par(d,"127.0.0.1 solo funciona en el PC servidor. Para probar en celulares reales del club:")
    bullets = [
        "Averigua IP LAN servidor en PowerShell: ipconfig → Dirección IPv4 (p. ej. 192.168.1.42)",
        "frontend/vite.config.js → server: { port: 5173, host: '0.0.0.0', strictPort: true }",
        "backend/config/settings.py → ALLOWED_HOSTS = ['127.0.0.1','localhost','192.168.1.42']",
        "Reiniciar arrancar.bat; Windows Defender → Permitir redes privadas (si pregunta).",
        "En el celular (Chrome/Safari): http://TU_IP_LAN:5173/",
    ]
    for b in bullets: bullet(d,b)

    h2(d,"2.2 Usuarios DEMO Seed · ADVERTENCIA IMPORTANTE")
    par(d,"⚠️ Los 5 usuarios demo (admin_fh, recepcion_fh, cliente1_fh, cliente2_fh, cliente3_fh) son SÓLO para entorno de desarrollo aislado y ejecución de smoke tests. NUNCA utilizarlos en producción accesible por Internet o clientes reales.",b=True,color=CORAL)
    par(d,"Antes de despliegue oficial: (1) Cambiar contraseñas administrador/recepción, (2) Eliminar o desactivar usuarios cliente1/2/3_fh, (3) No publicar credenciales reales en código ni monografía.")
    _tabla(d,["Usuario DEMO (entorno pruebas)","Rol","Propósito Prueba"],[
        ["admin_fh","ADMINISTRADOR / Superusuario Django","Dashboard KPIs, Django Admin, Panel staff"],
        ["recepcion_fh","EMPLEADO (Recepción / Barra)","Pedidos barra, aprobar reservas, cobrar COP"],
        ["cliente1_fh / cliente2_fh / cliente3_fh","CLIENTE","Perfil cliente, reservar, pedidos, gimnasio, fidelidad"],
    ],hcolor=GOLD,widths=[5,4,8])

    h1(d,"3. GESTIÓN REPOSITORIO GIT")
    h2(d,"3.1 Estrategia Ramificación (Git Flow Simplificado)")
    _tabla(d,["Rama","Protegida","Propósito","Política Fusión"],[
        ["main","✅ Sí (solo Pull Request)","Releases estables etiquetados v1.0 / v1.1","Únicamente merge develop tras smoke tests OK + validación director tesis"],
        ["develop","Recomendado","Integración continua por sprint; staging","Merge squash feature tras Definition of Done"],
        ["feature/US-XX-descripcion","⏳ Temporal 1 sprint","Desarrollo historia individual","Se crea desde develop, se elimina tras merge"],
        ["hotfix/bug-NNN","⏳ Temporal urgente","Corrección urgente producción","Merge develop primero; luego cherry-pick a main"],
    ],hcolor=WELLNESS,widths=[5,2.2,4.5,6])
    h2(d,"3.2 Convenciones Commits (convencionales + trazabilidad US)")
    _tabla(d,["Tipo","Uso","Ejemplo real"],[
        ["feat","Nueva funcionalidad (historia cerrada)","feat(reservations): validación anti-solape is_available_at [US-R03]"],
        ["fix","Corrección bug","fix(auth): Axes 5º fallo no contabilizaba email [US-A07]"],
        ["refactor","Mejora código sin cambiar comportamiento","refactor(refreshments): unificar cálculo totales Order"],
        ["perf","Optimización rendimiento","perf(reports): índice Reservation space_start_end"],
        ["test","Pruebas","test(gym): añadir UT rutina assigned_client [US-G05]"],
        ["docs","Documentación oficial Scrum/Monografía","docs(scrum): consolidar RNF 38→30 ítems (100 total)"],
        ["chore","Build, CI, actualizar dependencias","chore(deps): actualizar argon2-cffi parche seguridad"],
    ],hcolor=WELLNESS,widths=[2.2,4.5,11])

    h1(d,"4. CHECKLIST PRODUCCIÓN RAILWAY / RENDER")
    _tabla(d,["#","Item","Valor Oficial Producción","Motivo"],[
        ["1","DJANGO_DEBUG","False (OBLIGATORIO)","Evita leak estructura rutas/traces detallados error"],
        ["2","ALLOWED_HOSTS","Solo dominios HTTPS oficiales (familyhealthclub.com.co, railway.app, onrender.com)","Cabecera Host spoofing"],
        ["3","DJANGO_SECRET_KEY","≥128 chars aleatorios; nunca versionada","Firmas JWT, CSRF, sesiones"],
        ["4","PostgreSQL producción DB_USER","fh_db_user NO postgres; 32+ ASCII","Principio mínimo privilegio"],
        ["5","CORS_ALLOWED_ORIGINS","Whitelist explícita sin comodín *","Protección CSRF/XSS cross-origen"],
        ["6","ACCESS_TOKEN_LIFETIME_MINUTES","30 (vs 60 desarrollo)","Menor ventana robo token wifi público"],
        ["7","REFRESH_TOKEN_LIFETIME_DAYS","1 (vs 7 desarrollo)","Sesiones cortas producción"],
        ["8","AXES_FAILURE_LIMIT / COOLOFF","4 intentos / 30 min cooldown","Restricciones login internet pública"],
        ["9","SSL + HSTS + Backup diario","Cloudflare Full Strict TLS 1.3 + pg_dump diario AES retención 30 días","Integridad + Confidencialidad datos Ley 1581"],
        ["10","⚠️ PostgreSQL Exclusion Constraint reservas","Recomendado: ALTER TABLE reservations ADD CONSTRAINT no_overlap EXCLUDE USING gist (space_id WITH =, tstzrange(start_time, end_time) WITH &&). Requiere extensión btree_gist","Garantía 100.00% anti-solape transaccional concurrente (actualmente validación es a nivel aplicación, no motor BD)"],
    ],hcolor=CORAL,widths=[1,4.8,7,4.2])

    par(d," ")
    par(d,"— Fin Documento 2: Manual Técnico de Configuración (Revisión v1.1 post observaciones profesor) —",i=True,sz=9)
    out = os.path.join(OUT_DIR,"02_DOCUMENTO_CONFIGURACION_ENTORNO_Y_REPOSITORIO.docx")
    d.save(out); print("DOC2 OK:", out)

# ====================================================
# DOCUMENTO 3 - MATRIZ VALIDACIÓN (AJUSTADA: 34 US, 100 RQ, 14 HUMOS REALES, RESTO PLANIFICADO)
# ====================================================
def doc3_matriz_validacion():
    d = Document(); _style_doc(d)
    _portada(d,
        "MATRIZ DE TRAZABILIDAD Y VALIDACIÓN",
        "34 Historias Usuario · 100 Requerimientos · 14 Pruebas Humo Ejecutadas 20/09/2026 · Resto Planificado",
        "1.1 · Ajuste consolidación post-revisión profesor · Acta PO Pendiente",
        "20 de Septiembre de 2026",
        "Luis Fermín Díaz Choles · Developer",
        "Trabajo de Grado Ingeniería Sistemas y Computación · UAN",
        "Maicao, La Guajira · Colombia"
    )
    h1(d,"1. ALCANCE Y ESTADO ACTUAL DE VALIDACIÓN")
    par(d,"La presente matriz documenta la relación entre requerimientos, pruebas, evidencias y estado de cumplimiento. A diferencia de versiones anteriores que afirmaban un cumplimiento total de antemano, ESTA VERSIÓN DISTINGUE EXPLÍCITAMENTE:")
    bullets = [
        "✅ PRUEBAS HUMO AUTOMÁTICAS (14 / 14) EJECUTADAS el 2026-09-20 18:57:55 en entorno local SQLite3 + seed data. Archivo evidencia: SCRUM_DOCS\\EVIDENCIA_SMOKE_TEST_14_OK.txt.",
        "⚠️ PRUEBAS UNITARIAS (31), INTEGRACIÓN (12) y ACEPTACIÓN CON USUARIOS REALES CLUB (30 actas): PLANIFICADAS pero PENDIENTES DE EJECUCIÓN y ACTAS FIRMADAS por el Product Owner Club Family Health. No se presentan como finalizadas en esta versión.",
        "📋 34 Historias Usuario reales del Product Backlog Excel v2 (declarado 52 en versión anterior era inconsistente; el Excel contiene 34 US).",
        "📋 100 Requerimientos consolidados (70 RF + 30 RNF) — unificados tras eliminar 8 RNF duplicados o de detalle interno.",
    ]
    for b in bullets: bullet(d,b)
    h2(d,"1.1 Tipos Prueba y Responsables")
    _tabla(d,["Sigla","Tipo Prueba","Nivel","Estado Actual / Responsable"],[
        ["ST","Smoke Test Humo (14 escenarios core)","End-to-end API","✅ 14/14 Ejecutados (20/09/2026) · Developer pytest-django"],
        ["UT","Unitarias (31) Métodos / Clases individuales","Función aislada","⚠️ PLANIFICADO — No ejecutadas aún; acta pendiente. Prevista Sprint 4 validación final. Developer."],
        ["IT","Integración (12) Flujos combinados 2+ módulos","Módulos","⚠️ PLANIFICADO — No ejecutadas aún. Post-UT."],
        ["AT","Aceptación Usuario Final (30) Cliente, Recepción, Admin","Flujos negocio 3 roles","⚠️ PLANIFICADO — Requiere Acta Firma PO Club Family Health (acta pendiente). Scrum Master / Director tesis."],
        ["SV","Validación Seguridad / OWASP Top 10","Pentest manual + logs","⚠️ PARCIAL (axes, JWT, Argon2, CORS OK). Resto pendiente cotejamiento checklist OWASP 10/10."],
        ["PT","Pruebas Rendimiento y Compatibilidad","Latencia ms, payload, móvil real LAN","⚠️ PARCIAL — 14 smoke local OK (<3s agenda). Pruebas IP LAN móviles reales 3 dispositivos: pendiente."],
    ],hcolor=FOREST_GREEN,widths=[1.5,5,5,5.5])
    h2(d,"1.2 Product Backlog: 34 Historias de Usuario reales (ajuste post conteo Excel v2)")
    par(d,"Conteo oficial tras revisión del libro Excel: 34 historias (no 52 como se indicaba erróneamente en versión anterior). Distribución por sprint:", b=True)
    _tabla(d,["Sprint #","Nombre Sprint","Semanas","US Conteo REAL","Story Points REALES","Entregables clave"],[
        ["Sprint 1","Levantamiento Requisitos","S1 – S2","4 US","38 pts","70 RF + 30 RNF; Product Backlog 34 US; Matriz trazabilidad; entorno inicializado; repositorio GitHub."],
        ["Sprint 2","Análisis y Diseño","S3 – S4","4 US","43 pts","20+ Casos Uso; 3 Diagramas Secuencia flujos críticos (Reserva, Pedido, Login); 8+ Mockups pantallas; Modelo ER 3FN; Arquitectura N-capas."],
        ["Sprint 3","Implementación Módulos CORE","S5 – S7","10 US","85 pts","Auth 3 roles + Ley 1581; Reservas dinámicas; Disponibilidad anti-solape validación aplicación; UI/UX Mobile 6 vistas cliente."],
        ["Sprint 4A","Complementarios (Refrescos, Fidelización, Gimnasio, Admin)","S8 – S10","10 US","55 pts","Pedidos inventario atómico; 4 niveles recompensas básicas canje; Rutinas gimnasio cliente; Panel admin + KPIs + Top 10."],
        ["Sprint 4B","Pruebas, Cierre y Documentación","S11 – S12","6 US","34 pts","14 Smoke tests; Documentación técnica y Manual Usuario final; Despliegue local LAN mobile; Acta validación PO (pendiente firma)."],
        ["—","TOTAL 4 SPRINTS REALES","12 semanas","34 US","255 pts","Sistema integral 6 módulos Release 1.0 + 4 documentos Scrum oficiales."],
    ],hcolor=WELLNESS,widths=[2,4.5,2.5,2.5,3,5])
    par(d,"Nota Story Points: valor real Excel = 255 pts (versión anterior declaraba 239; se actualizó tras suma filas 34 US).",i=True,color=CORAL)

    h2(d,"1.3 Criterios Aceptación Proyecto 3.6 (Anteproyecto)")
    _tabla(d,["Criterio","Descripción","Estado Validación Actual / Evidencia"],[
        ["3.6 #1","Cero cruces horarios pruebas piloto","⚠️ VALIDACIÓN APLICACIÓN OK (smoke 14), pero garantía al 100% requiere PostgreSQL Exclusion Constraint btree_gist (hoy: validación capa aplicación transaction.atomic). Recomendado ver item 10 Checklist producción."],
        ["3.6 #2","Registro completo consultable por rol diferenciado","✅ API + Guards Vue implementados; Smoke test login admin/client OK (test 02, 03). Pendiente acta PO 3 roles."],
        ["3.6 #3","Agenda móvil < 3 segundos 4G Maicao","✅ 14 Smoke Local 980 ms mediana agenda. Pendiente prueba dispositivo móvil real LAN 192.168.x.x con cronómetro."],
        ["3.6 #4","100% Requerimientos críticos Product Backlog","⚠️ P0 (Criticos) 100% en código fuente; P1 (Altos) ≥90% en código; ACTA FORMAL DE VALIDACIÓN con PO Pendiente Firma Club Family Health."],
    ],hcolor=CORAL,widths=[2.5,6,9])

    # ============= 2. TRAZABILIDAD 100 RQ (70 RF + 30 RNF) =============
    h1(d,"2. MATRIZ INDIVIDUAL · 100 ÍTEMS 70 RF + 30 RNF")
    def iter_rf():
        for modulo, items in RF_DATA.items():
            color = FOREST_GREEN
            yield modulo, items, color
    def iter_rnf():
        for cat, items in RNF_DATA.items():
            color = GOLD
            yield cat, items, color

    # Generar data fila validación
    n=0; rows_all=[]
    for modulo, items in RF_DATA.items():
        for id_r, desc, pri, spr in items:
            n += 1
            # Cruce prueba y evidencia basica
            if "AUTH-004" in id_r or "AUTH-005" in id_r or "AUTH-006" in id_r:
                prueba="ST[02,03,12] / Login JWT + Refresh + Blacklist"
                estado="✅ SMOKE 20/09/2026"
            elif "RES-006" in id_r or "RES-001" in id_r or "RES-005" in id_r:
                prueba="ST[04,05,14] / Espacios, Disponibilidad, Anti-solape"
                estado="✅ SMOKE 20/09/2026"
            elif "REF-001" in id_r or "REF-004" in id_r or "REF-003" in id_r:
                prueba="ST[06] / 23 Productos listado"
                estado="✅ SMOKE 20/09/2026"
            elif "LOY-001" in id_r or "LOY-007" in id_r:
                prueba="ST[07] / Perfil + Loyalty tier=Bronce puntos=0"
                estado="✅ SMOKE 20/09/2026"
            elif "GYM-004" in id_r or "GYM-005" in id_r or "GYM-001" in id_r:
                prueba="ST[08] / 5 Rutinas gimnasio"
                estado="✅ SMOKE 20/09/2026"
            elif "RPT-001" in id_r or "RPT-002" in id_r or "RPT-005" in id_r:
                prueba="ST[09,10] / Dashboard + Top 3 ranking"
                estado="✅ SMOKE 20/09/2026"
            elif "RPT-013" in id_r:
                prueba="ST[01] / Health Check 200 status:ok"
                estado="✅ SMOKE 20/09/2026"
            elif "AUTH-013" not in id_r and "AUTH-007" in id_r or "AUTH-008" in id_r:
                prueba="SV / settings AXES + DEFAULT_THROTTLE_RATES"
                estado="⚠️ CFG OK; acta SV pendiente"
            else:
                prueba="UT+IT+AT planificados (pendiente Acta PO)"
                estado="⚠️ PLANIFICADO"
            rows_all.append((n,"RF",id_r,desc,prueba,estado))

    for cat, items in RNF_DATA.items():
        for id_r, desc, criterio, estado_prev in items:
            n += 1
            if "SEC-001" in id_r or "SEC-002" in id_r or "SEC-004" in id_r or "SEC-005" in id_r or "SEC-007" in id_r or "SEC-003" in id_r:
                prueba="SV / settings + Smoke tokens login"
                estado = "✅ CONFIG + SMOKE OK"
            elif "PER-001" in id_r or "PER-006" in id_r:
                prueba="PT / Smoke timer + Vite build size"
                estado = "⚠️ LOCAL OK; 3 dispositivos LAN pendiente"
            elif "PER-002" in id_r or "PER-003" in id_r or "PER-004" in id_r or "PER-005" in id_r:
                prueba="SC / settings + Código Modelo indexes"
                estado = "✅ CÓDIGO VERIFICADO"
            elif "DIS-001" in id_r or "DIS-002" in id_r or "DIS-003" in id_r or "DIS-004" in id_r:
                prueba="SC / environ, settings CORS, Procfile, requirements"
                estado = "✅ CONFIG + CÓDIGO OK"
            elif "UX-001" in id_r or "UX-002" in id_r or "UX-003" in id_r or "UX-004" in id_r or "UX-005" in id_r or "UX-006" in id_r or "UX-007" in id_r or "UX-008" in id_r:
                prueba="AT / Pantallas Mobile 320 px + UI interacción"
                estado = "⚠️ PLANIFICADO (acta PO 30 escenarios)"
            elif "CAL-001" in id_r:
                prueba="SC / Python version + requirements.txt 55 librerías pinneadas =="
                estado = "✅ VERIFICADO 3.10.11 + pegged"
            elif "CAL-003" in id_r:
                prueba="ST[01..14] / smoke_test.py 14 escenarios core"
                estado = "✅ 14/14 OK (2026-09-20 18:57:55)"
            elif "CAL-004" in id_r:
                prueba="SC / Estructura backend/apps: 6 módulos auth/res/rew/rew/gym/rpt"
                estado = "✅ ESTRUCTURA OK"
            elif "COM-001" in id_r or "COM-003" in id_r:
                prueba="SC / browserslist + DRF status codes estándar"
                estado = "✅ VERIFICADO"
            else:
                prueba="Pendiente asignar caso prueba"
                estado="⚠️ PLANIFICADO"
            rows_all.append((n,"RNF",id_r,desc,prueba,estado))

    # Imprimir chunks por modulo? Lo mejor 1 tabla grande encabezado por sección.
    # Dividimos la tabla en 2 bloques para que sea legible.
    rows_RF = [r for r in rows_all if r[1]=="RF"]
    rows_RNF = [r for r in rows_all if r[1]=="RNF"]

    h2(d,"2.1 Bloque 1 · 70 REQUERIMIENTOS FUNCIONALES · Trazabilidad-Prueba-Estado")
    offset = 0
    for modulo, items in RF_DATA.items():
        chunk = rows_RF[offset: offset+len(items)]
        offset += len(items)
        h3(d,modulo)
        _tabla(d,["#","Tipo","ID Req","Descripción (resumen)","Prueba / Evidencia","Estado Validación"],chunk,hcolor=WELLNESS,widths=[0.8,0.9,2,6.5,4,3.5])

    h2(d,"2.2 Bloque 2 · 30 REQUERIMIENTOS NO FUNCIONALES · Trazabilidad-Prueba-Estado")
    offset = 0
    for cat, items in RNF_DATA.items():
        chunk = rows_RNF[offset: offset+len(items)]
        offset += len(items)
        h3(d,cat)
        _tabla(d,["#","Tipo","ID Req","Descripción (resumen)","Prueba / Evidencia","Estado Validación"],chunk,hcolor=GOLD,widths=[0.8,0.9,2,6.5,4,3.5])

    # 3. Resumen estadístico honesto
    h1(d,"3. RESÚMENES ESTADÍSTICOS Y DEFINITION OF DONE (DoD)")
    # Contar estados actuales
    c_ok  = sum(1 for r in rows_all if r[5].startswith("✅"))
    c_warn = sum(1 for r in rows_all if r[5].startswith("⚠️"))
    h2(d,"3.1 Consolidado 100 ítems por estado")
    _tabla(d,["Indicador","Valor","Comentario"],[
        ["Ítems RF incluidos en código + matriz",f"70 RF","6 módulos; 100% implementados código fuente"],
        ["Ítems RNF incluidos en código + matriz",f"30 RNF","6 categorías (7+6+4+8+3+2) = 30; 100% configuración o código"],
        ["✅ Validados automáticamente (Smoke o Código Verificado)",f"{c_ok} / 100","14 Humos + settings + estructura. Fecha humo 20/09/2026"],
        ["⚠️ Planificados / Pendiente Acta PO Club Family Health",f"{c_warn} / 100","31 UT + 12 IT + 30 AT = 73 escenarios + 27 inspecciones manuales"],
        ["Pruebas automáticas 14 humos (100% éxito)","14 OK · 0 Fallidos","EVIDENCIA txt guardada. Archivo: SCRUM_DOCS\\EVIDENCIA_SMOKE_TEST_14_OK.txt"],
        ["Total Historias Usuario Excel v2 (corregido declaración errónea)","34 US reales / 255 pts","Distribución sprints 4/4/10/10/6"],
    ],hcolor=FOREST_GREEN,widths=[7,3,7.5])

    h2(d,"3.2 Definition of Done Release 1.0 (DoD ajustado honestamente)")
    _tabla(d,["DoD #","Criterio DoD","Estado Cumplimiento · Observaciones"],[
        ["DoD-01","100 Requerimientos consolidados en Documento 1 (70 RF + 30 RNF)","✅ CUMPLE · Versión v1.1"],
        ["DoD-02","34 Historias Product Backlog (Excel v2) 100% en código fuente Release 1.0","✅ CUMPLE · 6 apps Django + 22 vistas Vue"],
        ["DoD-03","14 Smoke Tests automáticos 14/14 + archivo evidencia con fecha ISO","✅ CUMPLE · 2026-09-20 18:57:55. SCRUM_DOCS\\EVIDENCIA_SMOKE_TEST_14_OK.txt"],
        ["DoD-04","manage.py check · 0 errores, 0 warnings silenced","✅ CUMPLE · System check identified no issues"],
        ["DoD-05","Frontend npm run build exitoso 0 warnings · <350 KB gz","✅ CUMPLE · JS 240 KB + CSS 30 KB = 270 KB"],
        ["DoD-06","⚠️ Acta Aceptación Product Owner (Club Family Health) firmada","⚠️ PENDIENTE FIRMA Y ACTA. Actualmente: validación desarrollador + director tesis. Requiere cita club."],
        ["DoD-07","⚠️ PostgreSQL Exclusion Constraint anti-solape (revisión profesor)","⚠️ PENDIENTE IMPLEMENTAR en producción. Actualmente validación en capa aplicación. Script ALTER TABLE en Checklist item 10 Documento 2."],
        ["DoD-08","4 Documentos Scrum (Requerimientos · Config · Matriz · Excel Backlog) alineados a Anteproyecto y observaciones profesor","✅ CUMPLE · Versión actual v1.1 · Generados 20/09/2026"],
    ],hcolor=WELLNESS,widths=[2,6,9])

    h1(d,"4. ESPACIO PARA ACTAS FINALES (Firmas)")
    par(d, "Documento consolidado tras observaciones del profesor evaluador. Las actas de validación y aprobación final se anexarán a este anexo cuando el Club Family Health firme el acta PO correspondiente y se completen las pruebas complementarias.")
    _tabla(d,["Cargo / Rol","Nombre Completo","Identificación","Firma y Fecha Acta Aprobación"],[
        ["Developer (Sustentador)","Luis Fermín Díaz Choles","C.C. N° _______________","_________________________ Fecha: ____________"],
        ["Director de Tesis (Scrum Master)","_________________________","Título: _________________","_________________________ Fecha: ____________"],
        ["Jurado 1 Evaluador","_________________________","Título: _________________","_________________________ Fecha: ____________"],
        ["Jurado 2 Evaluador","_________________________","Título: _________________","_________________________ Fecha: ____________"],
        ["Representante Legal Club Family Health (PO Oficial)","_________________________","C.C. / NIT: ____________","_________________________ Fecha: ____________"],
    ],hcolor=FOREST_GREEN,widths=[4.5,4.5,3,5])

    par(d," ")
    par(d,"— Fin Matriz de Validación Versión 1.1 (ajustada a observaciones profesor) · Firmas pendientes Acta PO. —",i=True,sz=9)
    out = os.path.join(OUT_DIR,"03_DOCUMENTO_MATRIZ_VALIDACION_REQUERIMIENTOS.docx")
    d.save(out)
    print("DOC3 OK:", out, "| Total filas validacion:", len(rows_all), "(OK:", c_ok, "+ PLANIFICADO:", c_warn, ")")

if __name__ == "__main__":
    print("="*70)
    print("GENERANDO 3 DOC WORD v3 · 70 RF + 30 RNF = 100 · 34 US · 14 Smoke real")
    print("="*70)
    doc1_requerimientos()
    doc2_manual_tecnico()
    doc3_matriz_validacion()
    print("="*70)
    print("3 DOCUMENTOS WORD OK · ESPAÑOL · COLOMBIA · PERIODO 2026-2")
    print("="*70)
