<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-club-gray-100 to-club-gray-200 px-5">
    <div class="text-center max-w-md">
      <div class="text-9xl font-black bg-gradient-to-r from-club-blue via-sky-700 to-club-green bg-clip-text text-transparent">
        404
      </div>
      <h1 class="mt-2 text-2xl font-black text-club-gray-900">Página no encontrada</h1>
      <p class="mt-2 text-sm text-club-gray-600">
        La ruta que buscas no existe o fue movida. Por favor usa la navegación inferior o regresa al inicio.
      </p>
      <button class="btn-primary mt-6 !px-6" @click="$router.replace({ name: 'root' })">
        Volver al inicio
      </button>
    </div>
  </div>
</template>
