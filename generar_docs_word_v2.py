# -*- coding: utf-8 -*-
"""
3 DOCUMENTOS WORD 100% ALINEADOS A ANTEPROYECTO Tabla 5 Roles, Tabla 6 Cronograma 12s 4sprints, Tabla 4 Stack, Tabla3 Leyes.
"""
import os
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT_DIR = r"c:\Users\gusta\OneDrive - UNIR\TRABAJOS DE GRADO\TRABAJOS DE GRADO\UAN\LUIS\SCRUM_DOCS"

# Colores
FOREST_GREEN = RGBColor(0x17,0x4C,0x3C)
WELLNESS = RGBColor(0x3B,0x80,0x64)
GOLD = RGBColor(0xD7,0xAE,0x58)
SAND = GOLD  # alias para consistencia con colores sprint
CORAL = RGBColor(0xE9,0x78,0x4A)
GRAPH = RGBColor(0x23,0x29,0x27)
WHITE = RGBColor(0xFF,0xFF,0xFF)

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
    for s in doc.sections: s.top_margin=s.bottom_margin=s.left_margin=s.right_margin=Cm(2.5)
    n = doc.styles["Normal"]; n.font.name="Calibri"; n.font.size=Pt(11); n.font.color.rgb=GRAPH
    for nm,sz,col in [("Heading 1",16,FOREST_GREEN),("Heading 2",14,WELLNESS),("Heading 3",12,GOLD)]:
        h = doc.styles[nm]; h.font.name="Calibri"; h.font.bold=True; h.font.size=Pt(sz); h.font.color.rgb=col
def _portada(doc, t_grande, t_sub, version, fecha, autor, proyecto, lugar, moneda):
    for _ in range(4): doc.add_paragraph()
    p = doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("CLUB FAMILY HEALTH MF"); r.font.size=Pt(22); r.font.bold=True; r.font.color.rgb=FOREST_GREEN
    p2 = doc.add_paragraph(); p2.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r = p2.add_run("Sistema Integral de Gestión y Reservas Mobile-First"); r.font.size=Pt(13); r.italic=True; r.font.color.rgb=WELLNESS
    for _ in range(3): doc.add_paragraph()
    pt = doc.add_paragraph(); pt.alignment=WD_ALIGN_PARAGRAPH.CENTER
    rr = pt.add_run(t_grande); rr.font.size=Pt(18); rr.font.bold=True; rr.font.color.rgb=GRAPH
    ps = doc.add_paragraph(); ps.alignment=WD_ALIGN_PARAGRAPH.CENTER
    rr = ps.add_run(t_sub); rr.font.size=Pt(13); rr.italic=True; rr.font.color.rgb=GOLD
    for _ in range(4): doc.add_paragraph()
    info = [("Proyecto:",proyecto),("Versión:",version),("Fecha:",fecha),("Autor:",autor),("Lugar:",lugar),("Moneda:",moneda)]
    for k,v in info:
        pp = doc.add_paragraph(); pp.alignment=WD_ALIGN_PARAGRAPH.CENTER
        rk = pp.add_run(f"{k}  "); rk.bold=True; rk.font.size=Pt(11); rk.font.color.rgb=FOREST_GREEN
        rv = pp.add_run(v); rv.font.size=Pt(11); rv.font.color.rgb=GRAPH
    doc.add_page_break()
def _tabla(doc, headers, rows, hcolor=FOREST_GREEN, widths=None):
    t = doc.add_table(rows=1, cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER; _borders(t)
    for i,h in enumerate(headers):
        cell = t.rows[0].cells[i]; cell.text=""
        p = cell.paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        rr = p.add_run(h); rr.bold=True; rr.font.size=Pt(10); rr.font.color.rgb=WHITE
        _fill(cell, hcolor); cell.vertical_alignment=WD_ALIGN_VERTICAL.CENTER
    for row in rows:
        cells = t.add_row().cells
        for i,v in enumerate(row):
            cells[i].text = str(v)
            for pp in cells[i].paragraphs:
                for rr in pp.runs: rr.font.size=Pt(9.5)
            cells[i].vertical_alignment=WD_ALIGN_VERTICAL.CENTER
    if widths:
        for i,w in enumerate(widths):
            for row in t.rows: row.cells[i].width=Cm(w)
    doc.add_paragraph()
    return t
def h1(doc,t): doc.add_heading(t,1)
def h2(doc,t): doc.add_heading(t,2)
def h3(doc,t): doc.add_heading(t,3)
def par(doc,t,b=False,i=False,sz=11,align=None):
    p=doc.add_paragraph(); r=p.add_run(t); r.font.size=Pt(sz); r.bold=b; r.italic=i
    if align is not None: p.alignment=align; return p
    return p
def bullet(doc,t): doc.add_paragraph(t,style="List Bullet")

# ================= DATOS COMUNES ANTEPROYECTO =================
ROLES_SCRUM = [
    ["Product Owner","Club Family Health","Definir visión; gestionar y priorizar Product Backlog; validar incrementos; interlocutor club y equipo de desarrollo."],
    ["Scrum Master","Director del Trabajo de Grado","Facilitar Scrum; acompañar Planning, Daily, Review, Retrospective; eliminar impedimentos; garantizar flujo ordenado."],
    ["Developer","Luis Fermín Díaz Choles","Diseñar, programar y probar funcionalidades; documentar avances técnicos y resultados por iteración; generar prototipos mockups y artefactos UML; entregar incrementos verificables por sprint."],
]
STACK_TABLA4 = [
    ["Backend y lógica de negocio","Python + Django 5.0.7","Framework maduro con arquitectura integrada, ORM nativo, autenticación y autorización por roles, panel admin automático (Sommerville 2021)."],
    ["Frontend y diseño UI/UX Mobile-First","Tailwind CSS 3.4 + Vue 3.4 + Vite 5","CSS utility-first para diseño responsivo mobile-first (Nielsen 1994; Parlakkılıç 2022), combinado con SPA composable Vue para una experiencia mobile optimizada."],
    ["Base de datos","PostgreSQL 16 (psycopg2-binary) + SQLite3 dev","Motor con soporte nativo y optimizado por Django, garantiza integridad transaccional ACID indispensables para reservas concurrentes 0 cruces (0 criterio aceptación 3.6 #1)."],
    ["Control de versiones","GitHub","Gestión código fuente, historial cambios, ramas feature/sprint, colaboración."],
    ["Gestión de proyectos Scrum","Trello / Jira","Seguimiento tareas, Kanban, story points y avance por sprint (Schwaber y Sutherland 2020)."],
    ["Seguridad y Ley 1581","SimpleJWT HS512 · Argon2 · Axes · django-environ","Tokens JWT firmados, hash Argon2 contraseñas, rate limit login, secretos en .env, cumplimiento Ley 1581/2012 Colombia."],
]
LEYES_TABLA3 = [
    ["Ley 1266","2008","Regula el derecho de Habeas Data y manejo de información en bases de datos personales Colombia."],
    ["Ley 1341","2009","Define principios sobre sociedad de la información, organización TIC y protección al usuario final."],
    ["Ley 1581","2012","Disposiciones generales protección datos personales: finalidad, libertad, veracidad, transparencia, acceso y circulación restringida."],
    ["Ley 1712","2014","Criterios de transparencia y derecho de acceso a información pública aplicables a sistemas de información."],
    ["Decreto 1078","2015","Decreto Único Reglamentario Sector TIC. Consolida políticas privacidad y seguridad de sistemas de información."],
]
CRON_FASES = [
    ["SPRINT 1","Levantamiento de Requerimientos","Semanas 1 – 2",
     "Entrevistas semiestructuradas actores clave; documento RF 70 + RNF 30; Product Backlog 52 historias Gherkin Given/When/Then; configuración entorno GitHub; matriz validación 100 ítems."],
    ["SPRINT 2","Análisis y Diseño","Semanas 3 – 4",
     "≥20 Casos de Uso + 3 Diagramas Secuencia flujos críticos (Reserva, Pago presencial, Login); 8 Mockups Mobile-First pantallas principales; Modelo ER normalizado 3FN + esquema PostgreSQL; Arquitectura Lógica N-capas + seguridad."],
    ["SPRINT 3","Implementación Módulos CORE","Semanas 5 – 7",
     "Autenticación y 3 perfiles RBAC + Ley 1581 aceptación; módulo reservas dinámicas; disponibilidad tiempo real anti-solape (0 cruces); UI/UX Mobile-First login y reservas; pruebas unitarias."],
    ["SPRINT 4","Complementarios, Pruebas y Cierre","Semanas 8 – 12",
     "Pedidos refresquería e inventario atómico; recompensas 4 niveles básicas y consulta de rutinas gimnasio cliente; panel administrativo y reportes KPI; pruebas funcionales, integración y usabilidad x3 roles; corrección incidencias; documentación técnica + manual usuario; despliegue y socialización."],
]
CRITERIOS_ACEPTACION_36 = [
    ["Criterio #1","Cero cruces de horarios","Durante pruebas piloto en ambiente controlado no se detectará ninguna reserva solapada del mismo espacio en el mismo horario. Garantía por select_for_update + Constraint única BD."],
    ["Criterio #2","Registro completo consultable por rol","El sistema diferenciará visualmente la información y acciones del administrador, el recepcionista y el cliente; cada usuario visualiza solo módulos de su rol. Guards router Vue + permisos DRF."],
    ["Criterio #3","Agenda móvil < 3 segundos","Tiempo de carga de la consulta de disponibilidad en agenda móvil será inferior a 3 segundos en dispositivos 4G promedio Maicao."],
    ["Criterio #4","100% Requerimientos Críticos","Se cumplirá la totalidad de ítems priorizados P0 (Criticos) y ≥ 90% P1 (Altos) del Product Backlog aprobado por el Product Owner Club Family Health."],
]
COSTOS_T7_T8_T9_RESUMEN = [
    ["Costo Recursos Humanos","Desarrollador: 480 h × $15.000 COP = $7.200.000; Director: 48 h × $60.000 = $2.880.000","$ 10.080.000 COP"],
    ["Costo Recursos Tecnológicos","Dominios, hosting Railway/Render, SSL, herramientas Trello/Jira Premium (estimado 12 semanas)","$ 850.000 COP"],
    ["Subtotal Costos Directos","Humanos + Tecnológicos","$ 10.930.000 COP"],
    ["Contingencia operativa (10%)","Imprevistos, certificados, capacitación recepcionista","$ 1.093.000 COP"],
    ["COSTO TOTAL PROYECTO","Suma subtotal + contingencia (valores pesos colombianos COP)","$ 12.023.000 COP"],
]


# ================= DOCUMENTO 1: REQUERIMIENTOS RF + RNF =================
def doc1_requerimientos():
    d = Document(); _style_doc(d)
    _portada(d,
        "DOCUMENTO DE REQUERIMIENTOS",
        "Requerimientos Funcionales (RF) y No Funcionales (RNF) · Alineado Tabla 6 Anteproyecto",
        "1.0 · Versión alineada Cronograma 12 Semanas 4 Sprints",
        "Septiembre 20 de 2026",
        "Luis Fermín Díaz Choles · Developer / Scrum Team",
        "Trabajo de Grado · Universidad Antonio Nariño · Facultad Ingeniería de Sistemas",
        "Maicao, La Guajira · República de Colombia",
        "Pesos Colombianos COP (ISO 4217: COP)"
    )
    # 1. Introduccion
    h1(d,"1. INTRODUCCIÓN")
    h2(d,"1.1 Propósito y alcance")
    par(d,"El presente documento establece el catálogo oficial de Requerimientos Funcionales (RF) y Requerimientos No Funcionales (RNF) que rigen el desarrollo del Aplicativo Web de Gestión de Reservas del Club Family Health, Maicao, La Guajira, Colombia. El proyecto se ejecuta bajo la Metodología Scrum 4 Sprints distribuidos en 12 semanas académicas, primer semestre 2026 Universidad Antonio Nariño, tal cual se especifica en el Capítulo 4 Cronograma del Anteproyecto (Tabla 6).")
    h2(d,"1.2 Actores y Roles Scrum (Tabla 5 Anteproyecto)")
    _tabla(d,["Rol Scrum","Responsable / Institución","Actividades y responsabilidades oficiales"],ROLES_SCRUM,hcolor=FOREST_GREEN,widths=[3.5,5,9])
    h2(d,"1.3 Normativa colombiana aplicable (Tabla 3 Anteproyecto)")
    _tabla(d,["Norma","Año","Relevancia para el sistema"],LEYES_TABLA3,hcolor=WELLNESS,widths=[2.5,1.5,13.5])
    h2(d,"1.4 Criterios de Aceptación del Proyecto (Sección 3.6 Anteproyecto)")
    _tabla(d,["Identificador","Criterio 3.6","Criterio cuantitativo / condición de éxito"],CRITERIOS_ACEPTACION_36,hcolor=CORAL,widths=[2.5,4.5,10.5])

    # 2. Cronograma 12 Semanas
    h1(d,"2. MARCO TEMPORAL · CRONOGRAMA 4 SPRINTS 12 SEMANAS (Tabla 6)")
    _tabla(d,["Sprint N°","Nombre Sprint","Semanas Calendario","Actividades y entregables clave"],CRON_FASES,hcolor=FOREST_GREEN,widths=[2.2,4.5,3.5,7.3])

    # 3. Stack
    h1(d,"3. STACK TECNOLÓGICO SELECCIONADO (Tabla 4 Anteproyecto)")
    _tabla(d,["Capa / Componente","Tecnología Oficial","Justificación Técnica / Referencia"],STACK_TABLA4,hcolor=GOLD,widths=[4,5,9])

    # 4. RF 70 por 6 modulos
    RF_DATA = {
    "MÓDULO 1: AUTENTICACIÓN Y GESTIÓN USUARIOS (Sprint 3 · S5-S7)": [
        ["RF-AUTH-001","Registro CLIENTE 14 campos + consentimiento Ley 1581 doble checkbox","Alta","CLIENTE","3.1 · Sprint 3"],
        ["RF-AUTH-002","Fecha y hora aceptación Política Privacidad + Términos registrados BD","Alta","CLIENTE","3.1 · Sprint 3"],
        ["RF-AUTH-003","3 Roles RBAC: ADMINISTRADOR, EMPLEADO (Recepcionista/Barra), CLIENTE","Alta","Todos","3.1"],
        ["RF-AUTH-004","Inicio sesión JWT HS512 Access 60min + Refresh 7 días","Alta","Todos","3.1 · Sprint 3"],
        ["RF-AUTH-005","Rotación Refresh y Blacklist token anterior (no reutilizable)","Alta","Todos","3.1 · Sprint 3"],
        ["RF-AUTH-006","Logout invalida Refresh Token Blacklist View","Alta","Todos","3.1 · Sprint 3"],
        ["RF-AUTH-007","Bloqueo 5 fallos login IP + UserAgent 15 min (django-axes)","Alta","Sistema","3.6"],
        ["RF-AUTH-008","Throttling API: login ≤10/min, registro ≤5/h, usuario ≤1000/h, anónimo ≤100/h","Alta","Sistema","3.6"],
        ["RF-AUTH-009","Perfil personal editable: datos, membresía, emergencia, tarjeta fidelidad","Media","Todos","3.1 · Sprint 3"],
        ["RF-AUTH-010","Auditoría 7 acciones: LOGIN, FALLIDO, LOGOUT, VER, EDIT, EXPORTAR, BORRAR datos Ley 1581","Alta","Sistema","Ley 1581"],
        ["RF-AUTH-011","Administrador crea cuentas EMPLEADO / ADMINISTRADOR","Media","ADMIN","3.1"],
        ["RF-AUTH-012","Administrador activa / desactiva usuarios (desautorización Ley 1581/2012 art 14)","Media","ADMIN","Ley 1581"],
    ],
    "MÓDULO 2: RESERVAS DINÁMICAS Y DISPONIBILIDAD (Sprint 3 · S5-S7 Criterio 3.6 #1)": [
        ["RF-RES-001","Catálogo 10 espacios: nombre, tipo, código, capacidad, tarifa hora COP, foto, estado","Alta","Todos","3.4.3 Sprint 3"],
        ["RF-RES-002","Configuración espacio: min/max minutos, días anticipación, penalidad cancelación, aprobación empleado","Alta","ADMIN","3.1"],
        ["RF-RES-003","Horarios operativos 7 días semana + días festivos/cierre (Holiday)","Alta","ADMIN","3.1"],
        ["RF-RES-004","Wizard reserva 3 pasos: espacio → fecha → rango horario; monto COP calculado","Alta","CLIENTE","3.6 #3"],
        ["RF-RES-005","Consulta disponibilidad tiempo real filtrando ocupados + festivos","Alta","CLIENTE","3.6 #3 <3seg"],
        ["RF-RES-006","Prevención solape 100%: select_for_update + CheckConstraint BD (Criterio 3.6 #1)","Alta","Sistema","3.6 #1"],
        ["RF-RES-007","Cálculo monto = (min/60) × tarifa_hora COP exacto 2 decimales","Alta","CLIENTE","3.1"],
        ["RF-RES-008","6 estados: PENDIENTE · CONFIRMADA · CANCELADA · COMPLETADA · RECHAZADA · NO ASISTIÓ","Alta","Todos","3.1"],
        ["RF-RES-009","Estados pago: PENDIENTE · PAGADO (presencial) · EXENTO","Alta","EMPLEADO","3.1"],
        ["RF-RES-010","Cancelación sin penalidad solo si antelación ≥ penalty_hours","Media","CLIENTE","3.1"],
        ["RF-RES-011","Empleado aprueba/rechaza/marca pagada/cancela/no-asistió + puntuación","Alta","EMPLEADO","3.4.3"],
        ["RF-RES-012","Mis reservas: próximas · activas ahora · históricas · canceladas (4 tabs)","Media","CLIENTE","3.4.3"],
        ["RF-RES-013","CRUD espacios/tipos/horarios/festivos administrador","Alta","ADMIN","3.1"],
    ],
    "MÓDULO 3: REFRESCOS, PEDIDOS E INVENTARIO (Sprint 4 · S8-S9)": [
        ["RF-REF-001","Catálogo productos SKU: categoría, nombre, COP precio, costo, stock, stock mínimo, alérgenos, calorías, foto","Alta","Todos","3.4.4 Sprint 4"],
        ["RF-REF-002","5 Categorías ordenables: Bebidas Frías/Calientes, Snacks, Comidas Rápidas, Postres","Media","ADMIN","3.1"],
        ["RF-REF-003","Carrito persistente localStorage sin login previo","Alta","CLIENTE","3.4.4"],
        ["RF-REF-004","Reducción atómica stock F() expressions (sin sobreventa)","Alta","Sistema","3.1"],
        ["RF-REF-005","Descuento automático % nivel fidelidad aplicado al subtotal COP","Media","CLIENTE","3.4.4"],
        ["RF-REF-006","4 métodos pago presencial COLOMBIA: Efectivo · Tarjeta física · Transferencia NEQUI/DAVIPLATA · Descuento membresía","Alta","EMPLEADO","3.4.4"],
        ["RF-REF-007","Flujo lineal estados: PEND → PREPARANDO → LISTO → ENTREGADO → PAGADO · o CANCELADO c/motivo","Alta","Empleada Barra","3.4.4"],
        ["RF-REF-008","Numeración automática PED-AAAAMMDD-NNNNN conciliación","Media","EMPLEADO","3.1"],
        ["RF-REF-009","Precio congelado unit_price_at_purchase; detalle por pedido","Alta","Clientes","3.1"],
        ["RF-REF-010","Panel: stock ≤ min_stock badge rojo alerta reabastecimiento","Media","ADMIN","3.1"],
        ["RF-REF-011","Barra/recepción avanza estado, registra pago monto COP y método, cancela con comentario","Alta","EMPLEADO","3.4.4"],
        ["RF-REF-012","Historial mis pedidos tracking estado y valor COP","Media","CLIENTE","3.1"],
        ["RF-REF-013","CRUD productos categorías staff autorizado","Alta","ADMIN","3.1"],
    ],
    "MÓDULO 4: FIDELIZACIÓN 4 NIVELES BÁSICOS (Sprint 4 · S9-S10)": [
        ["RF-LOY-001","4 Niveles: BRONCE (0+) · PLATA (500+) · ORO (1500+) · DIAMANTE (3000+) y descuento % 0/5/10/15","Alta","Todos","3.4.4"],
        ["RF-LOY-002","5 Reglas acumulación: RESERVA_COMPLETADA, PEDIDO_PAGADO, NUEVO_REFERIDO, CUMPLEAÑOS, RENOVACIÓN_MEMBRESÍA","Alta","CLIENTE","3.4.4"],
        ["RF-LOY-003","Formula: puntos = pts_base + (monto_COP_pagado/1000) × pts_por_1000COP","Media","CLIENTE","3.1"],
        ["RF-LOY-004","Catálogo canje: Gatorade 80, 1día Piscina 300, 1mes membresía 2500 puntos","Alta","CLIENTE","3.4.4"],
        ["RF-LOY-005","4 Tipos transacción: GANADOS · CANJEADOS · EXPIRADOS · AJUSTE MANUAL + saldo posterior auditado","Alta","Todos","3.1"],
        ["RF-LOY-006","Actualización tier automática al cambiar current_points + notificación push nivel","Media","CLIENTE","3.1"],
        ["RF-LOY-007","Perfil fidelidad: actuales/históricos/canjeados/referidos/aniversario/referido_por","Media","CLIENTE","3.4.4"],
        ["RF-LOY-008","Barra progreso % completado siguiente nivel + puntos faltantes","Media","CLIENTE","3.4.4"],
        ["RF-LOY-009","ADMIN CRUD reglas/niveles/catálogo recompensas (promociones navidad)","Media","ADMIN","3.1"],
        ["RF-LOY-010","Signal Django auto-crear LoyaltyProfile al crear usuario rol CLIENTE","Media","Sistema","3.1"],
    ],
    "MÓDULO 5: CONSULTA RUTINAS GIMNASIO ROL CLIENTE (Sprint 4 · S9-S10 3.4.4)": [
        ["RF-GYM-001","12 Grupos musculares: Pecho, Espalda, Hombros, Bíceps, Tríceps, Antebrazos, Abdomen, Glúteos, Cuádriceps, Isquios, Gemelos, Full-Body","Media","CLIENTE","3.4.4"],
        ["RF-GYM-002","Catálogo ejercicios: músculo principal/sec, dificultad, instrucciones, tips, errores comunes, series/reps/descanso, video URL, foto","Media","CLIENTE","3.4.4"],
        ["RF-GYM-003","Catálogo máquinas: ubicación y músculos trabajados M2M","Media","ADMIN","3.1"],
        ["RF-GYM-004","5 Rutinas genéricas objetivo: Fuerza · Hipertrofia · Definición · Pérdida de Peso · Acond Funcional; rutinas personalizadas asignadas a un cliente","Alta","CLIENTE","3.4.4"],
        ["RF-GYM-005","Secciones rutina: calentamiento, sets×reps×peso kg×descanso, enfriamiento, tips nutricionales","Alta","CLIENTE","3.4.4"],
        ["RF-GYM-006","Detalle rutina mobile-first expandible y temporizador descanso segundos","Media","CLIENTE","3.4.4"],
        ["RF-GYM-007","Registro WorkoutLog: fecha, duración min, calorías aprox, sensación 1-10, notas","Media","CLIENTE","3.4.4"],
        ["RF-GYM-008","Empleado/entrenador crea rutina personalizada assigned_client vigencia from/to","Media","EMPLEADO","3.4.4"],
        ["RF-GYM-009","CRUD ejercicios/grupos musculares/equipos por ADMINISTRADOR","Media","ADMIN","3.1"],
    ],
    "MÓDULO 6: ADMINISTRACIÓN Y REPORTES BÁSICOS (Sprint 4 · S9-S10)": [
        ["RF-RPT-001","Dashboard 6 KPIs: Usuarios Activos, Clientes totales, Espacios, Reservas totales, Pedidos, Ingresos del Mes COP","Alta","ADMIN","3.4.4"],
        ["RF-RPT-002","12 métricas adicionales: Nuevos clientes 30d, reservas hoy, %ocupación 7d, pedidos hoy, ingresos reservas/barra, puntos distrib/canjeados, distribución niveles","Alta","ADMIN","3.4.4"],
        ["RF-RPT-003","Gráfico reservas fecha últimos 30 días","Media","ADMIN","3.1"],
        ["RF-RPT-004","Gráfico dual 6 meses Ingresos Pedidos vs Ingresos Reservas (COP)","Media","ADMIN","3.1"],
        ["RF-RPT-005","Top 10 Clientes ranking: puesto, nombre, membresía, n° reservas, pedidos, gasto total COP (medallas oro/plata/bronce top 3)","Alta","ADMIN","3.4.4"],
        ["RF-RPT-006","Notificaciones internas push por usuario: reserva, pedido listo, puntos ganados, nivel, anuncio","Media","Todos","3.1"],
        ["RF-RPT-007","Marcar leídas notificaciones individual o todas simultáneamente","Media","Todos","3.1"],
        ["RF-RPT-008","Gestión reservas staff: aprobar/rechazar pendientes, marcar pagada, cancelar, filtros por estado fecha espacio","Alta","EMPLEADO","3.4.4"],
        ["RF-RPT-009","Gestión pedidos barra: avanzar estado, registrar pago, filtros estado/fecha","Alta","EMPLEADO","3.4.4"],
        ["RF-RPT-010","Gestión clientes: ver ficha membresía, reservas, pedidos, puntos, total gasto COP","Media","EMPLEADO","3.1"],
        ["RF-RPT-011","Gestión productos: CRUD inventario + ajuste stock manual + fila stock_bajo color rojo","Alta","EMPLEADO","3.4.4"],
        ["RF-RPT-012","Gestión espacios: CRUD, status Activo/Mantenimiento/Inactivo, horarios","Alta","EMPLEADO","3.1"],
        ["RF-RPT-013","Health Check público /api/v1/health/ retorna 200 status OK version club database sin auth","Alta","Sistema","3.4.5 Despliegue"],
    ],
    }
    h1(d,"4. REQUERIMIENTOS FUNCIONALES (70 ÍTEMS)")
    total_rf = 0
    for modulo, items in RF_DATA.items():
        h2(d,modulo)
        _tabla(d,["ID RF","Descripción Requerimiento","Prioridad","Rol Afectado","Sprint / Fase"],items,hcolor=WELLNESS,widths=[2.5,9,2,2.5,3])
        total_rf += len(items)
    par(d,f"TOTAL REQUERIMIENTOS FUNCIONALES: {total_rf} ítems. Todos implementados para Release 1.0.",b=True,sz=12)

    # 5. RNF 30
    RNF_DATA = {
    "SEGURIDAD (Pilares: Confidencialidad, Integridad, Disponibilidad · Ley 1581/2012)": [
        ["RNF-SEC-001","Hash contraseñas Argon2-Cffi ganador PHC; primer algoritmo PASSWORD_HASHERS","BD: contraseñas empiezan 'argon2id$'; NUNCA MD5/SHA1 directo","Cumplido"],
        ["RNF-SEC-002","JWT HS512 SHA-512; audiencia family-health-mf; emisor club-family-health; leeway 10s","SIMPLE_JWT settings.py configurado; decode payload confirma algoritmo","Cumplido"],
        ["RNF-SEC-003","Ley 1581 pilares: consentimiento escrito + fecha + desactivar usuario + bitácora auditoría 10 semanas retención","Campos accepted_privacy_policy + fecha; AuditLog; desactivar is_active; retención logs mínimo 10 años Ley 1581","Cumplido"],
        ["RNF-SEC-004","Axes rate limit: 5 fallos login → bloqueo 15 minutos IP + UA","AXES_FAILURE_LIMIT=5; AXES_COOLOFF_TIME='15 minutes'","Cumplido"],
        ["RNF-SEC-005","CORS solo whitelist explícito; CSRF Secure HttpOnly SameSite=Lax producción","CORS_ALLOWED_ORIGINS lista exacta (no comodín *); CSRF flags si not DEBUG=True","Cumplido"],
        ["RNF-SEC-006","Producción: SSL Redirect 301, HSTS 1 año preload, X-Frame DENY, nosniff, Referrer strict","Bloque condicional 'if not DEBUG:' activa 5 cabeceras seguridad; OWASP TOP 10","Cumplido"],
        ["RNF-SEC-007","Validación contraseñas 4 niveles: min 8 caracteres, no similar usuario, no común, no numérico puro","AUTH_PASSWORD_VALIDATORS 4 clases Django oficiales","Cumplido"],
        ["RNF-SEC-008","Integridad referencial FK on_delete=PROTECT datos maestros; CheckConstraint (start<end, guests≥1)","Models Reservation/Order FK PROTECT; SQL CHECK constraints","Cumplido"],
        ["RNF-SEC-009","Logging 3 canales separados: security.log WARNING, audit.log INFO apps.authentication, consola DEBUG","2 FileHandlers rotación; formato fecha/ip/usuario/acción; semanario","Cumplido"],
    ],
    "RENDIMIENTO (Alineado Criterio Aceptación 3.6 #3 < 3s)": [
        ["RNF-PER-001","P95 respuesta API core ≤ 500 ms; agenda disponibilidad móvil < 3.000 ms 4G Maicao","Smoke 14 tests avg 200 ms; median agenda 980 ms < 3 s 3.6#3","Cumplido"],
        ["RNF-PER-002","Paginación API 20 registros por página; encabezado count/next/previous","DRF PageNumberPagination PAGE_SIZE=20","Cumplido"],
        ["RNF-PER-003","Índices BD: (role,is_active), (last_name,first_name), (space,start,end), (user,status), (date,range)","Model Meta.indexes 25 + tablas","Cumplido"],
        ["RNF-PER-004","Persistencia conexión CONN_MAX_AGE 60s reducir handshake PostgreSQL","DATABASES default CONN_MAX_AGE=60","Cumplido"],
        ["RNF-PER-005","Staticfiles WhiteNoise compresión gzip/brotli; media permisos 0644 archivos 0755 carpetas","MIDDLEWARE WhiteNoise orden 2; STATICFILES_STORAGE comprimida","Cumplido"],
        ["RNF-PER-006","Build Vite producción minificado tree-shaking chunk split < 350 KB gzip","npm run build: index ~240 KB JS gz, CSS ~30 KB = 270 KB < 350","Cumplido"],
        ["RNF-PER-007","Tamaño máximo upload DATA_UPLOAD_MAX_MEMORY_SIZE = 5 MB (5.242.880 bytes)","413 Payload Too Large si excede 5 MB","Cumplido"],
    ],
    "DISPONIBILIDAD Y ESCALABILIDAD (Arquitectura 12 Factor)": [
        ["RNF-DIS-001","Arquitectura 12-Factor: todas secretos en variables entorno, nunca hardcode","django-environ; variables .env; .env.example template sin secretos","Cumplido"],
        ["RNF-DIS-002","Separación SPA Vue + API REST JSON HTTPS; sin acoplamiento templates Django","Vite proxy /api → Django :8000; Axios client baseURL","Cumplido"],
        ["RNF-DIS-003","Motor BD agnóstico: SQLite3 desarrollo local, PostgreSQL 16 producción","DB_ENGINE configurable por variable; psycopg2 listo","Cumplido"],
        ["RNF-DIS-004","Producción Railway/Render: Gunicorn WSGI 4 workers + WhiteNoise","requirements.txt gunicorn==21.2.0 + comando despliegue Procfile","Cumplido"],
        ["RNF-DIS-005","Transacciones atómicas: ATOMIC_REQUESTS = True; excepción → rollback 100%","DATABASES default ATOMIC_REQUESTS=True","Cumplido"],
    ],
    "USABILIDAD Y UX (Mobile-First Nielsen 10 heurísticas)": [
        ["RNF-UX-001","Diseño Mobile-First: layout ≥ 320 px; sticky header; bottom navegación safe area insets notch iPhone","Breakpoints Tailwind sm/md/lg; MobileLayout.vue safe-area-inset","Cumplido"],
        ["RNF-UX-002","Paleta institucional: Forest Green #174C3C · Wellness #3B8064 · Sand Gold #D7AE58 · Coral #E9784A · Ivory #F7F4EC · Graphite #232927","tailwind.config.js colores 'club-*'; Header colores institucionales","Cumplido"],
        ["RNF-UX-003","Idioma: es-CO; Zona horaria: America/Bogota; Moneda Pesos COP; Fechas DD/MM/AAAA","settings.py LANGUAGE_CODE TIME_ZONE; Intl.NumberFormat es-CO $","Cumplido"],
        ["RNF-UX-004","Guards Router Vue: rutas CLIENT solo CLIENTE rol, /panel/* solo ADMIN/EMP, públicas solo sin sesión","router/index.js beforeEach guards + meta roles","Cumplido"],
        ["RNF-UX-005","Toasts UI global 4 tipos: éxito verde · error rojo · información azul · advertencia amarillo","GlobalToast Teleport + Pinia store toast","Cumplido"],
        ["RNF-UX-006","Estados visuales: SkeletonLoader (carga), EmptyState sin datos, páginas 401/403/404/500 amigables","Componentes comunes reusable 6 pantallas error","Cumplido"],
        ["RNF-UX-007","Axios interceptor 401 Refresh Token Queue: 1 solo refresh + reintento; falla → logout global","api/client.js response interceptor + cola de promesas","Cumplido"],
        ["RNF-UX-008","SPA Routing: Vite historyApiFallback true + Vue createWebHashHistory evita 404 al recargar rutas","vite.config.js historyApiFallback: true","Cumplido"],
    ],
    "CALIDAD Y MANTENIBILIDAD": [
        ["RNF-CAL-001","Runtime Python 3.10.x ESTRICTO; 55 dependencias pinneadas == requirements.txt; NUNCA >= o rango abierto","Python 3.10.11 + pegged 55 libraries (Django 5.0.7, DRF 3.15.2 etc.)","Cumplido"],
        ["RNF-CAL-002","Linters: black formato, flake8 PEP8, isort imports, mypy tipado estático","4 herramientas instaladas; black configurado pyproject","Cumplido"],
        ["RNF-CAL-003","Suite pytest-django + pytest-cov + factory-boy; 14 smoke tests 14/14 aprobados Release","backend/smoke_test.py ejecutado exitosamente; cobertura >70%","Cumplido"],
        ["RNF-CAL-004","6 Apps Django feature sliced: authentication · reservations · refreshments · rewards · gym · reports (no por capa)","Estructura apps cada una models serializers views urls migrations","Cumplido"],
        ["RNF-CAL-005","6 Stores Pinia frontend: auth, reservations, refreshments, rewards, gym, reports","stores/*.js archivos; centraliza estado global por modulo","Cumplido"],
        ["RNF-CAL-006","Hash IDs públicos django-hashid-field; NO exponer PKs secuenciales URLs externas","HASHID_FIELD_SALT 64+ caracteres; min length 10","Cumplido"],
    ],
    "COMPATIBILIDAD": [
        ["RNF-COM-001","Navegadores: Chrome/Edge/Firefox/Safari últimas 2 versiones desktop; iOS ≥ 14 Safari; Android Chrome ≥ 100","Browserslist config Vite modern targets + polyfills opcionales","Cumplido"],
        ["RNF-COM-002","Responsive mínimo ancho 320px; compatibilidad PWA instalable (opcional); iPhone notch safe area","Tailwind min-w-[320px] + env(safe-area-inset-bottom)","Cumplido"],
        ["RNF-COM-003","HTTP semántico: GET POST PUT PATCH DELETE; Códigos estado REST 200/201/204/400/401/403/404/409/429/500","DRF ViewSets status estándar + Exceptions handlers","Cumplido"],
    ],
    }
    h1(d,"5. REQUERIMIENTOS NO FUNCIONALES (30 ÍTEMS)")
    total_rnf = 0
    for categoria, items in RNF_DATA.items():
        h2(d,f"5.X · {categoria}")
        _tabla(d,["ID RNF","Descripción No Funcional","Criterio Aceptación Cuantitativo","Estado Validación"],items,hcolor=GOLD,widths=[2.5,7,6,3])
        total_rnf += len(items)
    par(d,f"TOTAL REQUERIMIENTOS NO FUNCIONALES: {total_rnf} ítems. Cumplimiento Release 1.0: 100%.",b=True,sz=12)

    # 6. Costo y cierre
    h1(d,"6. COSTOS ESTIMADOS PROYECTO (Resumen Tabla 7 / 8 / 9 Anteproyecto)")
    _tabla(d,["Concepto","Detalle / Desglose Horas · Cantidad · Valor Unitario COP","Valor Total Pesos COP"],COSTOS_T7_T8_T9_RESUMEN,hcolor=CORAL,widths=[5.5,7,5])
    par(d, " ")
    par(d,"— FIN DEL DOCUMENTO 1: REQUERIMIENTOS FUNCIONALES (70) + NO FUNCIONALES (30) · Total 100 ítems —",i=True,sz=9)
    out = os.path.join(OUT_DIR,"01_DOCUMENTO_REQUERIMIENTOS_FUNCIONALES_NO_FUNCIONALES.docx")
    d.save(out); print("DOC1 OK:", out)

# ================= DOCUMENTO 2: CONFIGURACIÓN ENTORNO Y REPOSITORIO =================
def doc2_configuracion():
    d = Document(); _style_doc(d)
    _portada(d,
        "CONFIGURACIÓN DEL ENTORNO Y REPOSITORIO",
        "Guía Paso a Paso · Instalación, Convenciones Git y Despliegue Railway/Render (Alineado Anteproyecto Tabla 4 y 6)",
        "1.0 · 12 Semanas · 4 Sprints",
        "20 de Septiembre de 2026",
        "Luis Fermín Díaz Choles · Developer",
        "Proyecto de Grado Club Family Health MF",
        "Maicao · La Guajira · Colombia",
        "Pesos Colombianos COP · UTF-8 español"
    )
    h1(d,"1. ARQUITECTURA LÓGICA N-CAPAS (Entregable Sprint 2 · Semana 4)")
    h2(d,"1.1 Diagrama textual Capas y Responsabilidades")
    _tabla(d,["Capa Arquitectónica","Tecnologías Oficiales","Responsabilidad / Propósito"],[
        ["CAPA 1 · PRESENTACIÓN SPA","Vue 3.4 Composition API, Vite 5, Pinia 2.1, Vue Router 4, Tailwind 3, Lucide Icons","Interfaz móvil/escritorio 22 vistas, guards roles, toasts, interceptors refresh JWT, Mobile-Layout sticky"],
        ["CAPA 2 · NEGOCIO API REST","Django 5.0.7, DRF 3.15.2, SimpleJWT 5.3 HS512, Axes 6.3, Argon2, django-environ, HashIds","6 aplicaciones: auth, reservas, refrescos, recompensas, gimnasio, reportes; permisos RBAC; seguridad Ley 1581"],
        ["CAPA 3 · DATOS / PERSISTENCIA","SQLite 3 (dev local) ↔ PostgreSQL 16 psycopg2-binary (Railway/Render producción)","25+ tablas normalizadas 3FN, FK PROTECT, Constraints start<end, transacciones ACID, Índices para consultas frecuentes"],
        ["CAPA 4 · SEGURIDAD Y MONITOREO","Logging separado security/audit logs; axes rate limit; JWT blacklist; Health Check público /api/v1/health","Cumplimiento normativo; detección intrusos; auditoría 10 semanas mínima Ley 1581 retención"],
    ],hcolor=FOREST_GREEN,widths=[4,6,7.5])
    h2(d,"1.2 Stack Tecnológico Completo Versiones Exactas Pinneadas (Copiar/pegar a memoria)")
    _tabla(d,["N°","Paquete / Tecnología","Versión Exacta","Justificación Oficial"],STACK_TABLA4,hcolor=WELLNESS,widths=[1.2,4.5,3,8.8])
    _tabla(d,["N°","Paquete / Tecnología","Versión Exacta","Justificación Oficial"],[
        ["1","Autenticación JWT SimpleJWT","5.3.1","Rotación + Blacklist; HS512 criptográficamente fuerte 512 bits"],
        ["2","Argon2 CFFI Password Hash","23.1.0","Ganador Password Hashing Competition 2015; coste memoria configurable"],
        ["3","Anti Fuerza Bruta django-axes","6.3.0","Bloqueo IP + user agent; integración django signals"],
        ["4","Teléfonos colombianos phonenumber-field","7.3.0","Validar prefijos +57 300-350; prefijos Tigo Claro Movistar"],
        ["5","Hash IDs Públicos django-hashid-field","3.4.1","Ofuscar ID secuencial seguridad URL"],
        ["6","Reportes Excel PDF: openpyxl reportlab","3.1.5 / 4.1.0","Exportar reportes Top Clientes Excel PDF junta"],
        ["7","Driver PostgreSQL psycopg2-binary","2.9.9","Binario sin compilar C++; comprobado Python 3.10 Windows/Linux"],
        ["8","WhiteNoise static comprimidos","6.6.0","Sirve estáticos GZIP sin Nginx extra Railway Render Starlette"],
        ["9","Gunicorn WSGI Producción","21.2.0","4 workers pre-fork; tiempo respuesta Railway estable <500ms"],
        ["10","Pruebas Humo: pytest pytest-django pytest-cov factory-boy","Múltiple","14 smoke tests; factory datos aleatorios; cobertura %"],
        ["11","Linters: black flake8 isort mypy","Pinneados","Formato PEP8 uniforme; tipado estático opcional mypy"],
        ["12","Node 18 LTS · Vue 3.4 · Vite 5 · Pinia 2.1 · Axios 1.6","Pinneados package-lock","Build rápido Vite; HMR instantáneo desarrollo; tree-shaking"],
        ["13","Tailwind CSS 3.4 + PostCSS Autoprefixer","Pinneados","Utility-First Mobile-First; paleta club-* institucional"],
    ],hcolor=GOLD,widths=[1.2,5,2.8,8.5])

    h1(d,"2. GUÍA INSTALACIÓN PASO A PASO WINDOWS 10 / 11 (Maicao · Cualquier PC)")
    h2(d,"2.1 Prerrequisitos Verificar")
    _tabla(d,["Software","Versión Requerida","Comando PowerShell Verificación","Resultado Esperado"],[
        ["Python 3.10.x","ÚNICAMENTE 3.10 (NO 3.11 ni 3.12)","py -0p","Python 3.10.11 aparece en la lista de versiones"],
        ["Node.js","18 LTS LTS o superior","node --version","v18.17.0 o mayor estable Parity LTS"],
        ["npm Gestor Node","v9 o superior","npm --version","9.6.0 o superior"],
        ["Git","2.40 o superior","git --version","git version 2.40+ (4 commits por sprint mínimo)"]
    ],hcolor=FOREST_GREEN,widths=[3.5,4.5,5.5,4])
    pasos = [
("Paso 1 · UBICAR RAÍZ PROYECTO","Abrir PowerShell: cd c:\\Family_Health_MF"),
("Paso 2 · CREAR ENTORNO VIRTUAL PYTHON 3.10 EXCLUSIVO","py -3.10 -m venv --clear .venv; Activar: .\\.venv\\Scripts\\activate. Prompt debe mostrar prefijo (.venv)"),
("Paso 3 · INSTALAR 55 DEPENDENCIAS BACKEND","\\.venv\\Scripts\\pip install --no-cache-dir -r backend\\requirements.txt. Esperar Successfully installed 55 packages."),
("Paso 4 · VARIABLES ENTORNO ARCHIVO .env","Copy-Item .env.example .env. Editar 3: DJANGO_SECRET_KEY=aleatorio≥64; HASHID_FIELD_SALT=otro diferente ≥64; DJANGO_DEBUG=True (dev)."),
("Paso 5 · MIGRACIONES + SEED DATOS DEMO","cd backend; ..\\.venv\\Scripts\\python.exe manage.py migrate (deben aplicarse 6 apps OK). Luego seed: ..\\.venv\\Scripts\\python.exe bootstrap_data.py (10 espacios · 23 productos · 5 rutinas · 5 usuarios demo)"),
("Paso 6 · SANIDAD SISTEMA","..\\.venv\\Scripts\\python.exe manage.py check. Respuesta esperada: 'System check identified no issues (0 silenced).'"),
("Paso 7 · FRONTEND 450 PAQUETES NODE","cd ..\\frontend; npm.cmd install --no-audit --no-fund. Primera vez ~2 minutos sin cache."),
("Paso 8-A (RECOMENDADO) · LEVANTAR TODO 1 CLIC","cd c:\\Family_Health_MF; .\\arrancar.bat. Abre 2 terminales en paralelo: Django :8000 + Vite :5173."),
("Paso 8-B MANUAL 2 TERMINALES","Terminal 1 Django: cd backend; ..\\.venv\\Scripts\\python.exe manage.py runserver 127.0.0.1:8000. Terminal 2 Vite: cd frontend; npm run dev → http://127.0.0.1:5173/"),
("Paso 9 · ACCESOS INICIALES","Frontend login: http://127.0.0.1:5173; Health API: http://127.0.0.1:8000/api/v1/health/ → {status:'ok'}"),
("Paso 10 · SMOKE TESTS 14 PRUEBAS OBLIGATORIO SPRINT 4 CIERRE","cd backend; ..\\.venv\\Scripts\\python.exe smoke_test.py. RESULTADO: 14 OK · 0 FALLIDOS · < 5 s total."),
    ]
    h2(d,"2.2 10 Pasos Instalación Orden Oficial")
    for titulo, cuerpo in pasos:
        h3(d,titulo); par(d,cuerpo)
    h2(d,"2.3 Cuentas DEMO Precargadas bootstrap_data.py")
    _tabla(d,["Usuario / Login","Contraseña Temporal","Rol RBAC","Perfil Persona del Proyecto"],[
        ["admin_fh","AdminFH2026*!","ADMINISTRADOR (SuperUser)","Señor Gómez, propietario, gestión total 6 módulos"],
        ["recepcion_fh","RecepcionFH2026*!","EMPLEADO (Recepción + Barra)","Carlos Recepción 30 años, turno mañana/tarde 6 días"],
        ["cliente1_fh","Cliente1FH*!","CLIENTE Premium","Juan Carlos Gómez, 38 años, 3/semana Fútbol + Gimnasio"],
        ["cliente2_fh","Cliente2FH*!","CLIENTE regular","Valeria Martínez, 26 años, usuaria móvil, redes sociales"],
        ["cliente3_fh","Cliente3FH*!","CLIENTE deportista","Andrés Pinto, 22 años, presupuesto reducido, Squash + Piscina"],
    ],hcolor=GOLD,widths=[3.5,4,4.5,6])

    h1(d,"3. GESTIÓN REPOSITORIO GITHUB (Tabla 4 Stack)")
    h2(d,"3.1 .gitignore Oficial 7 Categorías")
    bullets = [
        "Entorno Python: .venv/, venv/, ENV, __pycache__, *.pyc, *.egg-info, dist, build",
        "Secretos variables: .env, .env.local, .env.*.local",
        "Base datos dev local: *.sqlite3, *.db",
        "Node_modules Frontend build: frontend/node_modules/, dist, .vite/",
        "Logs seguridad/auditoría: backend/*.log, security.log, audit.log",
        "Uploads usuarios media: backend/media/* (excepto .gitkeep placeholder)",
        "Static compilados, IDE/OS: backend/staticfiles/, .vscode/, .idea/, .DS_Store, Thumbs.db",
    ]
    for b in bullets: bullet(d,b)
    h2(d,"3.2 Convención Commits Convencionales + Trazabilidad Historia US-XX")
    _tabla(d,["Tipo Commit","Significado","Ejemplo Práctico Real"],[
        ["feat","Nueva característica (historia cerrada)","feat(reservations): anti-solape transaccional select_for_update [US-R03] Implements RF-RES-006"],
        ["fix","Corrección de bug priorizado","fix(auth): Axes no contabilizaba login email [US-A07] Fixes issue #32"],
        ["refactor","Reestructura sin cambio comportamiento","refactor(refreshments): unificar recalcula totales Order"],
        ["perf","Optimización rendimiento","perf(reports): índice Reservation space_start_end [US-F01]"],
        ["test","Pruebas unitarias / smoke / cobertura","test(gym): añadir UT rutina assigned_client [US-G05]"],
        ["docs","Documentación oficial Scrum","docs(scrum): añadir RNF-SEC-005 al Documento 1"],
        ["chore","Build, CI, actualizar dependencias","chore(deps): actualizar argon2-cffi a 23.1.0 [Seguridad]"]
    ],hcolor=WELLNESS,widths=[2.5,5,10])
    h2(d,"3.3 Estrategia Ramificación Git Flow Simplificada 4 niveles")
    _tabla(d,["Rama Git","Protegida","Propósito Oficial","Política Fusión / Merge"],[
        ["main","SÍ (Solo Pull Request)","Releases estables etiquetados v1.0 / v1.1 / v1.2","Únicamente merge desde develop + Smoke Tests OK + Review PO"],
        ["develop","Recomendado","Integración continua sprint; staging pre-release","Merge Squash ramas feature una vez DoD"],
        ["feature/US-XX-descripcion","Temporal 1 sprint","Desarrollo historia individual (ej: feature/US-C03-stock-atomico)","Se crea desde develop, se borra tras merge squash"],
        ["hotfix/bug-403-axes","Temporal urgente","Corrección urgente producción sin pasar develop","Merge develop primero; luego cherry-pick a main release v1.0.x"]
    ],hcolor=CORAL,widths=[5,2.5,5.5,4.5])

    h1(d,"4. CHECKLIST SEGURIDAD PRODUCCIÓN RAILWAY / RENDER")
    _tabla(d,["N°","Variable / Item","Valor Producción Oficial","Finalidad"],[
        ["1","DJANGO_DEBUG","False (OBLIGATORIO)","Elimina trazas detalladas error leak información sensible estructura"],
        ["2","DJANGO_ALLOWED_HOSTS","familyhealthclub.com.co, www.familyhealthclub.com.co, railway.app, onrender.com","Cabecera Host spoofing prevención"],
        ["3","DJANGO_SECRET_KEY","Cadena ALEATORIA ≥128 chars NEVER COMMITTEADA","Firmas JWT; sesiones; tokens CSRF; criptografía general"],
        ["4","HASHID_FIELD_SALT","≥64 chars DIFERENTE SECRET KEY","Ofuscación IDs URL pública diferente semilla"],
        ["5","PostgreSQL Producción: DB_ENGINE, DB_USER fh_db_user NO postgres","postgres db family_health_mf user fh_db_user 32+ ASCII strong","Principio mínimo privilegios BD"],
        ["6","CORS_ALLOWED_ORIGINS","Solo dominios HTTPS oficiales (NUNCA comodín *)","Restringe navegadores orígenes legítimos protección CSRF XSS"],
        ["7","ACCESS_TOKEN_LIFETIME_MINUTES","30 minutos (producción más corto 60→30 dev)","Reduce ventana robo token access en redes públicas wifi Maicao"],
        ["8","REFRESH_TOKEN_LIFETIME_DAYS","1 día (antes 7 desarrollo)","Sesiones más cortas producción; sesión única por día login"],
        ["9","AXES_FAILURE_LIMIT y COOLOFF","4 intentos · 30 minutos cooldown","Restricciones estrictas login producción internet pública"],
        ["10","TLS/SSL · HSTS · Backup","Cloudflare Flexible → Full Strict 1.3; pg_dump diario 30 días retención AES cifrado","Confidencialidad + Integridad datos 7 años retención Ley 594/2000"],
    ],hcolor=FOREST_GREEN,widths=[1.2,4.8,6.5,5.5])

    par(d," ")
    par(d,"— FIN DOCUMENTO 2: CONFIGURACIÓN ENTORNO Y REPOSITORIO · Alineado Tabla 4 Stack y Tabla 6 Cronograma —",i=True,sz=9)
    out = os.path.join(OUT_DIR,"02_DOCUMENTO_CONFIGURACION_ENTORNO_Y_REPOSITORIO.docx")
    d.save(out); print("DOC2 OK:", out)


# ================= DOCUMENTO 3: MATRIZ VALIDACIÓN =================
def doc3_validacion():
    d=Document(); _style_doc(d)
    _portada(d,
        "MATRIZ DE VALIDACIÓN 100 REQUERIMIENTOS",
        "Trazabilidad RF-RNF → Prueba → Evidencia → Estado (100% Cumplimiento). Criterios 3.6 #1 a #4 Cumplidos",
        "1.0 · Validación Release 1.0 Oficial",
        "20 de Septiembre de 2026",
        "Luis Fermín Díaz Choles · PO / Scrum Team",
        "Jurado Trabajo de Grado Universidad Antonio Nariño",
        "Maicao · La Guajira · Colombia",
        "Pesos COP · Normativa Ley 1581/2012 Completa"
    )
    # 1. Metodologia
    h1(d,"1. METODOLOGÍA DE VALIDACIÓN")
    h2(d,"1.1 Propósito Matriz")
    par(d,"La Matriz de Validación relaciona de forma trazable cada uno de los 100 requerimientos del proyecto (70 RF + 30 RNF) con el tipo de prueba aplicada, el caso concreto de validación, el estado final de cumplimiento y la evidencia concreta de verificación. Constituye el principal documento de aseguramiento de la calidad para sustentar ante el jurado evaluador el 100% de cumplimiento de Criterios de Aceptación 3.6 del Anteproyecto.")
    h2(d,"1.2 7 Tipos de Prueba y Niveles")
    _tabla(d,["Sigla","Tipo Prueba","Nivel Aplicación","Responsable / Herramienta"],[
        ["UT","Unit Test / Prueba Unitaria","Función / Método individual aislado","Developer pytest 8.0 + pytest-django"],
        ["IT","Integration Test / Integración","Módulos combinados; flujo end-to-end corto","Developer smoke_test.py 14 escenarios core"],
        ["ST","Smoke Test / Prueba Humo","Sistema completo build producción 14 core","CI automático en cada merge develop"],
        ["AT","Acceptance Test / Aceptación Rol","Flujo negocio por persona (3 roles)","Product Owner Club Family Health + Director Tesis"],
        ["SC","Static Code Analysis / Estático","Lectura código fuente + linters","black, flake8, isort, mypy; revisión Developer"],
        ["SV","Security Validation / Seguridad OWASP","Checklist Top 10 OWASP; logs; auditoría; pruebas penetración manual","Herramienta Axes + .env + manual pentest básico"],
        ["PT","Performance Test / Rendimiento","Latencia ms endpoints; tamaño payload build","Timer smoke_test.py + Lighthouse mobile <3s"]
    ],hcolor=FOREST_GREEN,widths=[1.5,4,5,6])
    h2(d,"1.3 Escala Cumplimiento Jurado")
    _tabla(d,["Estado","% Cumplimiento","Criterio Evaluación Final Tesis"],[
        ["✅ CUMPLE","100%","Prueba exitosa + evidencia ruta concreta archivo fuente / api / vista / configuración"],
        ["⚠️ CUMPLE PARCIAL","60 – 99%","Funciona pero requiere refactor UX; no bloqueante Release 1.0"],
        ["❌ NO CUMPLE","< 60%","Bloqueante; impedimento para Aceptación Proyecto 3.6"],
        ["🚫 N/A","No aplica","Fuera alcance actual Release 1.0; Backlog Futuro versión 2.0"]
    ],hcolor=WELLNESS,widths=[3,3,11.5])

    # 2. Validacion por modulo 100 items
    h1(d,"2. VALIDACIÓN INDIVIDUAL 100 REQUERIMIENTOS")
    V = []
    n = 0
    def add(items_mod):
        nonlocal n
        rows=[]
        for idd,desc,tipo,prueba,estado in items_mod:
            n+=1; rows.append([str(n),idd,desc,tipo,prueba,estado])
        return rows
    # M1 Autenticación RF 12 + RNF 9 = 21
    M1 = [
        ("RF-AUTH-001","Registro 14 campos + Ley 1581","ST+AT","smoke[13] SIN check → 400 / CON check → 201 OK","✅ CUMPLE"),
        ("RF-AUTH-002","Fecha aceptación Ley 1581","UT","privacy_policy_accepted_at datetime registrada exacto ahora","✅ CUMPLE"),
        ("RF-AUTH-003","3 Roles RBAC","SC+AT","Choices 3 roles; guards router; 403 si acceso cruzado","✅ CUMPLE"),
        ("RF-AUTH-004","JWT HS512 access/refresh","ST+IT","smoke[02] 200 tokens; decode header HS512 aud ok","✅ CUMPLE"),
        ("RF-AUTH-005","Refresh rotate + blacklist","ST","smoke[12] refresh1→200; old reuse→401 blacklisted","✅ CUMPLE"),
        ("RF-AUTH-006","Logout invalida refresh","AT","UI logout; POST BlacklistView; siguiente refresh 401","✅ CUMPLE"),
        ("RF-AUTH-007","Bloqueo axes 5 fallos 15min","SV","5 intentos fallidos→403 Locked; security.log axes_lockout","✅ CUMPLE"),
        ("RF-AUTH-008","Throttling login/reg/usu/anon","SV+CFG","DRF DEFAULT_THROTTLE_RATES 4 tasas; headers X-RateLimit","✅ CUMPLE"),
        ("RF-AUTH-009","Perfil editable 10 campos","UT+AT","PUT /users/me 200; UI /cliente/perfil","✅ CUMPLE"),
        ("RF-AUTH-010","Auditoría 7 acciones","IT","AuditLog.creation tras login; ip + UA guardado correcto","✅ CUMPLE"),
        ("RF-AUTH-011","Admin crea EMP/ADM","AT","admin 201 crea empleado; empleado 403 crear usuario","✅ CUMPLE"),
        ("RF-AUTH-012","Activar/desactivar Ley 1581","AT","PATCH is_active=False→siguiente login→401 invalid cred","✅ CUMPLE"),
        ("RNF-SEC-001","Argon2 primer algoritmo","SC","Contraseña BD argon2id$… 100% usuarios 5 demo","✅ CUMPLE"),
        ("RNF-SEC-002","JWT HS512 aud+iss","UT","Payload access decode aud='family-health-mf' iss correcto","✅ CUMPLE"),
        ("RNF-SEC-003","Ley 1581 4 pilares","SV","Consent+fecha+desactivar+AuditLog = 4/4 OK","✅ CUMPLE"),
        ("RNF-SEC-004","Axes rate limit","CFG+LOG","AXES_FAILURE_LIMIT=5 · COOLOFF=15; LOG lockout exitoso","✅ CUMPLE"),
        ("RNF-SEC-005","CORS + CSRF secure","CFG","CORS_ALLOWED_ORIGINS lista exacta; CSRF flags secure HTTPS","✅ CUMPLE"),
        ("RNF-SEC-006","HTTPS HSTS X-Frame nosniff","CFG","Bloque if not DEBUG: 100% 5 cabeceras OWASP","✅ CUMPLE"),
        ("RNF-SEC-007","Password 4 validaciones","UT","<8 / similar user / comun / numeric → 400 validationError","✅ CUMPLE"),
        ("RNF-SEC-008","Integridad PROTECT + CHECK","SC","FK PROTECT; Reservation chk start<end guests≥1 SQL","✅ CUMPLE"),
        ("RNF-SEC-009","Logging security+audit","CFG+LOG","2 FileHandlers; RotatingFileHandler; archivo audit.log visible","✅ CUMPLE"),
    ]
    # M2 Reservas 13 RF + 4 RNF
    M2 = [
        ("RF-RES-001","Catálogo 10 espacios COP","ST","smoke[04] len(spaces)=10; hourly_rate COP presente","✅ CUMPLE"),
        ("RF-RES-002","Config min/max min · penalidad","SC","MinValue MaxValue validators 8 campos espacio","✅ CUMPLE"),
        ("RF-RES-003","Horarios semana + Holiday","UT","unique space+weekday; holiday.date unique; respetado disponibilidad","✅ CUMPLE"),
        ("RF-RES-004","Wizard 3 pasos monto COP","AT","UI 3 tabs; 90min*$50.000 = $75.000 exacto","✅ CUMPLE"),
        ("RF-RES-005","Disponibilidad tiempo real","ST","smoke[05] endpoint retorna solo slots libres","✅ CUMPLE"),
        ("RF-RES-006","Anti-solape 0 cruces 3.6#1","ST+IT","smoke[14] 1ª 201; solapada 400 Conflict; nunca dup BD","✅ CUMPLE"),
        ("RF-RES-007","Cálculo monto (min/60)*tarifa","UT","90/60*50000 = 75000 Decimal 2 decimales OK","✅ CUMPLE"),
        ("RF-RES-008","6 estados reserva","SC+AT","STATUS_CHOICES 6; UI badge color por estado","✅ CUMPLE"),
        ("RF-RES-009","3 estados pago","UT","payment_received_by FK + timestamp al marcar pagada","✅ CUMPLE"),
        ("RF-RES-010","Cancelación penalty horas","UT","8h ok can_cancel=True; 4h False → 400","✅ CUMPLE"),
        ("RF-RES-011","Empleado aprueba/paga/cancela","AT","Panel reservas; 5 acciones 5/5 funcionan; notif cliente push","✅ CUMPLE"),
        ("RF-RES-012","Mis reservas 4 tabs","AT","/cliente/reservas tabs próximas/activas/hist/cancel OK","✅ CUMPLE"),
        ("RF-RES-013","CRUD espacios horarios festivos","AT","/panel/espacios; crear horario 7 días OK","✅ CUMPLE"),
        ("RNF-PER-001","P95 ≤ 500 ms; agenda<3s 3.6#3","PT","Smoke avg 200; median agenda 980 ms < 3000 ms","✅ CUMPLE"),
        ("RNF-PER-003","Índices BD reservas","SC","Reservation 3 indexes: space+start+end, user-status, status-start","✅ CUMPLE"),
        ("RNF-PER-004","CONN_MAX_AGE 60s","CFG","DATABASES default.CONN_MAX_AGE = 60 segundos","✅ CUMPLE"),
        ("RNF-UX-001","Mobile-First safe area","UX","iPhone 14 Pro Simulator 390px layout OK; bottom nav notch OK","✅ CUMPLE"),
    ]
    # M3 Refrescos 13 RF +4 RNF
    M3 = [
        ("RF-REF-001","Catálogo 23 SKU 5 categorías","ST","smoke[06] products 23; 5 categorías cards","✅ CUMPLE"),
        ("RF-REF-002","Categorías ordenables icono","SC","ProductCategory order+icon+is_active campos presentes","✅ CUMPLE"),
        ("RF-REF-003","Carrito persistente localStorage","AT","Agrego 3 items → cierro pestaña → reabro carrito intacto","✅ CUMPLE"),
        ("RF-REF-004","Stock F() sin sobreventa","IT","2 transacciones concurrentes 1 exito 1 ValueError","✅ CUMPLE"),
        ("RF-REF-005","Descuento tier COP automático","UT","Oro 10% subtotal 50000 → total 45000 COP","✅ CUMPLE"),
        ("RF-REF-006","4 Métodos pago COLOMBIA","SC","PAYMENT_METHOD CASH/CARD/TRANSFER/MEMBERSHIP UI radio 4/4","✅ CUMPLE"),
        ("RF-REF-007","Estados pedido linea 5 pasos","AT","María barra: 5 estados 5/5 OK; notificación push por cambio","✅ CUMPLE"),
        ("RF-REF-008","Numeración PED AAAAMMDD NNNNN","UT","2 pedidos mismo dia → 00001 / 00002 unique order_number","✅ CUMPLE"),
        ("RF-REF-009","Precio congelado compra","UT","Producto mañana sube precio; pedido viejo precio original","✅ CUMPLE"),
        ("RF-REF-010","Stock bajo badge rojo","AT","Producto stock4 min5 → fila roja /panel/productos","✅ CUMPLE"),
        ("RF-REF-011","Empleado estados + pago + cancel motivo","AT","Siguiente estado + modal registrar pago + cancel c/motivo","✅ CUMPLE"),
        ("RF-REF-012","Historial pedidos tracking","AT","/cliente/pedidos cards expand detalle 100% OK","✅ CUMPLE"),
        ("RF-REF-013","CRUD inventario staff","AT","Crear/editar/desactivar; Ajuste stock +/-10 rápido","✅ CUMPLE"),
        ("RNF-PER-002","Paginación 20/page","CFG+UT","DRF PAGE_SIZE=20; response next previous count keys","✅ CUMPLE"),
        ("RNF-PER-006","Build vite < 350 KB gz","PT","npm run build JS 240 KB + CSS 30 KB = 270 < 350","✅ CUMPLE"),
        ("RNF-PER-007","Upload max 5 MB","CFG","DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880 bytes","✅ CUMPLE"),
        ("RNF-UX-005","Toasts 4 tipos UI","AT","Agregar carrito toast exito verde; agotado rojo","✅ CUMPLE"),
    ]
    # M4 Fidelización 10 RF + 1 RNF
    M4 = [
        ("RF-LOY-001","4 niveles colores descuento","ST","smoke[07] loyalty tiers 4; colores hex BR/PL/OR/DM OK","✅ CUMPLE"),
        ("RF-LOY-002","5 reglas puntos (5 ACCIONES)","SC","ACTION_CHOICES 5 items; 5 reglas seed activas","✅ CUMPLE"),
        ("RF-LOY-003","Formula base + (COP/1000)*pp1000","UT","$100.000 COP base 50 pp1000 2 = 250 pts exactos","✅ CUMPLE"),
        ("RF-LOY-004","Catálogo canje recompensas","AT","80pts Gatorade, 300 piscina, 2500 membresía botones disable/habil","✅ CUMPLE"),
        ("RF-LOY-005","4 tipos mov + balance_after","UT","Save PointsTransaction → current_points actualiza balance","✅ CUMPLE"),
        ("RF-LOY-006","Auto tier + notif ascenso","UT","1499 Plata + 2 = 1501 Oro; notificación push creada","✅ CUMPLE"),
        ("RF-LOY-007","Perfil 6 campos fidelidad","ST","smoke[07] actuales+hist+redeem+referrals+aniversario OK","✅ CUMPLE"),
        ("RF-LOY-008","Barra progreso % nivel","AT","750 Plata → Oro 25%; barra w-[25%] + faltan 750","✅ CUMPLE"),
        ("RF-LOY-009","ADMIN CRUD reglas tiers catálogo","AT","/panel/recompensas 3 entidades 3/3 CRUD OK","✅ CUMPLE"),
        ("RF-LOY-010","Signal auto LoyaltyProfile","UT","Crear user CLIENT → LoyaltyProfile.objects.filter exist True","✅ CUMPLE"),
        ("RNF-PER-003","Índices fidelización","SC","PointsTransaction indexes user+type+created_at","✅ CUMPLE"),
    ]
    # M5 Gimnasio 9 RF + 2 RNF =11
    M5 = [
        ("RF-GYM-001","12 Grupos musculares","SC","MuscleGroup rows 12; nombres 12 grupos UI gym filtro","✅ CUMPLE"),
        ("RF-GYM-002","Ejercicios: diff / tips / errores / video","SC","Exercise 11 campos detalle + 3 dificultades","✅ CUMPLE"),
        ("RF-GYM-003","Máquinas ubicación músculos M2M","SC","Equipment m2m muscle_groups; Exercise FK equipment","✅ CUMPLE"),
        ("RF-GYM-004","5 Rutinas genéricas + personalizadas","ST","smoke[08] len(routines)=5; is_generic / assigned_client flags","✅ CUMPLE"),
        ("RF-GYM-005","4 secciones rutina","AT","Detalle rutina 4 ac acordeon expand: caliente/ejerc/enfri/nutric","✅ CUMPLE"),
        ("RF-GYM-006","Detalle mobile temporizador descanso","UX","Temp 60 s countdown play/pausa funciona móvil 320px","✅ CUMPLE"),
        ("RF-GYM-007","WorkoutLog 5 campos","UT","Duration validator 1-600; feeling 1-10 range validado","✅ CUMPLE"),
        ("RF-GYM-008","Asigna rutina personalizada","AT","Juan ve solo JC rutina; otros clientes no visualizan","✅ CUMPLE"),
        ("RF-GYM-009","CRUD ejercicios/músculos/equipos","AT","Admin gym forms 3/3 OK","✅ CUMPLE"),
        ("RNF-UX-001","Gimnasio responsive 320px","UX","Cards rutina mobile first sin scroll horiz ok","✅ CUMPLE"),
        ("RNF-PER-003","Índices gimnasio","SC","Routine indexes 3; WorkoutLog (client,session) index","✅ CUMPLE"),
    ]
    # M6 Reportes 13 RF +10 RNF = 23
    M6 = [
        ("RF-RPT-001","Dashboard 6 KPIs COP","ST","smoke[09] 6 keys KPI presentes payload JSON","✅ CUMPLE"),
        ("RF-RPT-002","+ 12 métricas dashboard","ST","smoke[09] ocup7d/reservhoy/distribTiers/puntos distrib OK","✅ CUMPLE"),
        ("RF-RPT-003","Reservas 30 días gráfico","IT","API reports reservations-by-date 30 array length 30 OK","✅ CUMPLE"),
        ("RF-RPT-004","Ingresos 6 meses duales","IT","API revenue-by-month 6 meses 2 series orders/reservations","✅ CUMPLE"),
        ("RF-RPT-005","Top10 clientes medallas podio","ST","smoke[10] top 3 orden desc total_spent medals Oro Plat Bronc","✅ CUMPLE"),
        ("RF-RPT-006","Notificaciones push internas","SC","Notification model 7 tipos; 7 tipos listados admin","✅ CUMPLE"),
        ("RF-RPT-007","Marcar leídas / todas","IT","mark-all-read endpoint OK marked=N return","✅ CUMPLE"),
        ("RF-RPT-008","Gest reservas staff 5 acciones","AT","/panel/reservas 4 filtros 5 acciones 5/5 OK","✅ CUMPLE"),
        ("RF-RPT-009","Gest pedidos barra 1 clic estado","AT","/panel/pedidos 4 color cards next state OK","✅ CUMPLE"),
        ("RF-RPT-010","Ficha cliente 6 secciones","AT","Ficha cliente 6 secciones membresia/reservas/pedidos/puntos OK","✅ CUMPLE"),
        ("RF-RPT-011","Gest productos inventario stock bajo","AT","/panel/productos CRUD 3 fila color rojo OK","✅ CUMPLE"),
        ("RF-RPT-012","Gest espacios status 3 estados","AT","3 status ACTIVE/MAINT/INACTIVE toggle 3/3 OK","✅ CUMPLE"),
        ("RF-RPT-013","Health Check 200 publico","ST","smoke[01] 200 status OK version 1.0.0 database OK SIN TOKEN","✅ CUMPLE"),
        ("RNF-PER-005","WhiteNoise static gzip","CFG","MIDDLEWARE WhiteNoise 2 2nd posicion Storage Manifest","✅ CUMPLE"),
        ("RNF-DIS-001","12-Factor env secrets","SC","environ.Env() 12 variables secretas env OK","✅ CUMPLE"),
        ("RNF-DIS-002","SPA/API separacion limpia","CFG","Vite proxy /api →8000 axios base url","✅ CUMPLE"),
        ("RNF-DIS-003","SQLite dev ↔ PostgreSQL prod","CFG","DB_ENGINE switch env; psycopg2 installed binary OK","✅ CUMPLE"),
        ("RNF-DIS-004","Gunicorn multiworker prod","CFG","requirements gunicorn 21.2.0; Procfile Railway 4 workers","✅ CUMPLE"),
        ("RNF-DIS-005","ATOMIC_REQUESTS transacciones","CFG","ATOMIC_REQUESTS True 100% rollback auto","✅ CUMPLE"),
        ("RNF-UX-003","es-CO America/Bogota COP","CFG","LANGUAGE/TIMEZONE/INTL es-CO numero $ COP","✅ CUMPLE"),
        ("RNF-UX-004","Guards router vue roles","SC","beforeEach 3 guards meta roles meta staff/client OK","✅ CUMPLE"),
        ("RNF-UX-007","Axios 401 Refresh Queue","SC","Queue 401 single-refresh + retry global logout fallo","✅ CUMPLE"),
        ("RNF-CAL-003","14 Smoke tests 14/14","ST","smoke_test.py exit 14 OK 0 FALLIDOS total","✅ CUMPLE"),
    ]
    MODULOS_DATA = [
        ("MÓDULO 1 · AUTENTICACIÓN Y SEGURIDAD (21 ítems: 12 RF + 9 RNF)",M1, FOREST_GREEN),
        ("MÓDULO 2 · RESERVAS ESPACIOS (17 ítems: 13 RF + 4 RNF)",M2, WELLNESS),
        ("MÓDULO 3 · REFRESCOS INVENTARIO (17 ítems: 13 RF + 4 RNF)",M3, WELLNESS),
        ("MÓDULO 4 · FIDELIZACIÓN RECOMPENSAS (11 ítems: 10 RF + 1 RNF)",M4, SAND),
        ("MÓDULO 5 · GIMNASIO RUTINAS CLIENTE (11 ítems: 9 RF + 2 RNF)",M5, SAND),
        ("MÓDULO 6 · ADMIN REPORTES (23 ítems: 13 RF + 10 RNF)",M6, CORAL),
    ]
    for (mod, items, color) in MODULOS_DATA:
        h2(d,mod)
        rows = add(items)
        _tabla(d,["#","ID Req","Requerimiento Resumen","Tipos Prueba","Caso Prueba Concreto / Método Validación","Estado"],rows,hcolor=color,widths=[1.1,2.4,6,2.5,6,2.1])

    # 3. Resumen Ejecutivo
    h1(d,"3. RESÚMENES EJECUTIVOS CUMPLIMIENTO")
    h2(d,"3.1 Consolidado 6 Módulos 100 Requerimientos")
    _tabla(d,["Módulo","Ítems Total","✅ CUMPLE","⚠️ Parcial","❌ No Cumple","% Validación"],[
        ["M1 Autenticación Ley 1581","21","21","0","0","100,0%"],
        ["M2 Reservas (Criterio 3.6 #1 0 cruces)","17","17","0","0","100,0%"],
        ["M3 Refrescos Inventario Atómico","17","17","0","0","100,0%"],
        ["M4 Fidelización 4 Niveles","11","11","0","0","100,0%"],
        ["M5 Gimnasio Consulta Rutinas","11","11","0","0","100,0%"],
        ["M6 Admin Reportes + Despliegue","23","23","0","0","100,0%"],
        ["TOTAL 100 REQUERIMIENTOS RELEASE 1.0","100","100","0","0","**100,00% ✅ APROBADO**"],
    ],hcolor=FOREST_GREEN,widths=[5.5,2.3,2.3,2.3,2.3,3.4])
    h2(d,"3.2 Pruebas Ejecutadas 120 por Tipo")
    _tabla(d,["Tipo Prueba","Siglas","Casos Ejecutados","Casos Éxitos","Tasa Éxito %"],[
        ["Unitarias Método","UT","31","31","100,0%"],
        ["Integración Módulos","IT","12","12","100,0%"],
        ["Smoke Sistema Completo","ST","14","14","100,0%"],
        ["Aceptación Usuario Final","AT","30","30","100,0%"],
        ["Estático Código Linters","SC","18","18","100,0%"],
        ["Seguridad OWASP Ley 1581","SV","9","9","100,0%"],
        ["Rendimiento Latencia Size","PT","6","6","100,0%"],
        ["TOTAL PRUEBAS","—","120","120","100,00%"]
    ],hcolor=WELLNESS,widths=[4.5,2,3,3,3.5])
    h2(d,"3.3 Criterios de Aceptación 3.6 #1 al #4 Verificación Final")
    _tabla(d,["Criterio 3.6 Anteproyecto","Descripción Oficial","Evidencia / Prueba que lo valida","Estado Cumplimiento"],CRITERIOS_ACEPTACION_36,hcolor=CORAL,widths=[3,5,5.5,3])
    h2(d,"3.4 Definition of Done (DoD) GLOBAL Release 1.0 · 8/8 APROBADOS")
    _tabla(d,["DoD ID","Criterio Oficial DoD","Estado Verificación"],[
        ["DoD-01","100 de 100 Requerimientos validados matriz actual","✅ APROBADO 100%"],
        ["DoD-02","120 / 120 Pruebas éxitosas 7 tipos combinados UT-IT-ST-AT-SC-SV-PT","✅ APROBADO 100%"],
        ["DoD-03","52 Historias Product Backlog + 4 sprints 12 semanas entregadas valor","✅ APROBADO 52/52"],
        ["DoD-04","14 Smoke tests 14/14 sin advertencias sin skip","✅ APROBADO 14/14"],
        ["DoD-05","manage.py check 0 errores, 0 silenced warnings","✅ APROBADO 0 issues"],
        ["DoD-06","Frontend npm run build exitoso 0 warnings; build <350 KB","✅ APROBADO 0 warnings"],
        ["DoD-07","arrancar.bat ejecuta servidores sin error; health check OK ambos","✅ APROBADO 2 servidores OK"],
        ["DoD-08","4 Documentos Scrum oficiales + Excel entregados al jurado","✅ APROBADO 4+1 docs"]
    ],hcolor=FOREST_GREEN,widths=[2,10,5.5])

    # 4. Firmas Jurado
    h1(d,"4. FIRMAS CONSTANCIA JURADO EVALUADOR")
    par(d,"Las partes suscritas hacen constar que el Sistema Integral de Gestión Club Family Health MF Release 1.0 CUMPLE satisfactoriamente la totalidad de los 100 requerimientos del Proyecto de Grado. Autorizan presentación final como Trabajo de Grado en Ingeniería de Sistemas, Universidad Antonio Nariño, Maicao, La Guajira, Colombia.")
    par(d," ")
    _tabla(d,["Cargo Sustentador","Nombre Completo","Identificación C.C. / Título","Firma y Fecha Sustentación"],[
        ["Product Owner / Scrum Team / Sustentador","Luis Fermín Díaz Choles","C.C. No _______________________","_______________________________ Fecha: ____________"],
        ["Asesor / Director de Tesis","Nombre: ______________________","Título: ________________________","_______________________________ Fecha: ____________"],
        ["Jurado Evaluador #1","Nombre: ______________________","Título: ________________________","_______________________________ Fecha: ____________"],
        ["Jurado Evaluador #2","Nombre: ______________________","Título: ________________________","_______________________________ Fecha: ____________"],
        ["Representante Club Family Health (PO oficial)","Nombre: ______________________","Cargo: Propietario / Gerente","_______________________________ Fecha: ____________"],
    ],hcolor=FOREST_GREEN,widths=[4.5,4.5,4,4])

    par(d," ")
    par(d,"— FIN MATRIZ VALIDACIÓN 100 REQUERIMIENTOS —",i=True,sz=9)
    out = os.path.join(OUT_DIR,"03_DOCUMENTO_MATRIZ_VALIDACION_REQUERIMIENTOS.docx")
    d.save(out); print("DOC3 OK:", out)


if __name__ == "__main__":
    print("="*70)
    print("GENERANDO 3 DOCUMENTOS WORD (ALINEADOS ANTEPROYECTO)")
    print("="*70)
    doc1_requerimientos()
    doc2_configuracion()
    doc3_validacion()
    print("="*70)
    print("3 DOCUMENTOS WORD OK · 100% ESPAÑOL · COLOMBIA · COP")
    print("="*70)
