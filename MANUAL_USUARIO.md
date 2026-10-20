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

### 4.1 Cliente

El cliente puede:

- iniciar sesión;
- consultar su panel de inicio;
- revisar sus reservas;
- crear una nueva reserva;
- consultar el catálogo de refresquería.

### 4.2 Administrador

El administrador puede:

- acceder al panel general del club;
- gestionar reservas;
- consultar productos;
- consultar espacios;
- acceder a reportes operativos.

### 4.3 Recepción y cafetería

Los roles de recepción y cafetería están restringidos a sus módulos operativos. En la validación final se confirmó que la recepción puede consultar el listado de reservas y que el cliente no puede acceder al panel administrativo.

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

## 7. Funcionamiento por pantallas

Las siguientes descripciones corresponden a pantallas realmente verificadas durante las pruebas automatizadas de navegador y Mobile-First.

### 7.1 Pantalla de acceso

La pantalla de acceso presenta el formulario de autenticación y el enlace hacia el registro de clientes. Desde aquí inicia cualquier flujo del sistema. El usuario ingresa sus credenciales y, tras autenticarse, es redirigido a la interfaz correspondiente a su rol.

### 7.2 Panel del cliente

El panel del cliente muestra la información general del usuario autenticado y ofrece accesos rápidos a los módulos principales. Desde esta vista el usuario puede desplazarse hacia reservas, refresquería, fidelización y gimnasio, aunque en la validación visual final se verificaron específicamente las pantallas de inicio, reservas, formulario de reserva y catálogo de refrescos.

### 7.3 Listado de reservas del cliente

El módulo **Mis Reservas** permite consultar el historial propio de reservas. La pantalla ofrece filtros por estado y mantiene visible únicamente la información del cliente autenticado. Durante el cierre técnico se corrigió el acceso a este listado mediante un endpoint específico de consulta de reservas propias.

### 7.4 Formulario de nueva reserva

El formulario de reserva guía al usuario por la selección de espacio, fecha y franja horaria. El sistema consulta la disponibilidad real del espacio y presenta las franjas calculadas por bloques de 30 minutos. En la versión final se corrigió la lectura de esas franjas para que el formulario mostrara correctamente la disponibilidad retornada por la API.

### 7.5 Catálogo de refresquería

La pantalla de refrescos presenta productos agrupados y navegables desde el cliente. Permite consultar la oferta disponible del club y avanzar hacia el flujo de selección de productos.

### 7.6 Panel administrativo

El panel administrativo consolida indicadores operativos del club. Incluye métricas generales, estados de reservas, acciones rápidas y accesos a módulos de operación.

### 7.7 Listado administrativo de reservas

Esta vista permite a los roles autorizados revisar las reservas registradas, su estado y la información básica de cada solicitud. Desde esta pantalla se soporta la gestión operativa del módulo de reservas.

### 7.8 Catálogo administrativo de productos

La pantalla de productos presenta el inventario administrable, acompañado de indicadores de stock y herramientas de consulta. Su diseño fue verificado en las cuatro resoluciones objetivo.

### 7.9 Catálogo administrativo de espacios

La vista de espacios permite revisar la configuración general de los espacios reservables, con información relacionada con capacidad, tarifa y operación.

## 8. Inventario de capturas reales verificadas

La versión Word de este manual incorpora las capturas completas del aplicativo con formato de figura y nota conforme a presentación académica. El inventario base utilizado para esa versión es el siguiente:

### 8.1 Acceso público

- Figura 1. `publico_acceso-login_360x800.png`
- Figura 2. `publico_acceso-login_390x844.png`
- Figura 3. `publico_acceso-login_768x1024.png`
- Figura 4. `publico_acceso-login_1280x800.png`

### 8.2 Panel del cliente

- Figura 5. `cliente_dashboard-cliente_360x800.png`
- Figura 6. `cliente_dashboard-cliente_390x844.png`
- Figura 7. `cliente_dashboard-cliente_768x1024.png`
- Figura 8. `cliente_dashboard-cliente_1280x800.png`

### 8.3 Reservas del cliente

- Figura 9. `cliente_listado-reservas-cliente_360x800.png`
- Figura 10. `cliente_listado-reservas-cliente_390x844.png`
- Figura 11. `cliente_listado-reservas-cliente_768x1024.png`
- Figura 12. `cliente_listado-reservas-cliente_1280x800.png`

### 8.4 Formulario de reserva

- Figura 13. `cliente_formulario-reserva_360x800.png`
- Figura 14. `cliente_formulario-reserva_390x844.png`
- Figura 15. `cliente_formulario-reserva_768x1024.png`
- Figura 16. `cliente_formulario-reserva_1280x800.png`

### 8.5 Catálogo de refrescos

- Figura 17. `cliente_catalogo-refrescos_360x800.png`
- Figura 18. `cliente_catalogo-refrescos_390x844.png`
- Figura 19. `cliente_catalogo-refrescos_768x1024.png`
- Figura 20. `cliente_catalogo-refrescos_1280x800.png`

### 8.6 Panel administrativo

- Figura 21. `admin_dashboard-admin_360x800.png`
- Figura 22. `admin_dashboard-admin_390x844.png`
- Figura 23. `admin_dashboard-admin_768x1024.png`
- Figura 24. `admin_dashboard-admin_1280x800.png`

### 8.7 Reservas administrativas

- Figura 25. `admin_listado-reservas-admin_360x800.png`
- Figura 26. `admin_listado-reservas-admin_390x844.png`
- Figura 27. `admin_listado-reservas-admin_768x1024.png`
- Figura 28. `admin_listado-reservas-admin_1280x800.png`

### 8.8 Productos administrativos

- Figura 29. `admin_productos_360x800.png`
- Figura 30. `admin_productos_390x844.png`
- Figura 31. `admin_productos_768x1024.png`
- Figura 32. `admin_productos_1280x800.png`

### 8.9 Espacios administrativos

- Figura 33. `admin_espacios_360x800.png`
- Figura 34. `admin_espacios_390x844.png`
- Figura 35. `admin_espacios_768x1024.png`
- Figura 36. `admin_espacios_1280x800.png`

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

Este manual documenta el uso real de la versión final del aplicativo Family Health MF y sirve como base para la guía en Word entregada junto con las capturas completas del sistema. La evidencia visual utilizada proviene de la carpeta `evidencias/mobile/`, generada durante las pruebas finales de usabilidad técnica y validación Mobile-First.
