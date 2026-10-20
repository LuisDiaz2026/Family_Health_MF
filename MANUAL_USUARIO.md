# Manual de Usuario - Family Health MF

## 1. Presentación

Este manual describe el uso de la versión final del aplicativo web **Family Health MF**, desarrollado para la gestión centralizada de reservas y módulos complementarios del Club Family Health. El documento se redacta con base en la interfaz realmente implementada y en las capturas verificadas durante las pruebas Mobile-First ejecutadas sobre el despliegue productivo.

**Datos generales**

- **Proyecto:** Family Health MF
- **Autor:** Luis Fermín Díaz Choles
- **Programa:** Ingeniería de Sistemas y Computación
- **Universidad:** Universidad Antonio Nariño, sede Maicao
- **Versión funcional verificada:** despliegue productivo con validación real en Railway
- **URL pública del sistema:** `https://familyhealthmf-production.up.railway.app/#/login`

## 2. Propósito del sistema

Family Health MF permite centralizar la operación del club en una sola aplicación, con acceso diferenciado por rol. En su versión final, el sistema permite:

- autenticación con control de acceso por roles;
- registro público de clientes;
- consulta de espacios y disponibilidad;
- creación y cancelación de reservas;
- administración operativa de reservas, clientes, productos, ofertas, espacios y reportes;
- uso en resoluciones móviles y de escritorio sin desbordamiento horizontal injustificado.

## 3. Acceso al aplicativo

El ingreso a la versión final se realiza desde un navegador web moderno. La dirección de acceso validada es:

```text
https://familyhealthmf-production.up.railway.app/#/login
```

La aplicación utiliza enrutamiento con hash, por lo que las pantallas principales se identifican con rutas como:

- `#/login`
- `#/cliente`
- `#/cliente/reservas`
- `#/cliente/reservas/crear`
- `#/cliente/refrescos`
- `#/panel`
- `#/panel/reservas`
- `#/panel/productos`
- `#/panel/espacios`

## 4. Roles de uso

El sistema trabaja con roles diferenciados. Cada rol visualiza únicamente las pantallas y acciones autorizadas.

| Perfil | Módulos habilitados |
| --- | --- |
| Cliente | Panel, Reservas, Refresquería, Puntos, Gimnasio y Perfil |
| Administrador | Panel, Reservas, Clientes, Productos, Espacios, Ofertas y Reportes |
| Recepción | Reservas, Clientes y Espacios |
| Cafetería | Pedidos, Productos y Ofertas |

### 4.1 Cliente

El cliente puede:

- iniciar sesión;
- consultar su panel de inicio;
- revisar sus reservas;
- crear una nueva reserva;
- consultar el catálogo de refresquería y gestionar su carrito;
- consultar sus puntos de fidelidad, las rutinas de gimnasio y su perfil.

### 4.2 Administrador

El administrador puede:

- acceder al panel general del club;
- gestionar reservas y clientes;
- administrar productos (inventario), ofertas y espacios;
- acceder a reportes operativos.

### 4.3 Recepción y cafetería

Los roles de recepción y cafetería están restringidos a sus módulos operativos. Recepción gestiona reservas y consulta clientes y espacios; cafetería administra pedidos, productos y ofertas. En la validación final se confirmó que la recepción puede consultar el listado de reservas y que el cliente no puede acceder al panel administrativo.

## 5. Ingreso al sistema

Para iniciar sesión:

1. Abra la URL pública del aplicativo.
2. Escriba su nombre de usuario.
3. Escriba su contraseña.
4. Pulse el botón **Ingresar**.

Si el usuario pertenece al rol cliente, el sistema lo redirige a la zona cliente. Si pertenece a un rol operativo, el sistema lo redirige a su panel autorizado.

## 6. Registro de cliente

El registro público está disponible desde la pantalla de acceso mediante la opción **Crear cuenta**. El proceso requiere diligenciar los datos personales y aceptar la política de privacidad. La aceptación de dicha política es obligatoria; si no se marca, el sistema rechaza el registro.

La cuenta creada mediante registro público queda sujeta al flujo de activación definido por la administración del club.

## 7. Funcionamiento por perfil y por pantalla

Las descripciones se organizan según el perfil de usuario y corresponden a pantallas realmente verificadas durante las pruebas automatizadas de navegador y Mobile-First.

### 7.1 Acceso (común a todos los perfiles)

La pantalla de acceso presenta el formulario de autenticación y el enlace hacia el registro de clientes. Desde aquí inicia cualquier flujo del sistema. El usuario ingresa sus credenciales y, tras autenticarse, es redirigido a la interfaz correspondiente a su rol.

### 7.2 Perfil Cliente

- **Panel del cliente.** Muestra el resumen de puntos, nivel de fidelidad y membresía, los accesos rápidos (Reservar, Refrescos, Puntos y Gimnasio), la oferta destacada y la rutina recomendada del día.
- **Mis Reservas.** Permite consultar el historial propio de reservas con filtros por estado. Muestra exclusivamente la información del cliente autenticado.
- **Nueva reserva.** Guía la selección de espacio, fecha y franja horaria. El sistema consulta la disponibilidad real y presenta las franjas calculadas por bloques de 30 minutos.
- **Refresquería y carrito.** Presenta los productos del club y permite agregarlos a un carrito para confirmar el pedido.
- **Puntos de fidelidad.** Muestra el nivel alcanzado, los puntos acumulados y las recompensas disponibles.
- **Gimnasio y rutinas.** Presenta las rutinas de ejercicio y el detalle de cada una.
- **Perfil.** Permite consultar los datos de la cuenta y cerrar la sesión de forma segura.

### 7.3 Perfil Administrador

- **Panel administrativo.** Consolida los indicadores operativos del club y los accesos a los módulos de operación.
- **Gestión de reservas.** Permite revisar y gestionar las reservas registradas, con filtros por estado.
- **Gestión de clientes.** Presenta el listado de clientes registrados y su estado.
- **Inventario de productos.** Presenta el catálogo administrable con indicadores de stock y herramientas de consulta.
- **Espacios.** Permite revisar la configuración de los espacios reservables (capacidad, tarifa, reglas y tipo de confirmación).
- **Ofertas.** Permite crear y administrar ofertas vinculadas a productos, con precio, etiqueta y vigencia.
- **Reportes.** Presenta la información consolidada de la operación del club.

### 7.4 Perfil Recepción

Recepción atiende la operación diaria y su menú se limita a **Reservas**, **Clientes** y **Espacios**. Las pantallas coinciden con las del administrador, con las acciones permitidas por su rol. Si intenta acceder a un módulo no autorizado, el sistema responde con un mensaje de acceso denegado.

### 7.5 Perfil Cafetería

Cafetería administra la operación de la refresquería y su menú se limita a **Pedidos**, **Productos** y **Ofertas**. La gestión de productos y ofertas reutiliza las pantallas administrativas correspondientes; el módulo de pedidos permite consultar y gestionar los pedidos generados por los clientes.

## 8. Figuras incorporadas en la versión Word

La versión Word de este manual (documento FIS–UDCII–G06) está organizada por perfiles y utiliza 18 figuras de capturas reales, dimensionadas uniformemente para su correcta apreciación en la hoja. Cuando una pantalla es extensa, la figura muestra únicamente la vista inicial, sin desplazamiento.

### 8.1 Acceso

- Figura 1. `publico_acceso-login` (pantalla de acceso).

### 8.2 Perfil Cliente

- Figura 2. Panel principal del cliente.
- Figura 3. Listado de reservas del cliente.
- Figura 4. Selección del espacio para una nueva reserva.
- Figura 5. Selección de fecha y franja horaria.
- Figura 6. Catálogo de refresquería.
- Figura 7. Carrito de compras.
- Figura 8. Puntos de fidelidad.
- Figura 9. Gimnasio y rutinas.
- Figura 10. Perfil del cliente.

### 8.3 Perfil Administrador

- Figura 11. Panel administrativo.
- Figura 12. Gestión de reservas.
- Figura 13. Gestión de clientes.
- Figura 14. Inventario de productos (vista inicial del catálogo).
- Figura 15. Espacios del club (vista inicial del catálogo).
- Figura 16. Ofertas de la refresquería.
- Figura 17. Reportes del sistema.

### 8.4 Perfil Cafetería

- Figura 18. Pedidos de la cafetería.

### 8.5 Evidencias originales conservadas

Las 36 capturas completas (9 pantallas en 4 resoluciones: 360, 390, 768 y 1280 px) se conservan sin recortes en la carpeta `evidencias/mobile/`. Los recortes del manual se derivaron únicamente de estas imágenes originales y no modifican el contenido funcional mostrado.

## 9. Recomendaciones de uso

- Utilice navegadores actualizados.
- Verifique que el usuario corresponda al rol operativo correcto antes de iniciar sesión.
- Para crear reservas, seleccione siempre una fecha futura y una franja disponible.
- Si una reserva ya no es necesaria, realice la cancelación desde el módulo correspondiente.
- En ambientes institucionales compartidos, cierre la sesión al terminar.

## 10. Preguntas frecuentes

**¿El sistema permite pagos en línea?**  
No. La operación documentada en la versión final corresponde a una atención presencial del club.

**¿El cliente puede ver reservas de otros usuarios?**  
No. La versión final restringe el listado global y ofrece al cliente un acceso solo a sus propias reservas.

**¿Qué ocurre si dos usuarios intentan reservar el mismo espacio en la misma hora?**  
El sistema rechaza la segunda solicitud cuando existe solapamiento, lo cual fue comprobado en pruebas locales, benchmark controlado, smoke test y validación sobre Railway.

**¿La interfaz funciona en celular?**  
Sí. Se verificaron resoluciones de 360 px, 390 px, 768 px y 1280 px, con 36 combinaciones aprobadas y 0 px de desbordamiento horizontal injustificado.

## 11. Cierre

Este manual documenta el uso real de la versión final del aplicativo Family Health MF y sirve como base para la guía en Word (documento FIS–UDCII–G06), organizada por perfiles de usuario. La evidencia visual utilizada proviene de la carpeta `evidencias/mobile/`, generada durante las pruebas finales de usabilidad técnica y validación Mobile-First.
