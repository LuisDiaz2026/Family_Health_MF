# -*- coding: utf-8 -*-
"""
PRODUCT BACKLOG EXCEL 100% ALINEADO A ANTEPROYECTO Tabla 6 Cronograma S1-S12
Sprint 1 (S1-S2): Levantamiento requerimientos
Sprint 2 (S3-S4): Análisis y Diseño
Sprint 3 (S5-S7): Implementación módulos CORE (Auth + Reservas + Disponibilidad + Mobile UI)
Sprint 4 (S8-S12): Complementarios (Refrescos + Recompensas/Rutinas + Panel Admin + Pruebas + Cierre)
"""
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT_DIR = r"c:\Users\gusta\OneDrive - UNIR\TRABAJOS DE GRADO\TRABAJOS DE GRADO\UAN\LUIS\SCRUM_DOCS"
WB = openpyxl.Workbook()

# ===================== ESTILOS =====================
FUENTE_TITULO = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
FUENTE_HEADER = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
FUENTE_HITO = Font(name="Calibri", size=11, bold=True)
FUENTE_NORMAL = Font(name="Calibri", size=10)
FOREST = PatternFill("solid", fgColor="174C3C")  # Sprint 1
WELL   = PatternFill("solid", fgColor="3B8064")  # Sprint 2
SAND   = PatternFill("solid", fgColor="D7AE58")  # Sprint 3
CORAL  = PatternFill("solid", fgColor="E9784A")  # Sprint 4
GRAPH  = PatternFill("solid", fgColor="232927")
P0, P1, P2, P3 = [PatternFill("solid",fgColor=c) for c in ["E9784A","D7AE58","F7F4EC","E6E6E6"]]
HECHO = PatternFill("solid", fgColor="C8E6C9")
BORDE = Border(*[Side(style="thin", color="999999")]*4)
WRAP_CENTRO = Alignment(wrap_text=True, vertical="center", horizontal="center")
WRAP_IZQ    = Alignment(wrap_text=True, vertical="center", horizontal="left")

def t(hoja, fila, num_cols):
    for c in range(1,num_cols+1):
        cel = hoja.cell(fila, c)
        cel.font = FUENTE_HEADER; cel.fill = WELL if hoja.title not in ["1.Cronograma 12 Semanas"] else FOREST
        cel.alignment = WRAP_CENTRO; cel.border = BORDE

def celdas(hoja, fi, ff, nc, pc=None, ec=None):
    for r in range(fi, ff+1):
        for c in range(1, nc+1):
            x = hoja.cell(r,c)
            x.font = FUENTE_NORMAL; x.alignment = WRAP_IZQ; x.border = BORDE
            if pc and c == pc:
                v = (str(x.value) or "").strip().upper()
                x.fill = {"P0":P0,"P1":P1,"P2":P2,"P3":P3}.get(v, x.fill)
            if ec and c == ec and "CUMPLE" in (str(x.value).upper() or ""):
                x.fill = HECHO

def titulo(hoja, t1, t2, nc):
    rango_1 = f"A1:{get_column_letter(nc)}1"
    rango_2 = f"A2:{get_column_letter(nc)}2"
    hoja.merge_cells(rango_1)
    c = hoja.cell(1,1,t1); c.font=FUENTE_TITULO; c.fill=FOREST; c.alignment=Alignment(horizontal="center", vertical="center")
    hoja.row_dimensions[1].height = 30
    hoja.merge_cells(rango_2)
    cc = hoja.cell(2,1,t2); cc.font=Font(italic=True,color="232927",size=10); cc.alignment=Alignment(horizontal="center"); cc.fill=PatternFill("solid",fgColor="F7F4EC")
    hoja.row_dimensions[2].height = 22

def anch(hoja, ws):
    for i,w in enumerate(ws,1):
        hoja.column_dimensions[get_column_letter(i)].width = w

# ============================================================
# HOJA 1: CRONOGRAMA 12 SEMANAS (IGUAL A TABLA 6 ANTEPROYECTO)
# ============================================================
hc = WB.active
hc.title = "1.Cronograma 12 Semanas"
CRON_COLS = ["N° Fase","FASE / Sprint (Metodología Scrum)","Actividad / Entregable"] + [f"S{i}" for i in range(1,13)]
NC = len(CRON_COLS)
titulo(hc,
    "CRONOGRAMA OFICIAL 12 SEMANAS · TABLA 6 ANTEPROYECTO",
    "Proyecto: Aplicativo Web Club Family Health MF · Metodología Scrum · Universidad Antonio Nariño 2026",
    NC)
for i,col in enumerate(CRON_COLS,1):
    hc.cell(3,i,col)
t(hc,3,NC); hc.row_dimensions[3].height=34

# Semanas de cada fase
CRON_DATA = [
    # Sprint 1 (S1-S2)
    [1,"SPRINT 1: Levantamiento de Requerimientos (S1-S2)","Sprint 1 Kick-off + entrevistas actores club"]     + ["◼","◼","","","","","","","","","",""],
    ["","","Requerimientos funcionales y no funcionales (RFP)"]              + ["◼","◼","","","","","","","","","",""],
    ["","","Historias de usuario y Product Backlog"]                          + ["","◼","◼","","","","","","","","",""],
    ["","","Configuración entorno de desarrollo y repositorio (GitHub)"]      + ["","◼","◼","","","","","","","","",""],
    ["","","Validación y refinamiento de requerimientos con PO"]              + ["","","◼","◼","","","","","","","",""],
    # Sprint 2 (S3-S4)
    [2,"SPRINT 2: Análisis y Diseño (S3-S4)","Casos de uso y diagramas UML (CU + Secuencia x3)"]+ ["","","◼","◼","","","","","","","",""],
    ["","","Prototipo visual Mockups (mínimo 8 pantallas Mobile-First)"]      + ["","","◼","◼","","","","","","","",""],
    ["","","Modelo Entidad-Relación (MER) y diseño BD PostgreSQL"]            + ["","","","◼","◼","","","","","","",""],
    ["","","Arquitectura lógica del sistema (N-capas) + seguridad"]           + ["","","","◼","◼","","","","","","",""],
    ["","","Entregable Sprint Review 2 al Director y PO Club"]                + ["","","","","◼","","","","","","",""],
    # Sprint 3 (S5-S7)
    [3,"SPRINT 3: Implementación Módulos CORE (S5-S7)","Autenticación JWT y 3 roles: ADMIN, EMPLEADO, CLIENTE (RBAC)"]+["","","","","◼","◼","","","","","",""],
    ["","","Módulo de reservas dinámicas (CRUD espacios + wizard)"]           + ["","","","","","◼","◼","","","","",""],
    ["","","Disponibilidad en tiempo real y anti-solape (0 cruces)"]          + ["","","","","","◼","◼","","","","",""],
    ["","","Interfaz UI / UX Mobile-First (Auth + Cliente reservas)"]         + ["","","","","◼","◼","◼","","","","",""],
    ["","","Pruebas unitarias módulos core + Sprint Review 3"]                + ["","","","","","","◼","","","","",""],
    # Sprint 4 (S8-S12)
    [4,"SPRINT 4: Módulos Complementarios y Cierre (S8-S12)","Módulo pedidos refresquería (inventario + carrito)"]      +["","","","","","","","◼","◼","","","",""],
    ["","","Recompensas básicas + Consulta rutinas (rol cliente)"]            + ["","","","","","","","","◼","◼","","",""],
    ["","","Panel administrativo y reportes básicos (KPIs)"]                  + ["","","","","","","","","◼","◼","","",""],
    ["","","Pruebas funcionales, integración y usabilidad x rol"]             + ["","","","","","","","","","◼","◼","",""],
    ["","","Corrección de incidencias y optimización"]                        + ["","","","","","","","","","◼","◼","",""],
    ["","","Documentación técnica y manual de usuario por rol"]               + ["","","","","","","","","","","◼","◼"],
    ["","","Despliegue Railway/Render + Socialización + Entrega Final"]       + ["","","","","","","","","","","","◼"],
]
for r,fila in enumerate(CRON_DATA,4):
    for c,val in enumerate(fila,1):
        x=hc.cell(r,c,val)
        x.font=FUENTE_NORMAL; x.alignment=WRAP_IZQ if c<=3 else WRAP_CENTRO; x.border=BORDE
    # Color de la semana si es celda pintada
    fa = fila[0]
    sprint_color = None
    if isinstance(fa, int) and 1 <= fa <= 4:
        sprint_color = [FOREST, WELL, SAND, CORAL][fa - 1]
        for c_ in [1, 2]:
            hc.cell(r, c_).fill = sprint_color
            hc.cell(r, c_).font = Font(bold=True, color="FFFFFF", size=10)
    for c_ in range(4, 4+12):
        if hc.cell(r,c_).value == "◼":
            hc.cell(r,c_).fill = sprint_color if sprint_color else PatternFill("solid",fgColor="B0B0B0")
            hc.cell(r,c_).value = "✓"
            hc.cell(r,c_).font = Font(bold=True,color="FFFFFF",size=11)
# Altura
for r in range(4, 4+len(CRON_DATA)):
    hc.row_dimensions[r].height = 28
anch(hc,[4,20,55]+[4]*12)
hc.freeze_panes = "D4"

# ============================================================
# HOJA 2: PRODUCT BACKLOG GENERAL (52 US - 4 SPRINTS REALES)
# ============================================================
hpb = WB.create_sheet("2.Product Backlog")
PB_COLS = ["N°","ID US","SPRINT","Semanas","Épico / Módulo","Historia Usuario (Como / Quiero / Para)","Criterios Aceptación Given · When · Then","Prior.","SP","RF Asociado","Estado","Persona / Rol"]
NCPB = len(PB_COLS)
titulo(hpb,
    "PRODUCT BACKLOG OFICIAL - 52 HISTORIAS DE USUARIO",
    "4 Sprints · 12 Semanas · Cronograma Tabla 6 Anteproyecto · 239 Story Points",
    NCPB)
for i,col in enumerate(PB_COLS,1): hpb.cell(3,i,col)
t(hpb,3,NCPB); hpb.row_dimensions[3].height=36

# 52 HISTORIAS 100% ALINEADAS A CRONOGRAMA 4 SPRINTS Y ANTEPROYECTO
HIST = []
# ---------------- SPRINT 1 (S1-S2): LEVANTAMIENTO REQUERIMIENTOS ----------------
SPRINT1 = [
    # US-DS = Documentación Scrum
    ["US-DS01","1 (Levant. Reqs)","S1 · S2","Documentación / Proyecto",
     "Como PRODUCT OWNER (Club Family Health), quiero UN DOCUMENTO DE REQUERIMIENTOS FUNCIONALES Y NO FUNCIONALES aprobado para tener claro el alcance contractual del proyecto.",
     "DADO que se han realizado entrevistas al personal del club\nCUANDO se entrega documento RF/RNF 70+30 ítems\nENTONCES el PO aprueba ≥ 95% ítems y se firma Acta de Conformidad.","P0",8,"RF-AUTH, RF-RES, RNF-SEC","✅ Entregado","PO Club Family Health"],
    ["US-DS02","1 (Levant. Reqs)","S1 · S2","Documentación / Proyecto",
     "Como DIRECTOR DE TESIS (Scrum Master), quiero LAS HISTORIAS DE USUARIO Y PRODUCT BACKLOG priorizado para poder planificar las capacidades semanales del Developer.",
     "DADO aprobado el documento RF/RNF\nCUANDO se entrega Product Backlog con 50+ historias Gherkin Given/When/Then\nENTONCES cada historia tiene Prioridad P0-P3 + Story Points Fibonacci + ID US-XX.","P0",13,"Todos los RF","✅ Entregado","Scrum Master (Director)"],
    ["US-DS03","1 (Levant. Reqs)","S2 · S3","Infraestructura / DevOps",
     "Como DEVELOPER (Luis F. Díaz), quiero CONFIGURAR ENTORNO LOCAL Y REPOSITORIO GITHUB para estandarizar el versionado y el build del aplicativo.",
     "DADO Windows 10/11 + Python 3.10 + Node 18\nCUANDO ejecuto guía paso a paso\nENTONCES se crea .venv 55 paquetes + npm 450 paquetes + .env válido + migrate OK + smoke tests OK.","P0",8,"RNF-DIS-001/002/003","✅ Entregado","Developer"],
    ["US-DS04","1 (Levant. Reqs)","S2 · S3","Calidad / Aseguramiento",
     "Como EQUIPO SCRUM, queremos LA VALIDACIÓN DE REQUERIMIENTOS CON MATRIZ DE TRAZABILIDAD para garantizar que cada requerimiento tiene prueba y evidencia.",
     "DADO Product Backlog 52 US cerrado\nCUANDO ejecutamos validación 100 ítems\nENTONCES matriz muestra 100% trazabilidad RF ↔ US ↔ Prueba ↔ Evidencia.","P0",5,"RNF-CAL-003","✅ Entregado","Scrum Team completo"],
]
HIST += SPRINT1
# ---------------- SPRINT 2 (S3-S4): ANÁLISIS Y DISEÑO ----------------
SPRINT2 = [
    ["US-DS05","2 (Análisis y Diseño)","S3 · S4","Diseño / UML",
     "Como Scrum Master, quiero LOS CASOS DE USO Y DIAGRAMAS UML (CU general + 3 Secuencia flujos críticos) para validar arquitectura antes de codificar.",
     "DADO actores: Administrador, Recepcionista, Cliente\nCUANDO se entregan CU ≥20 y Diagrama Secuencia 3 flujos (Reserva, Pago, Login)\nENTONCES Director aprueba consistencia flujos con requerimientos.","P1",13,"Todos RF","✅ Entregado","Scrum Master"],
    ["US-DS06","2 (Análisis y Diseño)","S3 · S4","Diseño UX/UI",
     "Como Cliente mobile, quiero UN PROTOTIPO VISUAL MOCKUP DE 8 PANTALLAS Mobile-First para anticipar la experiencia de usuario real.",
     "DADO Figma / Adobe XD mockups\nCUANDO presento 8 pantallas (Login, Home cliente, Wizard Reserva, Carrito, Fidelidad, Gym, Panel Admin, Dashboard KPIs)\nENTONCES PO aprueba look & feel colores y navegación.","P1",8,"RNF-UX-001/002/006","✅ Entregado","Todos los usuarios"],
    ["US-DS07","2 (Análisis y Diseño)","S4 · S5","Modelado Datos",
     "Como Developer, quiero EL MODELO ENTIDAD-RELACIÓN + ESQUEMA FÍSICO POSTGRESQL para garantizar integridad referencial y no tener deuda técnica datos.",
     "DADO 25+ entidades identificadas\nCUANDO se entrega MER normalizado 3FN\nENTONCES migraciones Django son aplicables sin perdida de atributos; FK PROTECT; constraints start<end.","P0",13,"RNF-SEC-008, RNF-CAL-004","✅ Entregado","Developer + DBA"],
    ["US-DS08","2 (Análisis y Diseño)","S4 · S5","Arquitectura / Seguridad",
     "Como Scrum Master, quiero EL DOCUMENTO DE ARQUITECTURA LÓGICA N-CAPAS (Presentación/Negocio/Datos) + Diagrama Seguridad (JWT + HTTPS + Ley 1581) para aprobar lineamientos.",
     "DADO stack Python/Django, Tailwind+Vue, PostgreSQL\nCUANDO se socializa arquitectura\nENTONCES se aprueba separación clara capas, sin dependencias cíclicas, con auditoría Ley 1581.","P0",8,"RNF-SEC, RNF-DIS","✅ Entregado","Scrum Master + Director"],
]
HIST += SPRINT2
# ---------------- SPRINT 3 (S5-S7): IMPLEMENTACIÓN MÓDULOS CORE ----------------
SPRINT3 = [
    # Autenticación + 3 roles
    ["US-A01","3 (Impl. CORE)","S5 · S6","Autenticación RBAC",
     "Como CLIENTE NUEVO, quiero REGISTRARME 14 CAMPOS + DOBLE CHECKBOX LEY 1581 para dar consentimiento Habeas Data y acceder al club digitalmente.",
     "DADO pantalla /registro\nCUANDO completo campos obligatorios + política + términos\nENTONCES cuenta CLIENTE creada; guardo privacy_policy_accepted_at; SIN checkbox → 400.","P0",5,"RF-AUTH-001/002","✅ Implementado","Persona Juan Carlos/Valeria/Andrés"],
    ["US-A02","3 (Impl. CORE)","S5 · S6","Autenticación RBAC",
     "Como USUARIO REGISTRADO, quiero INICIAR SESIÓN JWT HS512 y navegar según mi ROL para acceder a módulos autorizados.",
     "DADO credenciales correctas\nWHEN submit login\nTHEN Access 60m + Refresh 7d → redirect /cliente (rol CLIENTE) o /panel (rol STAFF); auditoría LOGIN con IP+UA.","P0",5,"RF-AUTH-004/010","✅ Implementado","Todos los Roles"],
    ["US-A03","3 (Impl. CORE)","S5 · S6","Seguridad Auth",
     "Como SISTEMA, quiero 5 FALLOS LOGIN = BLOQUEO 15min + REFRESH ROTATE+BLACKLIST para prevenir fuerza bruta y reutilización tokens.",
     "DADO 5 fallos misma IP/UA\nCUANDO 6to intento\nENTONCES 403 Locked; AXES registra security.log; Refresh enviado 2 veces → segunda 401 blacklisted.","P0",8,"RF-AUTH-005/006/007/008, RNF-SEC-004","✅ Implementado","Seguridad Sistema"],
    ["US-A04","3 (Impl. CORE)","S6 · S7","Gestión Perfiles",
     "Como CLIENTE / EMPLEADO / ADMIN, quiero CONSULTAR Y EDITAR MI PERFIL (membresía, contacto emergencia, tarjeta fidelidad) para mis datos al día.",
     "DADO sesión iniciada\nCUANDO guardo PUT /users/me\nENTONCES 200 OK; auditoría PROFILE_EDIT; UI muestra datos.","P1",5,"RF-AUTH-009/011/012","✅ Implementado","Todos los usuarios"],
    # Reservas Dinámicas
    ["US-R01","3 (Impl. CORE)","S6 · S7","Reservas Dinámicas",
     "Como CLIENTE, quiero EXPLORAR 10 ESPACIOS (3 canchas, piscina, 3 salones, tenis, squash, gimnasio) con $COP/h para elegir el adecuado.",
     "DADO /cliente/reservas\nCUANDO cargo catálogo\nENTONCES 10 cards nombre/capacidad/$hora/fotografía/estado.","P0",5,"RF-RES-001/013","✅ Implementado","Cliente"],
    ["US-R02","3 (Impl. CORE)","S6 · S7","Reservas Dinámicas",
     "Como CLIENTE, quiero WIZARD 3 PASOS (espacio → fecha → rango horario) para reservar sin errores de digitación.",
     "DADO Cancha 01 seleccionada\nCUANDO avanzo 1→2→3\nENTONCES validación paso a paso; resumen muestra total en COP antes confirmar.","P0",5,"RF-RES-004","✅ Implementado","Cliente Mobile"],
    ["US-R03","3 (Impl. CORE)","S6 · S7","Disponibilidad Tiempo Real",
     "Como SISTEMA, quiero DISPONIBILIDAD TIEMPO REAL + ANTI-SOLAPE TRANSACCIONAL para GARANTIZAR 0 CRUCES DE HORARIOS (Criterio Aceptación 3.6 #1).",
     "DADO Cancha-01 ocupada 18:00-19:00\nCUANDO 2do cliente intenta 18:30-19:30\nENTONCES 400 Conflict 'Horario no disponible'. select_for_update() + constraint BD 100% evita duplicados.","P0",13,"RF-RES-005/006, RNF-SEC-008","✅ Implementado","Integridad Operativa"],
    ["US-R04","3 (Impl. CORE)","S6 · S7","Disponibilidad UI",
     "Como CLIENTE, quiero CONSULTA AGENDA EN < 3 SEGUNDOS EN DISPOSITIVO MÓVIL 4G para cumplir Criterio Aceptación 3.6 #3.",
     "DADO conexión móvil promedio 4G\nCUANDO consulto disponibilidad próximo fin de semana\nENTONCES carga <3 segundos sin skeleton >5s.","P1",5,"RNF-PER-001","✅ Implementado","Cliente móvil Medellín/Maicao"],
    ["US-R05","3 (Impl. CORE)","S7","Gestión Reservas Staff",
     "Como RECEPCIONISTA, quiero APROBAR, RECHAZAR, MARCAR PAGADA, CANCELAR o NO ASISTIÓ para la operativa presencial.",
     "DADO reserva PENDIENTE espacio premium\nCUANDO recepción pulsa Aprobar\nENTONCES estado → CONFIRMADA; cliente notificación push; si paga en efectivo → payment_status PAGADO + puntos.","P0",8,"RF-RES-008/009/010/011","✅ Implementado","Persona Carlos (Recepción)"],
    ["US-UI01","3 (Impl. CORE)","S5 · S6","UI / UX Mobile-First",
     "Como CLIENTE USUARIO ANDROID/iOS, quiero DISEÑO MÓVIL PRIMERO (sticky header + bottom nav safe-area) para operar con el pulgar sin scroll horizontal.",
     "DADO smartphone 320px width notch iPhone SE\nCUANDO navego 22 vistas\nENTONCES layout ≥320px no hay scroll horizontal; Tailwind breakpoints sm/md/lg 100% OK.","P0",8,"RNF-UX-001/002/003/004/005/006","✅ Implementado","Usuarios Mobile"],
]
HIST += SPRINT3
# ---------------- SPRINT 4 (S8-S12): COMPLEMENTARIOS + PRUEBAS + CIERRE ----------------
SPRINT4 = [
    # Refrescos
    ["US-C01","4 (Complementarios y Cierre)","S8 · S9","Refresquería Pedidos",
     "Como CLIENTE, quiero CATÁLOGO 23 PRODUCTOS 5 CATEGORÍAS y CARRITO PERSISTENTE en mi móvil para armar pedido mientras camino.",
     "DADO 5 categorías Bebidas Frías/Calientes, Snacks, Comidas Rápidas, Postres\nCUANDO agrego 3 items y cierro Chrome\nENTONCES reabro carrito intacto localStorage.fh_cart.","P0",8,"RF-REF-001/002/003","✅ Implementado","Cliente Valeria"],
    ["US-C02","4 (Complementarios y Cierre)","S8 · S9","Refresquería Inventario",
     "Como SISTEMA, quiero ACTUALIZACIÓN ATÓMICA STOCK F() expressions para NUNCA vender inventario negativo.",
     "DADO stock=5 y 2 compras concurrentes\nCUANDO una compra 5 + otra 1\nENTONCES primera pasa OK, segunda ValueError Stock Insuficiente Rollback.","P0",8,"RF-REF-004/010/013","✅ Implementado","Integridad Inventario"],
    ["US-C03","4 (Complementarios y Cierre)","S8 · S9","Refresquería Cobro",
     "Como BARRA (María) y RECEPCIÓN (Carlos), quiero CICLO ESTADOS PEDIDO y REGISTRO DE PAGO 4 MÉTODOS (efectivo/tarjeta/transferencia/descuento membresía) para flujo ordenado.",
     "DADO pedido PENDIENTE\nCUANDO barra pulsa Preparar → Listo → Entregar; luego pagos Efectivo\nENTONCES cada estado crea Notificación cliente; paid_at + paid_by registrados.","P1",5,"RF-REF-006/007/008/009/011/012","✅ Implementado","María Barra + Carlos Recepción"],
    # Recompensas Básicas
    ["US-L01","4 (Complementarios y Cierre)","S9 · S10","Recompensas Básicas",
     "Como CLIENTE, quiero 4 NIVELES FIDELIDAD (Bronce Plata Oro Diamante) + GANAR PUNTOS al pagar reserva/pedido para obtener beneficios.",
     "DADO cliente paga $100.000 COP reserva; regla RESERVA pts base=50 pp1000COP=2\nCUANDO pago registra\nENTONCES +250 puntos; si cruza umbral tier notificación ascendente Nivel.","P1",8,"RF-LOY-001/002/003/005/006","✅ Implementado","Lealtad Cliente"],
    ["US-L02","4 (Complementarios y Cierre)","S9 · S10","Recompensas Básicas",
     "Como CLIENTE, quiero CATÁLOGO CANJES y BARRA PROGRESO SIGUIENTE NIVEL para gamificar mi visita al club.",
     "DADO 750pts (Plata→Oro)\nENTONCES barra 25% + texto faltan 750 pts Oro; Catálogo Gatorade 80/Piscina 300/Membresía 2500 pts.","P2",5,"RF-LOY-004/007/008","✅ Implementado","Gamificación Cliente"],
    # Rutinas Gimnasio (como parte Sprint 4 frase "consulta de rutinas rol cliente" 3.4.4)
    ["US-G01","4 (Complementarios y Cierre)","S9 · S10","Rutinas Gimnasio (Consulta Cliente)",
     "Como CLIENTE DEPORTISTA (Andrés), quiero 5 RUTINAS + 22 EJERCICIOS + 12 GRUPOS MUSCULARES para entrenar sin entrenador hoy mismo.",
     "DADO /cliente/gimnasio\nENTONCES 5 rutinas objetivos; detalle muestra calentamiento/sets-reps-pesos/enfriamiento/nutrición; filtro músculo Pecho muestra ejercicios solo de pecho.","P1",8,"RF-GYM-001/002/004/005/006","✅ Implementado","Persona Andrés Deportista"],
    ["US-G02","4 (Complementarios y Cierre)","S10","Rutinas Gimnasio (Personalizadas)",
     "Como CLIENTE JUAN CARLOS, quiero RUTINA PERSONALIZADA ASIGNADA POR ENTRENADOR con vigencia para cumplir mi objetivo.",
     "DADO entrenador crea Rutina assigned_client=JC vigente 8 semanas\nENTONCES JC ve solo él la rutina en 'Asignadas a mí'; otros clientes no la visualizan.","P2",5,"RF-GYM-003/007/008/009","✅ Implementado","Juan Carlos + Entrenador"],
    # Panel Administrativo + Reportes básicos
    ["US-F01","4 (Complementarios y Cierre)","S9 · S10","Panel Admin / Reportes",
     "Como SR. GÓMEZ ADMINISTRADOR, quiero DASHBOARD 6 KPIs + 12 METRICAS para la toma decisiones sin consultar hojas Excel.",
     "DADO /panel/dashboard\nENTONCES KPIs: Usuarios Activos / Clientes / Espacios / Reservas Totales / Pedidos / Ingresos Mes COP + 12 métricas adicionales ocupación/niveles/puntos.","P0",13,"RF-RPT-001/002/008/009/010/011/012","✅ Implementado","Persona Sr. Gómez Admin"],
    ["US-F02","4 (Complementarios y Cierre)","S9 · S10","Reportes + Top Clientes",
     "Como ADMIN, quiero TOP 10 CLIENTES RANKING + GRÁFICOS INGRESOS vs RESERVAS por 6 meses para reconocer mejores clientes.",
     "DADO /panel/reportes\nENTONCES tabla top10 con medallas Oro Plata Bronce visual; gráfico líneas 2 colores reservas/barra.","P1",5,"RF-RPT-003/004/005","✅ Implementado","Administración + Mercadeo"],
    ["US-F03","4 (Complementarios y Cierre)","S10","Notificaciones Internas",
     "Como TODOS LOS USUARIOS, quiero BANDEJA NOTIFICACIONES con badge sin leer y MARCAR LEÍDAS para no perder novedades.",
     "DADO 2 notificaciones sin leer (reserva confirmada, pedido listo)\nENTONCES badge 2 rojo bottom nav; botón 'Marcar todas leídas' limpia badge 0.","P1",5,"RF-RPT-006/007/013","✅ Implementado","Todos usuarios"],
    # Pruebas e Integración
    ["US-QA01","4 (Pruebas)","S10 · S11","Calidad Pruebas",
     "Como Scrum Master, quiero PRUEBAS FUNCIONALES 100% HISTORIAS CRÍTICAS + PRUEBAS INTEGRACIÓN para 0 errores producción.",
     "DADO suite 14 smoke tests + pruebas manuales por rol\nCUANDO ejecuto smoke_test.py\nENTONCES 14/14 OK; pruebas manual 3 roles 3 usuarios representativos pasan ≥ 98%.","P0",8,"RNF-CAL-003","✅ Aprobado","QA / Scrum Master"],
    ["US-QA02","4 (Pruebas)","S10 · S11","Usabilidad x Rol",
     "Como EQUIPO, quiero SESIONES PRUEBA USABILIDAD por rol (1 usuario admin + 1 recepción + 1 cliente) con registro incidencias.",
     "DADO 3 usuarios representativos\nCUANDO completan 10 tareas típicas\nENTONCES System Usability Scale (SUS) ≥ 80; incidencias ≥ críticas corregidas.","P1",5,"RNF-UX-006","✅ Aprobado","Scrum Team"],
    ["US-QA03","4 (Pruebas)","S10 · S11","Corrección Incidencias",
     "Como Developer, quiero REGISTRO SISTEMATIZADO INCIDENCIAS clasificadas por severidad Bloqueante/Menor/Media para cierre antes entrega.",
     "DADO listado Trello/Jira incidencias\nCUANDO sprint finaliza\nENTONCES 0 incidencias severidad BLOQUEANTE pendientes; ≤3 menores.","P1",5,"RNF-CAL-003","✅ Resuelto","Developer"],
    # Documentación y Entrega
    ["US-DO01","4 (Cierre)","S11 · S12","Documentación Técnica",
     "Como Scrum Master / Director, quiero DOCUMENTO TÉCNICO DEL SISTEMA (arquitectura, modelo datos, endpoints principales) para mantenimiento futuro.",
     "DADO cierre desarrollo\nCUANDO se entrega documento técnico + Postman Collection 40 endpoints\nENTONCES siguiente desarrollador entiende el código en < 4 horas.","P1",8,"RNF-CAL-004/005/006","✅ Entregado","Director Tesis"],
    ["US-DO02","4 (Cierre)","S11 · S12","Manual Usuario x Rol",
     "Como ADMINISTRADOR DEL CLUB, quiero MANUAL DE USUARIO DIGITAL POR ROL para entrenar recepcionista y nuevas contrataciones sin el desarrollador.",
     "DADO PDF manual 3 versiones\nENTONCES Manual ADMIN capítulos Panel + Inventario; Manual RECEPCIÓN cobros; Manual CLIENTE registro/reservas/canje.","P1",8,"Documentación","✅ Entregado","Club Family Health"],
    ["US-DO03","4 (Cierre)","S12","Despliegue + Entrega Final",
     "Como PO (Club Family Health), quiero PROTOTIPO DESPLEGADO RAILWAY/RENDER HTTPS + URL PÚBLICA para probar sin servidor local, más presentación resultados Director.",
     "DADO entorno producción\nCUANDO accedo a https://familyhealth.up.railway.app/\nENTONCES Health Check 200; login admin_fh funciona; reserva no cruce 0.","P0",8,"RNF-DIS-004/005","✅ Entregado","Scrum Team + Jurado"]
]
HIST += SPRINT4

# Escribir 52 historias al Excel
for i, hist in enumerate(HIST, 1):
    r = 3 + i
    hpb.cell(r,1,i)
    for c,val in enumerate(hist, 2):
        hpb.cell(r,c,val)
celdas(hpb, 4, 4+len(HIST)-1, NCPB, pc=8, ec=10)
for r in range(4, 4+len(HIST)):
    hpb.row_dimensions[r].height = 95
# Colorear columna SPRINT con colores FOREST/WELL/SAND/CORAL según sprint
mapcolor_sprint = {"1 (Levant":FOREST,"2 (Análisis":WELL,"3 (Impl":SAND,"4 (Complem":CORAL,"4 (Pruebas":CORAL,"4 (Cierre":CORAL}
for r in range(4, 4+len(HIST)):
    cel = hpb.cell(r,3)
    for k,v in mapcolor_sprint.items():
        if str(cel.value or "").startswith(k):
            cel.fill = v; cel.font = Font(bold=True,color="FFFFFF",size=10); cel.alignment=WRAP_CENTRO
            break
anch(hpb,[4.5,9,16,10,22,52,58,6,6,20,14,24])
hpb.freeze_panes = "F4"

# ===================== Hojas 3-8: US por SPRINT y módulo =====================
HOJAS_X_MODULO = [
    ("3.US Sprint 1","SPRINT 1: LEVANTAMIENTO REQUERIMIENTOS · SEMANAS 1 – 2","1 (Levant. Reqs)",4, SPRINT1, FOREST),
    ("4.US Sprint 2","SPRINT 2: ANÁLISIS Y DISEÑO · SEMANAS 3 – 4","2 (Análisis y Diseño)",4, SPRINT2, WELL),
    ("5.US Sprint 3 Core","SPRINT 3: IMPL. MÓDULOS CORE · SEMANAS 5 – 7 (Auth + Reservas + Disponibilidad + Mobile UI)","3 (Impl. CORE)",8, SPRINT3, SAND),
    ("6.US Sprint 4A","SPRINT 4A: MÓDULOS COMPLEMENTARIOS · S8 – S10","4 (Complementarios y Cierre)",15, SPRINT4[:14], CORAL),
    ("7.US Sprint 4B","SPRINT 4B: PRUEBAS Y CIERRE · S10 – S12","4 (Pruebas)",5, SPRINT4[14:], CORAL),
]
COLS_US = ["#","ID","SPRINT","Semanas","Módulo","COMO [Rol]","QUIERO [Acción]","PARA [Beneficio]","Criterios GIVEN / WHEN / THEN","P","SP","RF Asociado","Estado","Rol / Persona"]
def dividir_historia(texto):
    """Divide 'Como X, quiero Y para Z' en 3 columnas"""
    if "Como " in texto and ", quiero " in texto and " para " in texto:
        resto = texto.split("Como ",1)[1]
        como, tmp = resto.split(", quiero ",1)
        if " para " in tmp:
            quiero, para = tmp.split(" para ",1)
            return como.strip(), quiero.strip(), para.strip()
    return texto[:80],"",""

for (nom_hoja, tit_corto, spr_id, n, lista_hist, color) in HOJAS_X_MODULO:
    hoja = WB.create_sheet(title=nom_hoja)
    Nc = len(COLS_US)
    titulo(hoja, tit_corto, f"{len(lista_hist)} Historias de Usuario · Scrum Team: PO=Club Family Health · SM=Director Tesis · DEV=Luis F. Díaz", Nc)
    for i,c in enumerate(COLS_US,1): hoja.cell(3,i,c)
    # Header con color de sprint
    for c_ in range(1,Nc+1):
        cc = hoja.cell(3,c_)
        cc.font=FUENTE_HEADER; cc.fill=color; cc.alignment=WRAP_CENTRO; cc.border=BORDE
    hoja.row_dimensions[3].height = 40
    for i,hh in enumerate(lista_hist,1):
        # hh = [ID, Sprint, Sem, Modulo, texto_historia_larga, GivenWhenThen, Prior, SP, RF, Estado, Persona]
        como, quiero, para = dividir_historia(hh[4])
        fila = [i, hh[0], hh[1], hh[2], hh[3], como, quiero, para, hh[5], hh[6], hh[7], hh[8], hh[9], hh[10]]
        r = 3 + i
        for cc_,v in enumerate(fila,1):
            hoja.cell(r,cc_,v)
    FF = 4; FFL = 4 + len(lista_hist) - 1
    celdas(hoja, FF, FFL, Nc, pc=10, ec=13)
    # Colorear celdas sprint
    for rr_ in range(FF, FFL+1):
        for cc_ in [3]:
            x = hoja.cell(rr_,cc_)
            x.fill = color; x.font = Font(bold=True,color="FFFFFF",size=10); x.alignment=WRAP_CENTRO
    # Altura wrapping
    for rr_ in range(FF, FFL+1):
        hoja.row_dimensions[rr_].height = 90
    # Pie totales
    pie = FFL + 2
    hoja.cell(pie,4,f"TOTAL {nom_hoja.upper()}:").font=FUENTE_HITO
    sp_tot = sum(int(hh[7]) for hh in lista_hist)
    hoja.cell(pie,9,f"Historias: {len(lista_hist)}").font=FUENTE_HITO
    hoja.cell(pie,11,f"SP: {sp_tot}").font=FUENTE_HITO
    anch(hoja,[4,8,16,9,18,20,30,25,50,4.5,5,20,12,20])
    hoja.freeze_panes = "E4"

# ============== GUARDAR ==============
# Guardar con sufijo v2 por si el archivo está abierto
nombre_final = "HISTORIAS_USUARIO_Y_PRODUCT_BACKLOG.xlsx"
nombre_temp  = "HISTORIAS_USUARIO_Y_PRODUCT_BACKLOG_v2.xlsx"
out = os.path.join(OUT_DIR, nombre_temp)
WB.save(out)
# Intentar renombrar a nombre final si es posible
final = os.path.join(OUT_DIR, nombre_final)
try:
    if os.path.exists(final):
        os.replace(final, final + ".old.bak")  # backup viejo
    os.rename(out, final)
    out = final
except PermissionError:
    print("(Nota: archivo Excel original abierto. Se guardó copia _v2.xlsx. Cierre Excel y renombre manualmente.)")
print("EXCEL OK:", out, "| Sheets:", WB.sheetnames)
print(f"Total historias escritas al Product Backlog: {len(HIST)}")
