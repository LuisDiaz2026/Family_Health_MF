/**
 * Punto 8 - Pruebas Mobile-First sobre la version final desplegada.
 *
 * Recorre las pantallas representativas en 360, 390, 768 y 1280 px, mide el
 * desbordamiento horizontal real, el tamano de los botones y la presencia de
 * campos, tablas y modales; y guarda una captura por pantalla.
 *
 * Uso:
 *   node tests/e2e/mobile_first.js
 *
 * Salidas:
 *   evidencias/mobile_first.csv
 *   evidencias/mobile/*.png
 */
const fs = require('fs');
const path = require('path');

const {
  BASE, DIR_EVIDENCIAS, DIR_MOBILE, PERFILES,
  abrirNavegador, iniciarSesion, esperarPantalla, medirPantalla,
} = require('./comun');

const RESOLUCIONES = [
  { etiqueta: '360x800', width: 360, height: 800 },
  { etiqueta: '390x844', width: 390, height: 844 },
  { etiqueta: '768x1024', width: 768, height: 1024 },
  { etiqueta: '1280x800', width: 1280, height: 800 },
];

const PANTALLAS = {
  publico: [
    { ruta: '/login', nombre: 'acceso-login' },
  ],
  cliente: [
    { ruta: '/cliente', nombre: 'dashboard-cliente' },
    { ruta: '/cliente/reservas', nombre: 'listado-reservas-cliente' },
    { ruta: '/cliente/reservas/crear', nombre: 'formulario-reserva' },
    { ruta: '/cliente/refrescos', nombre: 'catalogo-refrescos' },
  ],
  admin: [
    { ruta: '/panel', nombre: 'dashboard-admin' },
    { ruta: '/panel/reservas', nombre: 'listado-reservas-admin' },
    { ruta: '/panel/productos', nombre: 'productos' },
    { ruta: '/panel/espacios', nombre: 'espacios' },
  ],
};

const TOLERANCIA_OVERFLOW = 2; // px

async function main() {
  if (!PERFILES.admin.clave || !PERFILES.cliente.clave) {
    throw new Error('Faltan credenciales en .env.evidencias (FH_PASS_ADMIN / FH_PASS_CLIENTE1).');
  }
  fs.mkdirSync(DIR_MOBILE, { recursive: true });

  const navegador = await abrirNavegador();
  const filas = [];

  for (const res of RESOLUCIONES) {
    for (const perfil of Object.keys(PANTALLAS)) {
      const contexto = await navegador.newContext({
        viewport: { width: res.width, height: res.height },
        deviceScaleFactor: 1,
        isMobile: res.width < 768,
      });
      const page = await contexto.newPage();
      try {
        if (perfil !== 'publico') {
          await iniciarSesion(page, PERFILES[perfil].usuario, PERFILES[perfil].clave);
        }
        for (const pantalla of PANTALLAS[perfil]) {
          await page.goto(`${BASE}/#${pantalla.ruta}`, { waitUntil: 'domcontentloaded' });
          await esperarPantalla(page);
          const m = await medirPantalla(page);
          const captura = `mobile/${perfil}_${pantalla.nombre}_${res.etiqueta}.png`;
          await page.screenshot({
            path: path.join(DIR_EVIDENCIAS, captura.replace(/\//g, path.sep)),
            fullPage: true,
          });
          const resultado = m.overflow <= TOLERANCIA_OVERFLOW ? 'PASS' : 'FAIL';
          filas.push({
            resolucion: res.etiqueta,
            ancho_px: m.ancho,
            alto_px: m.alto,
            perfil,
            pantalla: pantalla.nombre,
            ruta: `#${pantalla.ruta}`,
            overflow_horizontal_px: m.overflow,
            total_elementos: m.totalElementos,
            botones: m.botones,
            boton_min_alto_px: m.botonMinAlto,
            campos_formulario: m.campos,
            tablas: m.tablas,
            modales: m.modales,
            resultado,
            captura,
          });
          console.log(`[MOBILE] ${res.etiqueta} ${perfil}/${pantalla.nombre} `
            + `overflow=${m.overflow}px botones=${m.botones} minAlto=${m.botonMinAlto}px ${resultado}`);
        }
      } catch (e) {
        filas.push({
          resolucion: res.etiqueta, ancho_px: res.width, alto_px: res.height,
          perfil, pantalla: '(error)', ruta: '', overflow_horizontal_px: '',
          total_elementos: '', botones: '', boton_min_alto_px: '',
          campos_formulario: '', tablas: '', modales: '',
          resultado: 'FAIL', captura: '',
          observacion: String(e.message || e).slice(0, 180),
        });
        console.error(`[MOBILE][ERROR] ${res.etiqueta} ${perfil}: ${e.message}`);
      } finally {
        await contexto.close();
      }
    }
  }

  await navegador.close();
  exportar(filas);

  const fallos = filas.filter((f) => f.resultado === 'FAIL').length;
  console.log('='.repeat(74));
  console.log(`RESUMEN MOBILE-FIRST: ${filas.length} combinaciones, ${fallos} con fallo`);
  console.log(`CSV: ${path.join(DIR_EVIDENCIAS, 'mobile_first.csv')}`);
  console.log(`Capturas: ${DIR_MOBILE}`);
  return fallos === 0 ? 0 : 1;
}

function exportar(filas) {
  const campos = ['resolucion', 'ancho_px', 'alto_px', 'perfil', 'pantalla', 'ruta',
    'overflow_horizontal_px', 'total_elementos', 'botones', 'boton_min_alto_px',
    'campos_formulario', 'tablas', 'modales', 'resultado', 'captura', 'observacion'];
  const escapar = (v) => {
    const s = v === undefined || v === null ? '' : String(v);
    return /[",;\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const lineas = [campos.join(',')];
  for (const f of filas) lineas.push(campos.map((c) => escapar(f[c])).join(','));
  fs.writeFileSync(path.join(DIR_EVIDENCIAS, 'mobile_first.csv'),
    '\ufeff' + lineas.join('\r\n'), 'utf8');

  const total = filas.length;
  const fallos = filas.filter((f) => f.resultado === 'FAIL');
  const md = [
    '# Pruebas Mobile-First - version final',
    '',
    '> Family Health MF · cierre tecnico · punto 8',
    '',
    `- **URL evaluada:** ${BASE}`,
    `- **Resoluciones:** 360, 390, 768 y 1280 px`,
    `- **Combinaciones ejecutadas (resolucion x pantalla):** ${total}`,
    `- **Con desbordamiento horizontal injustificado:** ${fallos.length}`,
    '',
    'La medicion se realizo con Playwright controlando Microsoft Edge sobre la',
    'version desplegada. `overflow_horizontal_px` es la diferencia real entre',
    '`scrollWidth` del documento y el ancho del viewport; se considera correcto',
    'un valor <= 2 px.',
    '',
    '| Resolucion | Perfil | Pantalla | Overflow (px) | Botones | Alto minimo boton (px) | Campos | Tablas | Modales | Resultado | Captura |',
    '|---|---|---|---|---|---|---|---|---|---|---|',
  ];
  for (const f of filas) {
    md.push(`| ${f.resolucion} | ${f.perfil} | ${f.pantalla} | ${f.overflow_horizontal_px} | `
      + `${f.botones} | ${f.boton_min_alto_px} | ${f.campos_formulario} | ${f.tablas} | `
      + `${f.modales} | **${f.resultado}** | \`${f.captura || '-'}\` |`);
  }
  md.push('', '## Comandos de reproduccion', '', '```powershell',
    'cd c:\\Family_Health_MF\\tests\\e2e',
    'node mobile_first.js',
    '```', '');
  fs.writeFileSync(path.join(DIR_EVIDENCIAS, 'mobile_first.md'), md.join('\n'), 'utf8');
}

main().then((c) => process.exit(c)).catch((e) => {
  console.error('ERROR FATAL:', e.message);
  process.exit(2);
});
