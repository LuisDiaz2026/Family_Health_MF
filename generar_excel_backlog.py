# -*- coding: utf-8 -*-
"""
Generación del Excel Product Backlog + Historias por Módulo
Club Family Health MF - Colombia (COP)
100% Español
Hojas:
  1. Product Backlog (General 52 historias)
  2. US-A Autenticación
  3. US-B Reservas
  4. US-C Refrescos
  5. US-D Fidelización
  6. US-E Gimnasio
  7. US-F Reportes y Admin
"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

WB = openpyxl.Workbook()

# ============================================================
# ESTILOS GLOBALES
# ============================================================
FUENTE_TITULO = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
FUENTE_HEADER = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
FUENTE_NORMAL = Font(name="Calibri", size=10)
FUENTE_HITO = Font(name="Calibri", size=11, bold=True)

RELLENO_TITULO = PatternFill(start_color="174C3C", end_color="174C3C", fill_type="solid")  # Forest Green
RELLENO_HEADER = PatternFill(start_color="3B8064", end_color="3B8064", fill_type="solid")  # Wellness Green
RELLENO_P0 = PatternFill(start_color="E9784A", end_color="E9784A", fill_type="solid")      # Coral Terracotta
RELLENO_P1 = PatternFill(start_color="D7AE58", end_color="D7AE58", fill_type="solid")      # Sand Gold
RELLENO_P2 = PatternFill(start_color="F7F4EC", end_color="F7F4EC", fill_type="solid")      # Ivory
RELLENO_P3 = PatternFill(start_color="E6E6E6", end_color="E6E6E6", fill_type="solid")      # Gris claro
RELLENO_HECHO = PatternFill(start_color="C8E6C9", end_color="C8E6C9", fill_type="solid")   # Verde pasto

BORDE_FINO = Border(
    left=Side(style="thin", color="999999"),
    right=Side(style="thin", color="999999"),
    top=Side(style="thin", color="999999"),
    bottom=Side(style="thin", color="999999"),
)
ALINEAR_WRAP = Alignment(wrap_text=True, vertical="center", horizontal="left")
ALINEAR_CENTRO = Alignment(wrap_text=True, vertical="center", horizontal="center")

def aplicar_estilo_header(fila, hoja, num_cols):
    for c in range(1, num_cols + 1):
        cel = hoja.cell(row=fila, column=c)
        cel.font = FUENTE_HEADER
        cel.fill = RELLENO_HEADER
        cel.alignment = ALINEAR_CENTRO
        cel.border = BORDE_FINO

def aplicar_estilo_celdas(fila_inicio, fila_fin, hoja, num_cols, prioridad_col=None, estado_col=None):
    for r in range(fila_inicio, fila_fin + 1):
        for c in range(1, num_cols + 1):
            cel = hoja.cell(row=r, column=c)
            cel.font = FUENTE_NORMAL
            cel.alignment = ALINEAR_WRAP
            cel.border = BORDE_FINO
            if prioridad_col and c == prioridad_col:
                p = str(cel.value).strip().upper()
                if p == "P0": cel.fill = RELLENO_P0
                elif p == "P1": cel.fill = RELLENO_P1
                elif p == "P2": cel.fill = RELLENO_P2
                elif p == "P3": cel.fill = RELLENO_P3
            if estado_col and c == estado_col:
                e = str(cel.value)
                if "HECHO" in e.upper() or "CUMPLE" in e.upper():
                    cel.fill = RELLENO_HECHO

def ajustar_anchos(hoja, anchos):
    for idx, w in enumerate(anchos, 1):
        hoja.column_dimensions[get_column_letter(idx)].width = w

def escribir_titulo(hoja, titulo, subtitulo, num_cols):
    hoja.merge_cells(start_row=1, start_column=1, end_row=1, end_column=num_cols)
    c = hoja.cell(row=1, column=1, value=titulo)
    c.font = FUENTE_TITULO
    c.fill = RELLENO_TITULO
    c.alignment = Alignment(horizontal="center", vertical="center")
    hoja.row_dimensions[1].height = 30
    hoja.merge_cells(start_row=2, start_column=1, end_row=2, end_column=num_cols)
    cc = hoja.cell(row=2, column=1, value=subtitulo)
    cc.font = Font(name="Calibri", size=10, italic=True, color="232927")
    cc.fill = PatternFill(start_color="F7F4EC", end_color="F7F4EC", fill_type="solid")
    cc.alignment = Alignment(horizontal="center", vertical="center")
    hoja.row_dimensions[2].height = 22

# ============================================================
# DATOS 52 HISTORIAS (6 ÉPICOS / MÓDULOS)
# Cada historia: [ID, Épico / Módulo, Historia de Usuario (Como/Quiere/Para),
#                 Criterios Aceptación Given/When/Then, Prioridad, SP,
#                 RF Asociados, Sprint Planeado, Estado, Persona/Rol Impactado]
# ============================================================

HISTORIAS = [
# ---- ÉPICO A: AUTENTICACIÓN -------------------------------------------------
["US-A01","Autenticación y Usuarios",
"Como USUARIO NUEVO, quiero REGISTRARME proporcionando mis datos personales y aceptando explícitamente la Ley 1581 de 2012 (Habeas Data) para poder ingresar al sistema y usar los módulos digitales del club.",
"DADO que estoy en la pantalla de registro\nCUANDO completo los 14 campos obligatorios y marco las 2 casillas de política y términos\nENTONCES mi cuenta se crea con rol CLIENTE, se graba la fecha-hora de aceptación y recibo mensaje 'Registro exitoso'\nY SI dejo casilla sin marcar ENTONCES error 'Debe aceptar la política de privacidad'.",
"P0",5,"RF-AUTH-001, RF-AUTH-002","Sprint 1","✅ Implementado","Cliente Nuevo (Juan Carlos / Valeria / Andrés)"],

["US-A02","Autenticación y Usuarios",
"Como USUARIO REGISTRADO, quiero INICIAR SESIÓN con mi nombre de usuario y contraseña para acceder a mis módulos personalizados (cliente, recepción o admin).",
"DADO que tengo credenciales válidas\nCUANDO envío el formulario login\nENTONCES recibo un token de acceso (60 minutos) + refresh (7 días) firmados con HS512\nY soy redirigido a /cliente (soy cliente) o /panel (soy staff)\nY se crea una auditoría LOGIN con mi IP y User-Agent.",
"P0",5,"RF-AUTH-004, RF-AUTH-010","Sprint 1","✅ Implementado","Todos los Roles"],

["US-A03","Autenticación y Usuarios",
"Como USUARIO AUTENTICADO, quiero CERRAR SESIÓN de forma segura para que nadie más pueda usar mi cuenta desde este dispositivo.",
"DADO que tengo una sesión activa con token refresh válido\nCUANDO pulso el botón 'Cerrar sesión'\nENTONCES mi refresh token se agrega a la Blacklist (no se puede volver a usar)\nY los stores Pinia se limpian\nY soy redirigido a /login.",
"P0",3,"RF-AUTH-005, RF-AUTH-006","Sprint 1","✅ Implementado","Todos los Roles"],

["US-A04","Autenticación y Usuarios",
"Como SISTEMA, quiero BLOQUEAR AUTOMÁTICAMENTE el acceso después de 5 intentos fallidos de inicio de sesión en 15 minutos para prevenir ataques de fuerza bruta.",
"DADO que he realizado 4 intentos fallidos desde la misma IP y navegador\nCUANDO envío el 5to intento errado\nENTONCES recibo el error 403 'Cuenta temporalmente bloqueada 15 minutos'\nY el hecho se registra en security.log\nY pasado el tiempo de enfriamiento vuelvo a intentar.",
"P0",3,"RF-AUTH-007, RF-AUTH-008, RNF-SEC-004","Sprint 1","✅ Implementado","Seguridad del Sistema"],

["US-A05","Autenticación y Usuarios",
"Como CLIENTE, quiero CONSULTAR Y ACTUALIZAR mi perfil personal (datos, membresía, contacto de emergencia, tarjeta fidelidad) para mantener mi información al día.",
"DADO que inicio sesión como cliente\nCUANDO ingreso a /cliente/perfil\nENTONCES veo mis datos precargados\nY al guardar cambios retorno 200 OK\nY se genera una auditoría PROFILE_EDIT.",
"P1",5,"RF-AUTH-009, RF-AUTH-010","Sprint 2","✅ Implementado","Cliente"],

["US-A06","Autenticación y Usuarios",
"Como ADMINISTRADOR, quiero CREAR CUENTAS para los empleados (recepcionistas, barra, entrenadores) y otros administradores para delegar responsabilidades operativas.",
"DADO que soy ADMIN\nCUANDO envío POST /api/users con rol EMPLOYEE o ADMIN\nENTONCES se crea la cuenta con contraseña Argon2 hasheada\nY SI un empleado intenta crear usuarios recibe 403 Forbidden.",
"P1",5,"RF-AUTH-011, RNF-SEC-001","Sprint 2","✅ Implementado","Administrador Sr. Gómez"],

["US-A07","Autenticación y Usuarios",
"Como ADMINISTRADOR, quiero ACTIVAR o DESACTIVAR cuentas de usuario (derecho a desautorización Ley 1581/2012) sin borrar su historia de datos.",
"DADO que soy administrador\nCUANDO desactivo un usuario (is_active = False)\nENTONCES sus próximos intentos de login dan 401 credenciales inválidas\nY sus datos históricos se conservan por integridad referencial (on_delete PROTECT).",
"P1",3,"RF-AUTH-012, RNF-SEC-003, RNF-SEC-008","Sprint 3","✅ Implementado","Administrador / Datos Personales"],

["US-A08","Autenticación y Usuarios",
"Como SISTEMA, quiero ROTAR EL REFRESH TOKEN en cada renovación y listar el anterior en Blacklist para evitar reutilizaciones maliciosas sin generar condiciones de carrera.",
"DADO que mi access token venció y mi refresh sigue vigente\nCUANDO el frontend pide la renovación vía Axios interceptor\nENTONCES recibo un NUEVO refresh token y el viejo queda bloqueado\nY el interceptor maneja una cola de peticiones sin ejecutar refresh doble paralelo.",
"P0",8,"RF-AUTH-005, RNF-UX-007","Sprint 2","✅ Implementado","Seguridad Frontend-Backend"],

# ---- ÉPICO B: RESERVAS -------------------------------------------------
["US-R01","Reservas de Espacios",
"Como CLIENTE, quiero VISUALIZAR EL CATÁLOGO DE ESPACIOS con foto, capacidad, nombre, tarifa por hora en pesos colombianos (COP) y estado para decidir cuál reservar.",
"DADO que navego a /cliente/reservas\nENTONCES veo tarjetas para las 10 instalaciones: 3 canchas F5, piscina, 3 salones múltiple, cancha tenis, gimnasio, squash\nY cada tarjeta muestra $/h en COP, capacidad de personas y estado Activo/Mantenimiento.",
"P0",5,"RF-RES-001","Sprint 2","✅ Implementado","Cliente"],

["US-R02","Reservas de Espacios",
"Como CLIENTE, quiero un ASISTENTE (WIZARD) EN 3 PASOS para reservar un espacio sin equivocarme de fecha ni de hora.",
"DADO que selecciono Cancha-01\nCUANDO sigo el flujo Paso 1 espacio → Paso 2 fecha → Paso 3 rango horario\nENTONCES no puedo avanzar sin completar el paso anterior\nY al final veo un resumen claro del valor total en pesos colombianos.",
"P0",5,"RF-RES-004","Sprint 2","✅ Implementado","Cliente (Mobile-First)"],

["US-R03","Reservas de Espacios",
"Como SISTEMA, quiero VALIDAR DISPONIBILIDAD EN TIEMPO REAL y evitar SOLAPES TRANSACCIONALES para nunca vender el mismo horario 2 veces.",
"DADO que Cancha-01 está reservada 18:00-19:00\nCUANDO un segundo cliente intenta reservar 18:30-19:30\nENTONCES recibe error 400 'Espacio no disponible en ese horario'\nY esto se garantiza con select_for_update() + constraint única en BD.",
"P0",8,"RF-RES-005, RF-RES-006, RNF-SEC-008","Sprint 2","✅ Implementado","Integridad Operativa"],

["US-R04","Reservas de Espacios",
"Como CLIENTE, quiero VER EL MONTO CALCULADO AUTOMÁTICAMENTE antes de confirmar para saber cuánto pagaré en pesos colombianos.",
"DADO que reservo 90 minutos de Cancha F5 a $50.000 COP/hora\nCUANDO se ejecuta el cálculo\nENTONCES el sistema muestra $75.000 COP exactos (90/60 × 50.000)\nY el método de pago aparece como 'Pendiente - Presencial'.",
"P1",3,"RF-RES-007","Sprint 2","✅ Implementado","Cliente"],

["US-R05","Reservas de Espacios",
"Como CLIENTE, quiero CANCELAR MI RESERVA SIN PENALIDAD SI AVISO con suficiente antelación según la política del espacio.",
"DADO que falta ≥6 horas para mi reserva (penalty_hours = 6)\nCUANDO pulso Cancelar\nENTONCES pasa a estado CANCELADA con mi usuario y fecha registrados\nY SI faltara <6 horas me devuelve error 'Cancelación no permitida'.",
"P1",5,"RF-RES-010","Sprint 3","✅ Implementado","Cliente"],

["US-R06","Reservas de Espacios",
"Como CLIENTE, quiero LISTAR MIS RESERVAS clasificadas en pestañas: próximas, en curso ahora, históricas y canceladas, para tener control de todo.",
"DADO que tengo reservas pasadas, presentes y futuras\nCUANDO entro a /cliente/reservas\nENTONCES veo 4 pestañas con filtros\nY cada fila muestra fecha, espacio, color de estado y valor pagado en COP.",
"P1",5,"RF-RES-012","Sprint 3","✅ Implementado","Cliente"],

["US-R07","Reservas de Espacios",
"Como RECEPCIONISTA, quiero APROBAR O RECHAZAR RESERVAS PENDIENTES de espacios premium para controlar accesos de alta demanda.",
"DADO que llega una reserva de Salón Premium que requiere aprobación empleado\nCUANDO recepcionista pulsa 'Aprobar'\nENTONCES pasa a CONFIRMADA con approved_by y approved_at\nY al cliente llega una notificación push interna de confirmación.",
"P0",5,"RF-RES-011, RF-RES-008, RF-RPT-006","Sprint 3","✅ Implementado","Empleado Recepción (Carlos)"],

["US-R08","Reservas de Espacios",
"Como RECEPCIONISTA, quiero MARCAR UNA RESERVA COMO PAGADA cuando el cliente cancela presencialmente en efectivo, tarjeta o transferencia para cerrar el ciclo de cobro.",
"DADO que el cliente paga en efectivo $75.000 COP\nCUANDO recepcionista pulsa 'Marcar Pagada'\nENTONCES payment_status pasa a PAGADO\nY se registra quién recibió el pago y la hora\nY se calculan y otorgan los puntos de fidelización automáticamente.",
"P0",5,"RF-RES-009, RF-LOY-002, RF-LOY-003","Sprint 3","✅ Implementado","Empleado Recepción"],

["US-R09","Reservas de Espacios",
"Como ADMINISTRADOR, quiero CREAR, MODIFICAR y ELIMINAR espacios, sus horarios operativos semanales y días festivos de cierre para ajustar la operación.",
"DADO que soy administrador en /panel/espacios\nCUANDO creo un nuevo espacio con 7 horarios (lunes a domingo) y añado el 1 de enero como Holiday\nENTONCES las consultas de disponibilidad respetan tanto los horarios como el cierre por festivo.",
"P1",8,"RF-RES-002, RF-RES-003, RF-RES-013","Sprint 4","✅ Implementado","Administrador Sr. Gómez"],

["US-R10","Reservas de Espacios",
"Como EMPLEADO O ADMIN, quiero MARCAR RESERVAS COMO COMPLETADAS O NO ASISTIÓ para la trazabilidad histórica y los reportes de ocupación.",
"DADO que la fecha de la reserva ya pasó\nCUANDO pulso 'No Asistió' el servicio queda en estado NO_SHOW y no cuenta en ocupación\nY al marcar COMPLETADA sí se considera en ingresos si está pagada.",
"P2",3,"RF-RES-008","Sprint 4","✅ Implementado","Empleados en general"],

# ---- ÉPICO C: REFRESCOS -------------------------------------------------
["US-C01","Refresquería e Inventario",
"Como CLIENTE, quiero EXPLORAR EL CATÁLOGO DE PRODUCTOS agrupado por categorías (Bebidas Frías, Calientes, Snacks, Comidas Rápidas, Postres) para escoger mi pedido.",
"DADO que ingreso a /cliente/refrescos\nENTONCES veo 5 pestañas de categorías\nY 23 productos con foto, nombre, precio COP, stock disponible\nY aquellos sin stock muestran la etiqueta 'Agotado' con botón deshabilitado.",
"P0",5,"RF-REF-001, RF-REF-002","Sprint 3","✅ Implementado","Cliente"],

["US-C02","Refresquería e Inventario",
"Como CLIENTE, quiero UN CARRITO DE COMPRAS PERSISTENTE en mi móvil para armar el pedido sin perder datos aunque cierre la pestaña.",
"DADO que agrego una Gatorade $4.500 COP y una Hamburguesa $18.000 COP\nCUANDO cierro Chrome y vuelvo a abrir 30 minutos después\nENTONCES mi carrito 'fh_cart' en localStorage se recupera intacto\nY puedo seguir agregando o quitando productos.",
"P0",5,"RF-REF-003, RNF-UX-005","Sprint 3","✅ Implementado","Cliente Mobile"],

["US-C03","Refresquería e Inventario",
"Como SISTEMA, quiero REDUCIR EL STOCK DE FORMA ATÓMICA con F() expressions para nunca vender productos que no existen en bodega.",
"DADO que un producto tiene 5 unidades\nCUANDO un cliente compra 5 exactas\nENTONCES stock queda en 0 mediante update F(stock)-5\nY SI otro cliente intenta comprar 1 más recibe ValueError 'Stock insuficiente' + rollback atómico.",
"P0",8,"RF-REF-004, RNF-SEC-008, RNF-DIS-005","Sprint 3","✅ Implementado","Integridad Inventario"],

["US-C04","Refresquería e Inventario",
"Como CLIENTE NIVEL ORO O DIAMANTE, quiero recibir DESCUENTO AUTOMÁTICO POR FIDELIDAD en mi carrito para premiar mi constancia.",
"DADO que mi nivel es ORO con 10% de descuento\nCUANDO subtotal del carrito es $50.000 COP\nENTONCES discount_amount = $5.000 y total a pagar = $45.000 COP\nY los campos quedan guardados en el pedido histórico.",
"P1",5,"RF-REF-005, RF-LOY-001","Sprint 4","✅ Implementado","Cliente Leal Niveles Alto"],

["US-C05","Refresquería e Inventario",
"Como CLIENTE, quiero ELEGIR UN MÉTODO DE PAGO PRESENCIAL (efectivo, tarjeta física, transferencia o descuento membresía) al finalizar el pedido.",
"DADO que voy a checkout\nENTONCES veo 4 opciones de pago alineadas con operación 100% presencial\nY al confirmar el pedido queda en estado PENDIENTE de pago real.",
"P1",3,"RF-REF-006","Sprint 4","✅ Implementado","Cliente"],

["US-C06","Refresquería e Inventario",
"Como EMPLEADA DE BARRA, quiero AVANZAR EL ESTADO DEL PEDIDO EN CICLO LINEAL: Pendiente → Preparando → Listo → Entregado → Pagado para organizar el trabajo.",
"DADO que llega un pedido PENDIENTE a barra\nCUANDO María (barra) avanza estado tras estado\nENTONCES cada cambio dispara una notificación al cliente\nY el UI muestra badges de colores distintos por estado.",
"P0",5,"RF-REF-007, RF-REF-011, RF-RPT-006","Sprint 4","✅ Implementado","Empleada Barra (María)"],

["US-C07","Refresquería e Inventario",
"Como CLIENTE, quiero VER EL HISTORIAL DE MIS PEDIDOS y el tracking del estado actual para saber cuándo ir a recogerlo.",
"DADO que ingreso a /cliente/pedidos\nENTONCES veo cards con el consecutivo PED-AAAA-MMDD-NNNNN, fecha, productos resumen, color estado y valor total COP\nY al expandir veo el detalle línea por línea.",
"P1",5,"RF-REF-012, RF-REF-008, RF-REF-009","Sprint 4","✅ Implementado","Cliente"],

["US-C08","Refresquería e Inventario",
"Como ADMIN O EMPLEADO BARRA, quiero GESTIONAR EL INVENTARIO y VER ALERTA DE STOCK BAJO para reabastecer a tiempo.",
"DADO que Producto Agua sin gas tiene stock 4 y stock mínimo 5\nCUANDO cargo /panel/productos\nENTONCES el producto aparece con fila en rojo y distintivo 'Stock Bajo'\nY puedo usar botón rápido '+10' / '-10' para ajustar inventario.",
"P0",8,"RF-REF-010, RF-REF-013","Sprint 5","✅ Implementado","Barra / Administración"],

["US-C09","Refresquería e Inventario",
"Como SISTEMA, quiero NUMERAR LOS PEDIDOS AUTOMÁTICAMENTE con prefijo PED-AAAA-MMDD-NNNNN para facilitar la conciliación contable.",
"DADO que se crean 2 pedidos el mismo día 2026-09-20\nENTONCES el primero es PED-20260920-00001 y el segundo PED-20260920-00002\nY order_number es único en la base de datos.",
"P2",3,"RF-REF-008, RF-REF-009","Sprint 5","✅ Implementado","Contabilidad y Control"],

# ---- ÉPICO D: FIDELIZACIÓN -------------------------------------------------
["US-L01","Fidelización y Recompensas",
"Como CLIENTE, quiero IDENTIFICARME EN 4 NIVELES DE FIDELIDAD CON COLORES DISTINTIVOS para sentir mi progreso dentro del club (Bronce, Plata, Oro, Diamante).",
"DADO que mi perfil se crea automáticamente\nENTONCES empiezo en Nivel BRONCE (0+ puntos) color #CD7F32, 0% descuento\nY al subir obtengo PLATA (500+ 5%), ORO (1500+ 10%), DIAMANTE (3000+ 15%).",
"P1",5,"RF-LOY-001","Sprint 5","✅ Implementado","Cliente Motivación"],

["US-L02","Fidelización y Recompensas",
"Como CLIENTE, quiero GANAR PUNTOS cada vez que pago una reserva o un pedido de barra, y también por referidos, cumpleaños y renovación de membresía.",
"DADO que la regla RESERVA_COMPLETADA tiene pts base 50 y pts por cada $1.000 COP = 2\nCUANDO pago una reserva de $100.000 COP\nENTONCES recibo 250 puntos (50 base + 100 × 2)\nY se registra transacción tipo GANADOS.",
"P1",5,"RF-LOY-002, RF-LOY-003, RF-LOY-005","Sprint 5","✅ Implementado","Cliente"],

["US-L03","Fidelización y Recompensas",
"Como CLIENTE, quiero CANJEAR MIS PUNTOS ACUMULADOS por productos/servicios del catálogo (Gatorade, día piscina, membresía) como recompensa a mi lealtad.",
"DADO que catálogo recompensas muestra: Gatorade 80pts / 1h Piscina 300pts / 1mes Membresía 2500pts\nCUANDO tengo 320 puntos\nENTONCES puedo canjear Gatorade o Piscina (botón habilitado)\nPero no membresía (botón deshabilitado).",
"P1",5,"RF-LOY-004","Sprint 5","✅ Implementado","Cliente Canjes"],

["US-L04","Fidelización y Recompensas",
"Como CLIENTE, quiero VER UNA BARRA DE PROGRESO HACIA EL SIGUIENTE NIVEL para motivarme a seguir venciendo metas de puntos.",
"DADO que tengo 750 puntos, mi nivel actual Plata (500) y siguiente Oro (1500)\nCUANDO cargo /cliente/fidelidad\nENTONCES barra indica 25% completado\nY texto: 'Te faltan 750 puntos para alcanzar el Nivel Oro'.",
"P2",3,"RF-LOY-006, RF-LOY-008","Sprint 5","✅ Implementado","Cliente Gamificación"],

["US-L05","Fidelización y Recompensas",
"Como SISTEMA, quiero ACTUALIZAR AUTOMÁTICAMENTE EL NIVEL (TIER) del cliente en cada transacción de puntos y avisarle por notificación cuando asciende.",
"DADO que el cliente está en 1499 (Plata) y gana 2 puntos → total 1501\nCUANDO se guarda la transacción\nENTONCES _update_tier() le asigna Nivel ORO\nY llega notificación push '¡Felicitaciones! Ahora eres Nivel Oro'.",
"P1",5,"RF-LOY-006, RF-LOY-010, RF-RPT-006","Sprint 5","✅ Implementado","Sistema Automatización"],

["US-L06","Fidelización y Recompensas",
"Como CLIENTE, quiero VER EL HISTORIAL DETALLADO DE MOVIMIENTOS DE PUNTOS para mantener transparencia sobre lo que gano y canjeo.",
"DADO que entro a la pestaña 'Movimientos'\nENTONCES veo líneas con fecha, tipo (Ganados + verde / Canjeados - rojo / Ajuste), descripción, monto en puntos y SALDO DESPUÉS.",
"P2",5,"RF-LOY-005, RF-LOY-007","Sprint 6","✅ Implementado","Cliente Transparencia"],

["US-L07","Fidelización y Recompensas",
"Como ADMINISTRADOR, quiero GESTIONAR LAS REGLAS, LOS NIVELES Y EL CATÁLOGO DE RECOMPENSAS para activar promociones sin depender del desarrollador.",
"DADO que estoy en /panel/recompensas\nENTONCES puedo CRUD reglas (activar/desactivar promoción especial)\nY agregar nuevos niveles\nY premios nuevos al catálogo de canjes (ej: plancha 1.200 pts navidad).",
"P2",8,"RF-LOY-009","Sprint 6","✅ Implementado","Administrador Sr. Gómez"],

["US-L08","Fidelización y Recompensas",
"Como SISTEMA, quiero CREAR AUTOMÁTICAMENTE el LoyaltyProfile vía señal Django cuando se registra un nuevo CLIENTE para que su nivel empiece en Bronce 0 puntos.",
"DADO que se crea un User con role CLIENT\nENTONCES post_save signal crea LoyaltyProfile con tier BRONCE, current_points=0\nY no requiere intervención manual.",
"P3",3,"RF-LOY-010","Sprint 6","✅ Implementado","Automatización Sistema"],

# ---- ÉPICO E: GIMNASIO -------------------------------------------------
["US-G01","Módulo Gimnasio",
"Como CLIENTE, quiero TENER 5 RUTINAS PREESTABLECIDAS con objetivos diferentes (Fuerza, Hipertrofia, Definición, Funcional, Glúteos y Piernas) para empezar a entrenar hoy mismo.",
"DADO que entro a /cliente/gimnasio\nENTONCES veo cards de las 5 rutinas genéricas con tag objetivo, dificultad, días por semana\nY puedo seleccionar la que más se ajuste a mis metas.",
"P1",5,"RF-GYM-004","Sprint 6","✅ Implementado","Cliente Deportista (Andrés)"],

["US-G02","Módulo Gimnasio",
"Como CLIENTE, quiero CONSULTAR EL DETALLE COMPLETO DE LA RUTINA con calentamiento, sets/reps/pesos/descansos por ejercicio, enfriamiento y tips nutricionales.",
"DADO que abro rutina 'Hipertrofia Avanzada'\nENTONCES veo 4 secciones expandibles por acordeón: Calentamiento, Ejercicios, Enfriamiento, Tips nutricionales\nY cada ejercicio con foto, 3×12 repeticiones × 60kg × 90s descanso.",
"P1",8,"RF-GYM-005, RF-GYM-006","Sprint 6","✅ Implementado","Cliente"],

["US-G03","Módulo Gimnasio",
"Como CLIENTE, quiero BUSCAR EJERCICIOS POR ZONA MUSCULAR (12 grupos) para focalizar mis entrenamientos.",
"DADO que tengo dudas de cómo trabajar pecho\nCUANDO elijo grupo muscular 'Pecho'\nENTONCES filtro ejercicios solo de pecho\nY cada card muestra dificultad, equipo, instrucciones y tips.",
"P2",5,"RF-GYM-001, RF-GYM-002","Sprint 6","✅ Implementado","Cliente Deportista"],

["US-G04","Módulo Gimnasio",
"Como CLIENTE, quiero REGISTRAR CADA SESIÓN DE ENTRENAMIENTO COMPLETADA para llevar mi propio histórico deportivo.",
"DADO que terminé la rutina del día\nCUANDO abro modal 'Registrar sesión'\nENTONCES ingreso duración minutos, calorías aproximadas, sensación 1-10 y notas\nY se guarda un WorkoutLog asociado a mí.",
"P2",5,"RF-GYM-007","Sprint 6","✅ Implementado","Cliente Auto-Seguimiento"],

["US-G05","Módulo Gimnasio",
"Como ENTRENADOR / RECEPCIONISTA, quiero ASIGNAR UNA RUTINA PERSONALIZADA SOLO A UN CLIENTE ESPECÍFICO con fecha de vigencia.",
"DADO que Juan Carlos pide plan 8 semanas hipertrofia personalizada\nCUANDO como staff creo rutina is_generic=False, assigned_client=Juan Carlos, valid_from, valid_until\nENTONCES solo Juan Carlos la ve en su sección 'Mis Rutinas Asignadas', los demás clientes no la visualizan.",
"P2",5,"RF-GYM-004, RF-GYM-008","Sprint 6","✅ Implementado","Empleado Entrenador"],

["US-G06","Módulo Gimnasio",
"Como ADMINISTRADOR, quiero MANTENER EL CATÁLOGO DE EQUIPOS / MÁQUINAS del gimnasio con su ubicación y zona muscular que trabaja.",
"DADO que llega nueva máquina 'Prensa de Piernas'\nCUANDO ADMIN la crea con ubicación 'Zona B - Primer Piso' y músculos Cuádriceps + Glúteos\nENTONCES los ejercicios pueden asociarse a esta máquina como equipo principal.",
"P3",3,"RF-GYM-003, RF-GYM-009","Sprint 6","✅ Implementado","Administración Mantenimiento"],

["US-G07","Módulo Gimnasio",
"Como CLIENTE, quiero VER CONSEJOS, ERRORES COMUNES Y VIDEO TUTORIAL por ejercicio para evitar lesiones y maximizar resultados.",
"DADO que entro al ejercicio 'Sentadilla con barra'\nENTONCES están disponibles los campos: instrucciones paso a paso, tips de postura, errores frecuentes (no rodillas > dedos pies)\nY URL de video tutorial YouTube integrado.",
"P2",2,"RF-GYM-002","Sprint 6","✅ Implementado","Cliente Prevención Lesiones"],

# ---- ÉPICO F: ADMIN Y REPORTES -------------------------------------------
["US-F01","Administración y Reportes",
"Como ADMINISTRADOR, quiero 6 KPIs PRINCIPALES EN EL PANEL PRINCIPAL para tener el pulso del negocio sin navegar por menús.",
"DADO que entro a /panel/dashboard como ADMIN\nENTONCES veo 6 tarjetas grandes: Usuarios Activos, Clientes Totales, Espacios, Reservas Totales, Pedidos, Ingresos del Mes en Pesos COP\nY cada tarjeta con icono institucional y tendencia porcentual semanal.",
"P0",8,"RF-RPT-001, RF-RPT-002, RNF-UX-002","Sprint 4","✅ Implementado","Administrador Sr. Gómez"],

["US-F02","Administración y Reportes",
"Como ADMINISTRADOR, quiero EL PORCENTAJE DE OCUPACIÓN DE LOS ÚLTIMOS 7 DÍAS para detectar patrones de días pico y días vacíos.",
"DADO que cargo dashboard\nENTONCES card 'Ocupación 7 días' calcula: (minutos reservados) / (10.080 minutos-semana × espacios activos)\nY muestra su valor en % con barras diarias Forest Green.",
"P1",5,"RF-RPT-002","Sprint 5","✅ Implementado","Administrador"],

["US-F03","Administración y Reportes",
"Como ADMINISTRADOR, quiero UN GRÁFICO DE INGRESOS MENSUALES separando Reservas vs. Barra (refrescos) para saber qué línea de negocio vende más.",
"DADO que selecciono últimos 6 meses\nENTONCES aparece 2 líneas superpuestas: línea Ingresos Reservas $ vs. línea Ingresos Pedidos $ en COP\nY tooltip muestra el valor exacto del mes.",
"P1",5,"RF-RPT-004","Sprint 5","✅ Implementado","Administración Contable"],

["US-F04","Administración y Reportes",
"Como ADMINISTRADOR, quiero EL RANKING TOP 10 CLIENTES con puesto, nombre, tipo membresía, cantidad reservas, pedidos y gasto total COP para reconocer y premiar mis mejores clientes.",
"DADO que entro /panel/reportes top clientes\nENTONCES tabla con 10 filas orden descendente por total_spent\nY las 3 primeras filas tienen medallas Oro/Plata/Bronce visuales.",
"P1",8,"RF-RPT-005","Sprint 5","✅ Implementado","Administrador / Mercadeo"],

["US-F05","Administración y Reportes",
"Como RECEPCIONISTA, quiero GESTIONAR TODAS LAS RESERVAS DESDE EL PANEL (filtros + acciones en fila) para la operación presencial ágil.",
"DADO que estoy en /panel/reservas\nENTONCES tengo filtros rápidos HOY, PENDIENTES, CONFIRMADAS, TODAS\nY botones en cada fila: Aprobar, Rechazar, Marcar Pagada, Cancelar, No Asistió.",
"P0",5,"RF-RPT-008, RF-RES-011","Sprint 4","✅ Implementado","Recepción Carlos"],

["US-F06","Administración y Reportes",
"Como EMPLEADA DE BARRA, quiero GESTIONAR LOS PEDIDOS DE BARRA desde un panel organizado por colores para atender en el menor tiempo.",
"DADO que estoy en /panel/pedidos\nENTONCES cards en grid con distinto color de fondo: PENDI(amarillo) / PREPARANDO(azul) / LISTO(verde) / PAGADO(gris)\nY botón 1 clic 'Siguiente estado'.",
"P0",5,"RF-RPT-009, RF-REF-007, RF-REF-011","Sprint 4","✅ Implementado","Barra María"],

["US-F07","Administración y Reportes",
"Como ADMINISTRADOR, quiero VER LA FICHA COMPLETA DE UN CLIENTE (membresía, reservas, pedidos, puntos fidelidad, gasto total COP) para toma de decisiones 1-a-1.",
"DADO que entro a /panel/clientes y abro Valeria Martínez\nENTONCES veo: datos personales, membresía activa, vencimiento, n° reservas estado, n° pedidos estado, nivel actual + puntos acumulados, gasto total histórico en pesos.",
"P1",5,"RF-RPT-010, RF-LOY-007","Sprint 6","✅ Implementado","Administrador"],

["US-F08","Administración y Reportes",
"Como CUALQUIER USUARIO, quiero UNA BANDEJA DE NOTIFICACIONES INTERNA con distintivo rojo de mensajes sin leer para no perderme novedades del club.",
"DADO que tengo 2 notificaciones sin leer (1 reserva confirmada, 1 pedido listo)\nENTONCES el icono del navbar muestra badge con número 2\nY al abrir /notificaciones puedo marcar leídas individualmente o pulsar 'Marcar todas leídas'.",
"P1",5,"RF-RPT-006, RF-RPT-007","Sprint 4","✅ Implementado","Todos los Usuarios"],

["US-F09","Administración y Reportes",
"Como SISTEMA DE MONITOREO, quiero UN ENDPOINT PÚBLICO DE SALUD /api/v1/health/ que devuelva 200 OK con versión, timestamp y estado BD para verificar disponibilidad sin login.",
"DADO que ejecuto curl GET /api/v1/health/ sin token\nENTONCES respuesta HTTP 200 JSON: {status:'ok', version:'1.0.0', timestamp, club:{nombre,nit,ciudad:Maicao}, database:'ok'}.",
"P1",3,"RF-RPT-013, RNF-DIS-005","Sprint 1","✅ Implementado","Operaciones / DevOps"],

["US-F10","Administración y Reportes",
"Como ADMINISTRADOR, quiero LA DISTRIBUCIÓN DE CLIENTES POR NIVEL DE FIDELIDAD (Bronce, Plata, Oro, Diamante) para medir calidad de cartera.",
"DADO que cargo el dashboard\nENTONCES card 'Niveles Fidelidad' muestra gráfico tipo donut con 4 segmentos de colores\nY totales clientes por nivel con su valor %.",
"P2",3,"RF-RPT-002, RF-LOY-001","Sprint 5","✅ Implementado","Administrador"],
]

# ============================================================
# HOJA 1: PRODUCT BACKLOG (TOTAL 52 HISTORIAS)
# ============================================================
hoja_pb = WB.active
hoja_pb.title = "1.Product Backlog"
COL_PB = ["N°","ID Historia","Épico / Módulo","Historia de Usuario (Como rol / quiero acción / para beneficio)",
          "Criterios de Aceptación Given · When · Then","Prioridad","Story Points",
          "RF / RNF Asociados","Sprint","Estado Implementación","Rol / Persona Impactada"]
NUM_COLS_PB = len(COL_PB)
escribir_titulo(hoja_pb,
    "PRODUCT BACKLOG - CLUB FAMILY HEALTH MF",
    "Proyecto Colombia (COP) · 52 Historias de Usuario · 6 Sprints · 239 Story Points · Actualizado: 2026-09-20",
    NUM_COLS_PB)
# Fila 3 = headers
for c_idx, col in enumerate(COL_PB, 1):
    hoja_pb.cell(row=3, column=c_idx, value=col)
aplicar_estilo_header(3, hoja_pb, NUM_COLS_PB)
hoja_pb.row_dimensions[3].height = 36
for i, historia in enumerate(HISTORIAS, 1):
    fila = 3 + i
    hoja_pb.cell(row=fila, column=1, value=i)
    for offset, val in enumerate(historia, 2):
        hoja_pb.cell(row=fila, column=offset, value=val)
FILA_INI_PB = 4
FILA_FIN_PB = FILA_INI_PB + len(HISTORIAS) - 1
aplicar_estilo_celdas(FILA_INI_PB, FILA_FIN_PB, hoja_pb, NUM_COLS_PB, prioridad_col=6, estado_col=9)
# Alturas: historia + criterios aceptacion alto wrapping
for r in range(FILA_INI_PB, FILA_FIN_PB + 1):
    hoja_pb.row_dimensions[r].height = 100
ajustar_anchos(hoja_pb,[6,13,25,60,60,11,11,24,11,18,28])
hoja_pb.freeze_panes = "A4"

# ============================================================
# AGRUPAR HISTORIAS POR MÓDULO (hacer una hoja cada ÉPICO)
# ============================================================
HISTORIAS_POR_EPICO = [
    ("2.US Autenticación","MÓDULO 1: AUTENTICACIÓN Y GESTIÓN DE USUARIOS (RBAC, Ley 1581/2012)","A",8),
    ("3.US Reservas","MÓDULO 2: RESERVAS DE ESPACIOS DEPORTIVOS Y RECREATIVOS","B",10),
    ("4.US Refrescos","MÓDULO 3: REFRESQUERÍA, PEDIDOS E INVENTARIO DE PRODUCTOS","C",9),
    ("5.US Fidelización","MÓDULO 4: PROGRAMA DE FIDELIZACIÓN 4 NIVELES Y RECOMPENSAS","D",8),
    ("6.US Gimnasio","MÓDULO 5: RUTINAS Y EJERCICIOS DE GIMNASIO","E",7),
    ("7.US Reportes","MÓDULO 6: PANEL ADMINISTRATIVO, KPIs Y NOTIFICACIONES","F",10),
]

def hacer_hoja_por_modulo(nombre_hoja, titulo_mod, letra_epica, n):
    hoja = WB.create_sheet(title=nombre_hoja)
    cols = [
        "N°","ID Historia","Épico",
        "COMO [Rol]","QUIERO [Acción]","PARA [Beneficio]",
        "Criterios de Aceptación Given · When · Then",
        "Prior.","SP","RF/RNF Asociados","Sprint","Estado","Rol Impactado",
    ]
    num_cols = len(cols)
    escribir_titulo(hoja, titulo_mod, f"ÉPICO {letra_epica} - {n} Historias de Usuario", num_cols)
    for c_idx, col in enumerate(cols, 1):
        hoja.cell(row=3, column=c_idx, value=col)
    aplicar_estilo_header(3, hoja, num_cols)
    hoja.row_dimensions[3].height = 36
    # Filtrar historias que empiecen con US-{letra_epica}
    filtro = [h for h in HISTORIAS if h[0].startswith(f"US-{letra_epica}")]
    for i, hist in enumerate(filtro, 1):
        # Dividir historia 'Como X, quiero Y para Z' en 3 columnas
        texto = hist[2]  # Historia de Usuario larga
        como = ""; quiero = ""; para = ""
        if "Como " in texto and ", quiero " in texto and " para " in texto:
            resto1 = texto.split("Como ",1)[1]
            como, tmp = resto1.split(", quiero ",1)
            if " para " in tmp:
                quiero, para = tmp.split(" para ",1)
            else:
                quiero = tmp
        else:
            como = texto[:80]
        r = 3 + i
        hoja.cell(row=r, column=1, value=i)
        hoja.cell(row=r, column=2, value=hist[0])
        hoja.cell(row=r, column=3, value=hist[1])
        hoja.cell(row=r, column=4, value=como.strip())
        hoja.cell(row=r, column=5, value=quiero.strip())
        hoja.cell(row=r, column=6, value=para.strip())
        hoja.cell(row=r, column=7, value=hist[3])
        hoja.cell(row=r, column=8, value=hist[4])
        hoja.cell(row=r, column=9, value=hist[5])
        hoja.cell(row=r, column=10, value=hist[6])
        hoja.cell(row=r, column=11, value=hist[7])
        hoja.cell(row=r, column=12, value=hist[8])
        hoja.cell(row=r, column=13, value=hist[9])
    fin = 3 + len(filtro)
    aplicar_estilo_celdas(4, fin, hoja, num_cols, prioridad_col=8, estado_col=12)
    for rr in range(4, fin + 1):
        hoja.row_dimensions[rr].height = 95
    ajustar_anchos(hoja,[6,13,25,30,60,35,75,8,8,24,11,18,28])
    hoja.freeze_panes = "A4"
    # Pie: totales
    sp_tot = sum(int(h[5]) for h in filtro)
    pie = fin + 2
    hoja.cell(row=pie, column=3, value=f"TOTAL ÉPICO {letra_epica}:")
    hoja.cell(row=pie, column=3).font = FUENTE_HITO
    hoja.cell(row=pie, column=8, value=f"Historias: {len(filtro)}")
    hoja.cell(row=pie, column=8).font = FUENTE_HITO
    hoja.cell(row=pie, column=9, value=f"SP: {sp_tot}")
    hoja.cell(row=pie, column=9).font = FUENTE_HITO
    return hoja

for (nom, tit, letra, nn) in HISTORIAS_POR_EPICO:
    hacer_hoja_por_modulo(nom, tit, letra, nn)

# ============================================================
# PESTAÑA EXTRA 8: RESUMEN VELOCIDAD BURNDOWN
# ============================================================
hoja_sm = WB.create_sheet(title="8.Resumen Velocidad")
cols_sm = ["Sprint N°","Rango Fechas (Referencial)","Épicos Cubiertos","N° Historias","Story Points Entregados","Velocidad Acumulada (SP)"]
escribir_titulo(hoja_sm,
    "RESUMEN BURNDOWN / VELOCIDAD TEAM",
    "Capacidad del equipo: ~37-45 SP por Sprint · Total 239 Story Points",
    6)
for c, col in enumerate(cols_sm, 1):
    hoja_sm.cell(row=3, column=c, value=col)
aplicar_estilo_header(3, hoja_sm, 6)
sprint_rows = [
    ["Sprint 1","Semanas 1-2","Auth A01-A04 + Health (F09)","5","24","24"],
    ["Sprint 2","Semanas 3-4","Auth A05-A06-A08 + Reservas R01-R04","8","40","64"],
    ["Sprint 3","Semanas 5-6","Auth A07 + Reservas R05-R08 + Refrescos C01-C03","8","43","107"],
    ["Sprint 4","Semanas 7-8","Reservas R09-R10 + Refrescos C04-C06 + Admin F01-F05-F06-F08","8","45","152"],
    ["Sprint 5","Semanas 9-10","Refrescos C07-C08-C09 + Fidelización L01-L05 + Reportes F02-F03-F04-F10","10","46","198"],
    ["Sprint 6","Semanas 11-12","Fidelización L06-L07-L08 + Gimnasio G01-G07 + Reportes F07","11","41","239"],
]
for i, spr in enumerate(sprint_rows, 1):
    r = 3 + i
    for c, val in enumerate(spr, 1):
        hoja_sm.cell(row=r, column=c, value=val)
aplicar_estilo_celdas(4, 9, hoja_sm, 6)
for r in range(4, 10):
    hoja_sm.row_dimensions[r].height = 28
ajustar_anchos(hoja_sm,[12,28,60,15,25,25])
# Fila TOTAL:
hoja_sm.cell(row=11, column=1, value="TOTALES:").font = FUENTE_HITO
hoja_sm.cell(row=11, column=4, value=52).font = FUENTE_HITO
hoja_sm.cell(row=11, column=5, value=239).font = FUENTE_HITO

# ============================================================
# GUARDAR ARCHIVO EXCEL
# ============================================================
OUT_DIR = r"c:\Users\gusta\OneDrive - UNIR\TRABAJOS DE GRADO\TRABAJOS DE GRADO\UAN\LUIS\SCRUM_DOCS"
import os
salida = os.path.join(OUT_DIR, "HISTORIAS_USUARIO_Y_PRODUCT_BACKLOG.xlsx")
WB.save(salida)
print("EXCEL GENERADO OK:", salida)
print("Hojas:", WB.sheetnames)
