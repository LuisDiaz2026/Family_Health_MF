# MANUAL DE USUARIO - Club Family Health MF
### Versión 1.0 · Trabajo de Grado - Ingeniería de Sistemas y Computación - Universidad Antonio Nariño - Periodo Académico 2026-2
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

El software corre localmente en el PC del club o de pruebas. **Para acceder desde un celular en la misma red Wi-Fi del club, usa la IP privada del PC (no 127.0.0.1).**

### Opción A: En el mismo computador que ejecuta el servidor
1. Abre la carpeta `C:\Family_Health_MF\`
2. Haz **doble clic** en **`arrancar.bat`**
3. Se abrirán dos ventanas negras de consola. **No las cierres** (son el backend y el frontend).
4. Espera 15 segundos, luego en tu navegador (Chrome/Safari/Edge) abre:
   - **Frontend (todos los usuarios):** http://127.0.0.1:5173/
   - **Panel Admin Django (solo personal):** http://127.0.0.1:8000/admin/

### Opción B: Desde tu celular o tablet en la MISMA RED WI-FI del club (Mobile-First)
1. En el PC servidor, **averigua tu IP privada LAN**:
   - Abre PowerShell y escribe: `ipconfig`
   - Busca en "Adaptador Wi-Fi" la línea **Dirección IPv4**: suele ser `192.168.1.XX`, `192.168.0.XX` o `10.0.0.XX` (anótala, p.ej. `192.168.1.42`)
2. En el PC servidor, **detén Vite y levántalo permitiendo conexiones externas** (solo la primera vez):
   - En el archivo `frontend\vite.config.js`, modifica la sección `server` para que quede así:
     ```js
     server: { port: 5173, host: "0.0.0.0", strictPort: true }
     ```
   - Haz lo mismo con Django en `backend\config\settings.py` añadiendo tu IP a `ALLOWED_HOSTS`:
     ```py
     ALLOWED_HOSTS = ["127.0.0.1", "localhost", "192.168.1.42"]  # <- reemplaza por tu IP
     ```
3. Reinicia `arrancar.bat` (cierra las 2 ventanas y vuelve a dar doble clic).
4. **En el celular, conectado al MISMO Wi-Fi del club**, abre Chrome/Safari y navega a:
   - `http://192.168.1.42:5173/`  ← **reemplaza 192.168.1.42 por TU IP real**

> Si no carga: espera 10 segundos y actualiza. Las dos ventanas CMD deben permanecer abiertas todo el tiempo. Si el firewall de Windows pregunta, marca "Permitir en redes privadas".

---

## 3. Crear una cuenta de Cliente

1. Entra a la URL del Frontend (127.0.0.1 en el PC o la IP LAN en el celular).
2. Pulsa **Crear cuenta**.
3. Rellena **TODOS** los campos (nombres, apellidos, usuario, email, tipo + número doc, celular, contraseña x2).
4. ✅ Marca **Acepto Política de Privacidad Ley 1581** (OBLIGATORIO — sin esto no te deja registrarte).
5. Pulsa **Crear cuenta**. ¡Listo! Serás redirigido/a automáticamente.

---

## 4. Iniciar sesión

> ⚠️ **ADVERTENCIA ENTORNO DE PRUEBAS:** Los usuarios que aparecen a continuación son **usuarios de demostración (seed data)** creados para evaluar el sistema en un entorno aislado. **Nunca utilices estas credenciales en un entorno de producción accesible por internet.** En el club real deberás crear cuentas con contraseñas propias y seguras, y jamás publicar las credenciales de administración en documentos, manuales o el código fuente.

| Tipo de usuario | Usuario DEMO | Contraseña DEMO (solo entorno pruebas) |
|---|---|---|
| 👑 Administrador Total | `admin_fh` | (configurar internamente en recepción) |
| 🧑‍💼 Recepción / Barra | `recepcion_fh` | (configurar internamente en recepción) |
| 🏋️ Cliente de prueba 1 | `cliente1_fh` | (solo pruebas internas) |
| 🏋️ Cliente de prueba 2 | `cliente2_fh` | (solo pruebas internas) |
| 🏋️ Cliente de prueba 3 | `cliente3_fh` | (solo pruebas internas) |

> Para ejecutar las pruebas humo del sistema (14 tests automáticos) y consultar los usuarios seed reales, consúltalo con el administrador del proyecto o revisa el script `backend/bootstrap_data.py` y `backend/smoke_test.py`. **La pantalla de login NO muestra credenciales públicas**, son solo para uso del equipo de desarrollo y validación.

**Paso a paso inicio sesión:**
1. Escribe tu **usuario** (no email).
2. Escribe tu **contraseña** (usa el ojo 👁️ para mostrarla).
3. (Opcional) Marca **Recordarme en este equipo** para no volver a ingresar la próxima vez (solo en equipos privados, NO en celulares compartidos).
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
➡️ El sistema implementa una **validación de disponibilidad a nivel de aplicación** mediante el método `Space.is_available_at()` (consulta de solapamiento `start_time < fin_solicitado AND end_time > inicio_solicitado`), combinado con una transacción atómica `transaction.atomic()` en el `save()` de la reserva (models.py línea 459). **Esta validación es efectiva en escenarios normales de uso en el club**, pero tiene dos limitaciones técnicas que deben conocerse para usarlo en producción:
1. En **SQLite (entorno de desarrollo local)** el motor no implementa bloqueos de fila `SELECT ... FOR UPDATE` al mismo nivel que PostgreSQL; en escenarios de concurrencia EXTREMA (dos usuarios pulsando "Confirmar reserva" al milisexacto en el mismo slot) podría darse una ventana de solapamiento.
2. Actualmente **no existe un Exclusion Constraint a nivel de base de datos** (ej: PostgreSQL `btree_gist` sobre `space, tstzrange(start_time, end_time)`) que bloquee a nivel motor cualquier solapamiento parcial. La protección actual se realiza en la capa de aplicación (Django ORM).
➡️ **Recomendación para producción:** migrar a PostgreSQL 16 y añadir un Exclusion Constraint `USING gist (space_id WITH =, tstzrange(start_time, end_time) WITH &&)` para garantía al 100.00% incluso ante concurrencia extrema. Esto está contemplado como mejora para versiones posteriores.
➡️ **Pruébalo ahora:** si intentas reservar dos veces el mismo espacio en el mismo horario, la segunda recibirá el mensaje "Conflicto: Espacio no disponible en horario solicitado".

**❓ ¿Se pierde mi carrito si cierro la pestaña?**
➡️ No. Se guarda en `localStorage` del navegador (vuelve intacto).

**❓ ¿Cómo paso de Bronce a Plata?**
➡️ Junta **500 puntos** (reservas confirmadas, pedidos pagados). Se actualiza automáticamente al próximo login.

**❓ Me equivoqué en una reserva. ¿Qué hago?**
➡️ Entra a la reserva y pulsa **Cancelar** (gratis si faltan >24 horas, consulta política del club para cancelaciones tardías).

**❓ Las ventanas CMD aparecen y desaparecen al abrir arrancar.bat**
➡️ Abre la carpeta Family_Health_MF, clic derecho → "Abrir ventana de PowerShell aquí" y escribe `.\arrancar.bat` para ver el error.

---

## 8. Contacto y Datos del Proyecto

Este manual forma parte del **Trabajo de Grado en Ingeniería de Sistemas y Computación** de la **Universidad Antonio Nariño (UAN)**, sede Maicao, La Guajira, Colombia. El periodo académico de presentación es **2026-2**.

| Datos Proyecto | Valor |
|---|---|
| Autor | **Luis Fermín Díaz Choles** |
| Correo | `luis.diaz@uan.edu.co` (institucional) |
| Programa | Ingeniería de Sistemas y Computación |
| Universidad | **Universidad Antonio Nariño (UAN)** - Maicao, La Guajira |
| Empresa socia | **Club Family Health** · NIT 32739028-5 · Maicao · La Guajira |
| Metodología | Scrum 4 Sprints · 12 semanas académicas |
| Roles Scrum acordados (Anteproyecto Tabla 5) | PO = Club Family Health · SM = Director Tesis · Developer = L. F. Díaz |

---

### Anexo: Accesos de Referencia (ENTORNO PRUEBAS LOCAL - NO PRODUCCIÓN)

| Recurso | URL (Equipo local PC servidor) | Credencial DEMO |
|---|---|---|
| App Web Cliente / Staff | http://127.0.0.1:5173/ | Cuenta propia de cada usuario |
| Panel Admin Django | http://127.0.0.1:8000/admin/ | Solo personal autorizado por el club |
| API REST Base | http://127.0.0.1:8000/api/v1/ | JWT Bearer token después de login |
| Health Check (sin auth) | http://127.0.0.1:8000/api/v1/health/ | Público |
| Acceso móvil red local | `http://[TU_IP_LAN]:5173/` | Igual que app web |

---

**¡Gracias por usar Club Family Health MF!** 🏋️⚽🏊‍♀️🥤
