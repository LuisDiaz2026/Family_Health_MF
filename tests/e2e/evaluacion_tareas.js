/**
 * Punto 9 - Evaluacion CONTROLADA de tareas mediante navegador.
 *
 * Se denomina "evaluacion controlada de tareas": un script NO puede aportar la
 * percepcion de una persona, por lo que NO se presenta como encuesta SUS ni
 * como opinion de usuarios reales. Solo se registran hechos medibles:
 * tarea, pasos, duracion, resultado, errores y numero de interacciones.
 *
 * Las tareas son deliberadamente no destructivas (no crean ni modifican datos
 * operativos). El escenario destructivo de "registrar una reserva" se mide en
 * el benchmark del punto 7, que limpia sus datos de prueba.
 *
 * Uso:
 *   node tests/e2e/evaluacion_tareas.js
 *
 * Salida:
 *   evidencias/evaluacion_controlada_tareas.csv
 */
const fs = require('fs');
const path = require('path');

const {
  BASE, DIR_EVIDENCIAS, PERFILES,
  abrirNavegador,
} = require('./comun');

const FILAS = [];

function crearMedidor(page) {
  const estado = { interacciones: 0, errores: [], apiFallidas: [] };
  page.on('pageerror', (e) => {
    estado.errores.push(`error de script: ${String(e.message).slice(0, 120)}`);
  });
  page.on('response', (r) => {
    if (r.url().includes('/api/') && r.status() >= 400) {
      const ruta = r.url().split('/api/v1')[1] || r.url();
      estado.apiFallidas.push(`${r.status()} ${ruta.split('?')[0]}`);
    }
  });
  estado.contar = () => { estado.interacciones += 1; };
  return estado;
}

async function tareaLogin(page, med, perfil) {
  const pasos = [];
  await page.goto(`${BASE}/#/login`, { waitUntil: 'domcontentloaded' });
  med.contar(); pasos.push('abrir la pantalla de acceso');
  await page.waitForSelector('input[autocomplete="username"]', { timeout: 30000 });
  await page.fill('input[autocomplete="username"]', PERFILES[perfil].usuario);
  med.contar(); pasos.push('escribir el usuario');
  await page.fill('input[autocomplete="current-password"]', PERFILES[perfil].clave);
  med.contar(); pasos.push('escribir la contrasena');
  await page.click('form button.btn-primary');
  med.contar(); pasos.push('pulsar Ingresar');
  await page.waitForFunction(() => !location.hash.includes('/login'), null,
    { timeout: 30000 });
  await page.waitForTimeout(1500);
  secretosGuardados(perfil);
  return pasos;
}

const SECRETOS_OK = [];
function secretosGuardados(perfil) { SECRETOS_OK.push(perfil); }

async function tareaNavegar(page, med, ruta, descripcion, selectorEsperado) {
  const pasos = [];
  await page.goto(`${BASE}/#${ruta}`, { waitUntil: 'domcontentloaded' });
  med.contar(); pasos.push(`navegar a ${ruta}`);
  await page.waitForTimeout(1200);
  try {
    await page.waitForLoadState('networkidle', { timeout: 12000 });
  } catch (e) { /* la SPA mantiene conexiones */ }
  if (selectorEsperado) {
    await page.waitForSelector(selectorEsperado, { timeout: 20000 });
    med.contar(); pasos.push(`confirmar contenido (${descripcion})`);
  }
  return pasos;
}

async function tareaDisponibilidad(page, med) {
  const pasos = [];
  await page.goto(`${BASE}/#/cliente/reservas/crear`, { waitUntil: 'domcontentloaded' });
  med.contar(); pasos.push('abrir el formulario de reserva');
  await page.waitForTimeout(1500);
  const tarjetas = await page.$$('.grid button.card');
  if (!tarjetas.length) throw new Error('No se listaron espacios para reservar');
  await tarjetas[0].click();
  med.contar(); pasos.push('seleccionar un espacio');
  await page.waitForTimeout(2500);
  const franjas = await page.$$('button[class*="rounded-xl"]');
  pasos.push('consultar las franjas horarias disponibles');
  return { pasos, franjas: franjas.length };
}

const TAREAS = [
  {
    id: 'T01', perfil: 'admin',
    descripcion: 'Iniciar sesion como administrador',
    ejecutar: (p, m) => tareaLogin(p, m, 'admin'),
  },
  {
    id: 'T02', perfil: 'admin',
    descripcion: 'Consultar el panel de indicadores del club',
    iniciarSesion: 'admin',
    ejecutar: (p, m) => tareaNavegar(p, m, '/panel', 'panel de indicadores', 'main, .page-padding'),
  },
  {
    id: 'T03', perfil: 'admin',
    descripcion: 'Listar las reservas registradas',
    iniciarSesion: 'admin',
    ejecutar: (p, m) => tareaNavegar(p, m, '/panel/reservas', 'listado de reservas', '.page-padding'),
  },
  {
    id: 'T04', perfil: 'admin',
    descripcion: 'Consultar el catalogo de espacios',
    iniciarSesion: 'admin',
    ejecutar: (p, m) => tareaNavegar(p, m, '/panel/espacios', 'catalogo de espacios', '.page-padding'),
  },
  {
    id: 'T05', perfil: 'recepcion',
    descripcion: 'Iniciar sesion como recepcion y listar reservas',
    iniciarSesion: 'recepcion',
    ejecutar: (p, m) => tareaNavegar(p, m, '/panel/reservas', 'listado de reservas', '.page-padding'),
  },
  {
    id: 'T06', perfil: 'cliente',
    descripcion: 'Iniciar sesion como cliente y consultar sus reservas',
    iniciarSesion: 'cliente',
    ejecutar: (p, m) => tareaNavegar(p, m, '/cliente/reservas', 'mis reservas', '.page-padding'),
  },
  {
    id: 'T07', perfil: 'cliente',
    descripcion: 'Consultar disponibilidad y abrir el formulario de reserva',
    iniciarSesion: 'cliente',
    ejecutar: (p, m) => tareaDisponibilidad(p, m),
  },
];

async function main() {
  if (!PERFILES.admin.clave || !PERFILES.cliente.clave || !PERFILES.recepcion.clave) {
    throw new Error('Faltan credenciales en .env.evidencias.');
  }
  const navegador = await abrirNavegador();

  for (const tarea of TAREAS) {
    const contexto = await navegador.newContext({
      viewport: { width: 390, height: 844 }, isMobile: true,
    });
    const page = await contexto.newPage();
    const med = crearMedidor(page);
    const t0 = Date.now();
    let pasos = [];
    let resultado = 'COMPLETADA';
    let observacion = '';
    try {
      if (tarea.iniciarSesion) {
        pasos = pasos.concat(await tareaLogin(page, med, tarea.iniciarSesion));
      }
      const r = await tarea.ejecutar(page, med);
      if (Array.isArray(r)) {
        pasos = pasos.concat(r);
      } else if (r && r.pasos) {
        pasos = pasos.concat(r.pasos);
        if (r.franjas !== undefined) observacion = `franjas detectadas: ${r.franjas}`;
      }
    } catch (e) {
      resultado = 'NO COMPLETADA';
      observacion = String(e.message || e).slice(0, 160);
    }
    const duracion = (Date.now() - t0) / 1000;
    const errores = med.errores.length + med.apiFallidas.length;
    FILAS.push({
      id: tarea.id,
      perfil: tarea.perfil,
      dispositivo: 'Movil 390x844 (emulado)',
      tarea: tarea.descripcion,
      pasos: pasos.length,
      detalle_pasos: pasos.join(' | '),
      duracion_s: duracion.toFixed(2),
      resultado,
      errores,
      detalle_errores: med.errores.concat(med.apiFallidas).join(' | ').slice(0, 200),
      interacciones: med.interacciones,
      observacion,
    });
    console.log(`[TAREA] ${tarea.id} ${tarea.perfil} -> ${resultado} `
      + `pasos=${pasos.length} interacciones=${med.interacciones} `
      + `duracion=${duracion.toFixed(2)}s errores=${errores}`);
    await contexto.close();
  }

  await navegador.close();
  exportar();
  const fallos = FILAS.filter((f) => f.resultado !== 'COMPLETADA').length;
  console.log('='.repeat(74));
  console.log(`RESUMEN TAREAS: ${FILAS.length} tareas, ${fallos} no completadas`);
  return fallos === 0 ? 0 : 1;
}

function exportar() {
  const campos = ['id', 'perfil', 'dispositivo', 'tarea', 'pasos', 'detalle_pasos',
    'duracion_s', 'resultado', 'errores', 'detalle_errores', 'interacciones',
    'observacion'];
  const escapar = (v) => {
    const s = v === undefined || v === null ? '' : String(v);
    return /[",;\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const lineas = [campos.join(',')];
  for (const f of FILAS) lineas.push(campos.map((c) => escapar(f[c])).join(','));
  fs.writeFileSync(path.join(DIR_EVIDENCIAS, 'evaluacion_controlada_tareas.csv'),
    '\ufeff' + lineas.join('\r\n'), 'utf8');
  console.log(`CSV: ${path.join(DIR_EVIDENCIAS, 'evaluacion_controlada_tareas.csv')}`);
}

main().then((c) => process.exit(c)).catch((e) => {
  console.error('ERROR FATAL:', e.message);
  process.exit(2);
});
