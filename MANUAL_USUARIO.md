# MANUAL DE USUARIO - Club Family Health MF
### Versión 1.0 · TFM Universidad Antonio Nariño
#### Por: Luis Fermín Díaz Choles

---

## Índice

1. [¿Qué es Club Family Health MF?](#1-qué-es-club-family-health-mf)
2. [Primeros pasos: Iniciar la aplicación](#2-primeros-pasos-iniciar-la-aplicación)
3. [Crear una cuenta de Cliente](#3-crear-una-cuenta-de-cliente)
4. [Iniciar sesión](#4-iniciar-sesión)
5. [Zona Cliente - Menú inferior](#5-zona-cliente---menú-inferior)
   - 5.1 Inicio
   - 5.2 Mis Reservas
   - 5.3 Refrescos
   - 5.4 Mis Puntos
   - 5.5 Gimnasio
   - 5.6 Perfil y Notificaciones
6. [Zona Staff (ADMIN / Recepción) - Menú inferior](#6-zona-staff-admin--recepción---menú-inferior)
   - 6.1 Panel principal
   - 6.2 Gestión de Reservas
   - 6.3 Pedidos de Barra
   - 6.4 Clientes
   - 6.5 Inventario (Productos + Espacios)
   - 6.6 Reportes operativos
7. [Preguntas frecuentes (FAQ)](#7-preguntas-frecuentes-faq)
8. [Contacto](#8-contacto)

---

## 1. ¿Qué es Club Family Health MF?

Es una aplicación web mobile-first (optimizada para celulares) del Club Family Health de Maicao. Con ella podrás:

✅ **Reservar** canchas, piscinas, salones y espacios del club (sin cruces de horario).
✅ **Comprar** snacks, bebidas y almuerzos en la barra (con descuento automático por nivel).
✅ **Ganar puntos** por cada reserva/pedido y canjear premios.
✅ **Consultar** rutinas del gimnasio con calorías, sets, descansos.
✅ (ADMIN / Recepción) Controlar todo el club desde un solo panel.

Todo **100% presencial** — no hay pagos online, tu pagas en recepción o barra.

---

## 2. Primeros pasos: Iniciar la aplicación

El software solo corre en el PC del club o de pruebas:

1. Abre la carpeta `C:\Family_Health_MF\`
2. Haz **doble clic** en **`arrancar.bat`**
3. Se abrirán dos ventanas negras de consola. **No las cierres** (son el backend y el frontend).
4. Espera 15 segundos, luego en tu navegador (Chrome/Safari/Edge) abre:
   - **Frontend (todos los usuarios):** http://127.0.0.1:5173/
   - **Panel Admin Django (solo personal):** http://127.0.0.1:8000/admin/

> Si no carga: espera 10 segundos y actualiza (F5). Las dos ventanas CMD deben permanecer abiertas todo el tiempo.

---

## 3. Crear una cuenta de Cliente

1. Entra a http://127.0.0.1:5173/
2. Pulsa **Crear cuenta**.
3. Rellena **TODOS** los campos (nombres, apellidos, usuario, email, tipo + número doc, celular, contraseña x2).
4. ✅ Marca **Acepto Política de Privacidad Ley 1581** (OBLIGATORIO — sin esto no te deja registrarte).
5. Pulsa **Crear cuenta**. ¡Listo! Serás redirigido/a automáticamente.

---

## 4. Iniciar sesión

Usuarios **DEMO** para pruebas (todos visibles en la pantalla login):

| Tipo de usuario | Usuario | Contraseña |
|---|---|---|
| 👑 Administrador Total | `admin_fh` | `AdminFH2026*!` |
| 🧑‍💼 Recepción / Barra | `recepcion_fh` | `RecepcionFH2026*!` |
| 🏋️ Cliente #1 | `cliente1_fh` | `Cliente1FH*!` |
| 🏋️ Cliente #2 | `cliente2_fh` | `Cliente2FH*!` |
| 🏋️ Cliente #3 | `cliente3_fh` | `Cliente3FH*!` |

**Paso a paso:**
1. Escribe tu **usuario** (no email).
2. Escribe tu **contraseña** (usa el ojo 👁️ para mostrarla).
3. (Opcional) Marca **Recordarme en este equipo** para no volver a ingresar la próxima vez.
4. Pulsa **Ingresar**.

---

## 5. Zona Cliente - Menú inferior

Cuando entras como CLIENTE verás 5 botones abajo:
**🏠 Inicio · 📅 Reservas · 🥤 Refrescos · 🏆 Puntos · 💪 Gimnasio**

### 5.1 🏠 Inicio
- Saludo personalizado + membresía + puntos actuales.
- 4 botones **rápidos** (Reservar, Refrescos, Puntos, Gimnasio).
- Tus **3 reservas más recientes** (y botón "Ver todas").
- **Ofertas destacadas** de refresquería (desliza horizontalmente).
- **Rutina recomendada del día** (entra directo al detalle).

### 5.2 📅 Reservas
- Pulsa **+ Nueva Reserva** para abrir el asistente.
- **Filtros scrolleables** (Todas / Pendientes / Confirmadas / Completadas / Canceladas).
- Cada reserva tiene un botón **Cancelar** si aún no está completada.

**Asistente 3 pasos:**
1. **Elige espacio**: Cancha fútbol, piscina, salones… verás tarifa/hora y si requiere aprobación de recepción.
2. **Elige fecha** (solo fechas futuras).
3. **Elige horario**: slots de 30/60 minutos verdes = libre.
4. (Final) Ajusta cuántas personas, pulsa **Confirmar Reserva**.

### 5.3 🥤 Refrescos
- Buscador arriba 🔍 + chips categorías (Todos, Bebidas Frías, Calientes, Snacks, Comidas, Postres).
- Tarjetas de producto con foto, stock, alergenos, precio.
- Botones `−` y `+` para añadir al carrito.
- **🛒 Botón carrito (arriba derecha)** → entra al checkout.
- En el checkout verás:
  - Subtotal.
  - ✅ Descuento fidelidad (aplicado automáticamente según tu nivel).
  - Método de pago (todos presenciales: Efectivo, Transferencia, Tarjeta, Prepagada).
  - Campo notas (ej. "sin cebolla", "vaso extra hielo").
- Pulsa **Confirmar pedido** → recibes número de pedido y puedes ver el estado (Preparando → Listo → Pagado/Entregado).

### 5.4 🏆 Mis Puntos
Arriba tienes 2 pestañas (cambian pulsando):

**⭐ Recompensas (catálogo)**
- Cada premio muestra el nombre, foto, puntos que cuesta.
- Si tienes suficientes puntos → botón **Canjear** habilitado (verde).
- Si no → botón deshabilitado (gris) y mensaje de cuántos puntos te faltan.
- Al canjear: Toast éxito ✅ "Dirígete a recepción para reclamar".
- Los puntos se descuentan automáticamente.

**📈 Mi Fidelidad**
- Tarjeta gradiente de tu nivel actual (Bronce = café, Plata = plata, Oro = dorado, Diamante = celeste pálido).
- 3 KPIs: Puntos actuales · % Descuento · Amigos invitados.
- **Barra progreso % hacia próximo nivel** (actualizado en tiempo real).
- Reglas para ganar puntos (ej. "+20 por reserva confirmada").
- Movimientos recientes (ganado → verde ↑, canjeado → rojo ↓).

### 5.5 💪 Gimnasio
- 6 botones filtro por objetivo (Todos, Fuerza, Hipertrofia, Definición, Pérdida, General).
- Tarjetas de rutina: color por objetivo + 3 KPIs (ejercicios, días/sem, semanas).
- Pulsa una rutina → **Detalle**:
  - Header gradiente color objetivo.
  - 4 KPIs (días/semana, semanas, nivel, nº ejercicios).
  - Calentamiento (lista).
  - **Ejercicios numerados**: Sets · Repeticiones · Descanso · Dificultad (chip).
  - Enfriamiento (lista).
  - Tips nutricionales finales.

### 5.6 👤 Perfil y 🔔 Notificaciones
- **Arriba derecha de todas las pantallas** → botón 🔔 con badge azul (notificaciones NO leídas).
  - Cada notificación tiene un color por tipo (reserva, pedido, recompensa, puntos, info, aviso).
  - Clic sobre ella → se marca como leída, desaparece el punto azul.
- **Botón iniciales (arriba derecha)** → **Mi Perfil**:
  - Avatar iniciales (p.ej. "JG" para Juan Gómez).
  - Datos personales (cédula, celular, email, membresía).
  - Tarjeta fidelidad (y link directo a Fidelidad).
  - Bloque Seguridad Ley 1581 (Argon2, JWT, auditoría).
  - Botón **Cerrar sesión** (rojo).

---

## 6. Zona Staff (ADMIN / Recepción) - Menú inferior

Al iniciar con `admin_fh` o `recepcion_fh` → menú cambia automáticamente a:
**📊 Panel · 📅 Reservas · 🥡 Pedidos · 👥 Clientes · 📈 Reportes**

### 6.1 📊 Panel (Dashboard principal)
**6 KPIs grandes arriba**:
- Usuarios activos · Clientes registrados · Espacios activos · Reservas totales · Pedidos · Ingresos mes.
- **4 StatBox** estados reservas (Pendientes, Confirmadas, Canceladas, Completadas).
- **📊 Distribución niveles fidelidad** (barras porcentaje clientes Bronce/Plata/Oro/Diamante).
- **🥇 Top 5 Clientes** (puesto 1-5, nombre, # reservas, # pedidos, $ total gastado).
- **4 Acciones rápidas**: Gestionar Reservas, Pedidos Barra, Inventario, Reportes.

### 6.2 📅 Gestión de Reservas
- Filtros estados (Todas, Pendientes, Confirmadas, Completadas, Canceladas).
- Cada reserva: #ID, cliente, espacio, fecha + hora, total.
- Botones según estado:
  - 🟡 Pendiente → **Confirmar** (verde), **Cancelar** (rojo).
  - 🔵 Confirmada → **Marcar completada**, **Cancelar**, **Marcar pagada**.
  - 🟢 Completada → sin acciones, solo lectura.

### 6.3 🥡 Pedidos de Barra
- Filtros 6 estados: Todos/Pendientes/Preparando/Listos/Pagados/Cancelados.
- Cada pedido: #, cliente, fecha, items, total, método pago.
- Botones flujo barra:
  - **Preparar** → **Listo para retirar** → **Marcar pagado y entregado**.
  - Cancelar (antes de entrega).

### 6.4 👥 Clientes
- Buscador por nombre / cédula / usuario.
- Tarjetas mini: avatar iniciales + username + cédula + membresía + nivel fidelidad + teléfono.
- Badge Activo/Inactivo.

### 6.5 Inventario (2 secciones en menú hamburguesa staff)
**📦 Productos**:
- Total / Stock bajo / Agotados (3 KPIs arriba).
- Buscador productos.
- Tarjeta cada producto: SKU, categoría, stock/minimo, precio, color chip (OK/Stock bajo/Agotado).

**🏟️ Espacios**:
- Buscador por nombre/código.
- Tarjeta: tarifa/hora, capacidad, antelación días, chip si requiere aprobación o confirmación instantánea.

### 6.6 📈 Reportes operativos
- Resumen (usuarios, clientes, nuevos 30d, reservas total/hoy, pedidos total/hoy).
- 💰 Ingresos (mes reservas, mes barra, TOTAL MES destacado verde).
- 📊 % Ocupación 7 días.
- Puntos distribuidos vs canjeados.
- Distribución por niveles (barras).
- 🥇 **Top 10 clientes ranking** (puesto, avatar, nombre, $ total, # reservas R, # pedidos P).

---

## 7. Preguntas frecuentes (FAQ)

**❓ ¿Puedo pagar con tarjeta online?**
➡️ No. Toda transacción es 100% presencial en recepción/barra.

**❓ ¿Perdí mi contraseña?**
➡️ Comunicate con recepción (admin) en el panel Django Admin para reestablecer.

**❓ ¿Dos reservas quedaron al mismo tiempo en la misma cancha?**
➡️ **Es IMPOSIBLE** — el sistema tiene protección anti-solape a nivel base de datos + `select_for_update`. Si el slot se veía libre y otra persona lo tomó al mismo tiempo, la segunda reserva recibe mensaje "Horario ocupado" automáticamente.

**❓ ¿Se pierde mi carrito si cierro la pestaña?**
➡️ No. Se guarda en `localStorage` del navegador (vuelve intacto).

**❓ ¿Cómo paso de Bronce a Plata?**
➡️ Junta **500 puntos** (reservas confirmadas, pedidos pagados). Se actualiza automáticamente al próximo login.

**❓ Me equivoqué en una reserva. ¿Qué hago?**
➡️ Entra a la reserva y pulsa **Cancelar** (gratis si faltan >24 horas, consulta política del club para cancelaciones tardías).

**❓ Las ventanas CMD aparecen y desaparecen al abrir arrancar.bat**
➡️ Abre la carpeta Family_Health_MF, clic derecho → "Abrir ventana de PowerShell aquí" y escribe `.\arrancar.bat` para ver el error.

---

## 8. Contacto (TFM)

| Datos | Valor |
|---|---|
| Autor TFM | **Luis Fermín Díaz Choles** |
| Correo institucional | `luis.diaz@uan.edu.co` (cambiar por el tuyo real) |
| Programa | Ingeniería de Sistemas |
| Universidad | **Universidad Antonio Nariño (UAN)** - Maicao, La Guajira |
| Empresa real | **Club Family Health** · NIT 32739028-5 · Maicao · La Guajira |

---

### Versiones y credenciales finales recordatorio:

| Recurso | URL | Credencial |
|---|---|---|
| App Cliente/Staff | http://127.0.0.1:5173/ | `cliente1_fh` / `Cliente1FH*!` |
| App Admin | http://127.0.0.1:5173/ | `admin_fh` / `AdminFH2026*!` |
| Django Admin | http://127.0.0.1:8000/admin/ | `admin_fh` / `AdminFH2026*!` |
| API Base URL | http://127.0.0.1:8000/api/v1/ | (JWT Bearer token) |
| Health Check | http://127.0.0.1:8000/api/v1/health/ | Público, sin login |

---

**¡Gracias por usar Club Family Health MF!** 🏋️⚽🏊‍♀️🥤
