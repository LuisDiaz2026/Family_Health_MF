/**
 * Utilidades compartidas para las pruebas de navegador (puntos 8 y 9).
 *
 * Las credenciales NO se escriben en el codigo: se leen de `.env.evidencias`
 * (ignorado por Git) o de variables de entorno FH_*.
 */
const fs = require('fs');
const path = require('path');

const RAIZ = path.resolve(__dirname, '..', '..');
const ARCHIVO_CREDENCIALES = path.join(RAIZ, '.env.evidencias');

function leerCredenciales() {
  const valores = {};
  if (!fs.existsSync(ARCHIVO_CREDENCIALES)) return valores;
  for (const linea of fs.readFileSync(ARCHIVO_CREDENCIALES, 'utf8').split(/\r?\n/)) {
    const t = linea.trim();
    if (!t || t.startsWith('#') || !t.includes('=')) continue;
    const i = t.indexOf('=');
    valores[t.slice(0, i).trim()] = t.slice(i + 1).trim().replace(/^["']|["']$/g, '');
  }
  return valores;
}

const ARCH = leerCredenciales();

function cfg(clave, defecto = '') {
  return process.env[clave] || ARCH[clave] || defecto;
}

const BASE = cfg('FH_BASE', 'https://familyhealthmf-production.up.railway.app').replace(/\/+$/, '');
const DIR_EVIDENCIAS = path.join(RAIZ, 'evidencias');
const DIR_MOBILE = path.join(DIR_EVIDENCIAS, 'mobile');

const PERFILES = {
  admin: { usuario: cfg('FH_USER_ADMIN', 'admin_fh'), clave: cfg('FH_PASS_ADMIN') },
  recepcion: { usuario: cfg('FH_USER_RECEPCION', 'recepcion_fh'), clave: cfg('FH_PASS_RECEPCION') },
  cafeteria: { usuario: cfg('FH_USER_CAFETERIA', 'cafeteria_fh'), clave: cfg('FH_PASS_CAFETERIA') },
  cliente: { usuario: cfg('FH_USER_CLIENTE1', 'cliente1_fh'), clave: cfg('FH_PASS_CLIENTE1') },
};

/** Lanza Chromium usando el navegador del sistema (no descarga binarios). */
async function abrirNavegador() {
  const { chromium } = require('playwright');
  for (const canal of ['msedge', 'chrome']) {
    try {
      return await chromium.launch({ channel: canal, headless: true });
    } catch (e) {
      /* se intenta el siguiente canal */
    }
  }
  return chromium.launch({ headless: true });
}

/** Inicia sesion por la interfaz real y espera a salir de la pantalla de login. */
async function iniciarSesion(page, usuario, clave) {
  await page.goto(`${BASE}/#/login`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('input[autocomplete="username"]', { timeout: 30000 });
  await page.fill('input[autocomplete="username"]', usuario);
  await page.fill('input[autocomplete="current-password"]', clave);
  await page.click('form button.btn-primary');
  await page.waitForFunction(() => !location.hash.includes('/login'), null,
    { timeout: 30000 });
  await page.waitForTimeout(1800);
}

/** Espera a que la pantalla deje de mostrar esqueletos de carga. */
async function esperarPantalla(page) {
  await page.waitForTimeout(1500);
  try {
    await page.waitForLoadState('networkidle', { timeout: 15000 });
  } catch (e) {
    /* la SPA puede mantener conexiones; se continua */
  }
}

/** Mide el layout real de la pantalla cargada. */
async function medirPantalla(page) {
  return page.evaluate(() => {
    const de = document.documentElement;
    const ancho = window.innerWidth;
    const alto = window.innerHeight;
    const scrollW = Math.max(de.scrollWidth, document.body ? document.body.scrollWidth : 0);
    const overflow = Math.max(0, scrollW - ancho);
    const botones = Array.from(document.querySelectorAll('button'))
      .map((b) => b.getBoundingClientRect())
      .filter((r) => r.width > 0 && r.height > 0);
    const altos = botones.map((r) => Math.round(r.height));
    return {
      ancho,
      alto,
      scrollWidth: scrollW,
      overflow,
      totalElementos: document.querySelectorAll('*').length,
      botones: botones.length,
      botonMinAlto: altos.length ? Math.min(...altos) : 0,
      campos: document.querySelectorAll('input, select, textarea').length,
      tablas: document.querySelectorAll('table').length,
      modales: document.querySelectorAll('[role="dialog"], .modal, .overlay').length,
    };
  });
}

module.exports = {
  BASE, DIR_EVIDENCIAS, DIR_MOBILE, PERFILES,
  cfg, abrirNavegador, iniciarSesion, esperarPantalla, medirPantalla,
};
