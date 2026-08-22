<template>
  <div class="page-padding space-y-4">
    <button class="inline-flex items-center gap-1 text-club-blue font-bold text-sm hover:underline" @click="$router.back()">
      <ArrowLeft class="w-4 h-4" /> Volver a catálogo
    </button>

    <div class="flex items-center justify-between">
      <div>
        <h1 class="title-page">Mi carrito</h1>
        <p class="subtitle-page">{{ rf.cartCount }} productos</p>
      </div>
      <button v-if="rf.cart.length" class="btn-ghost text-sm" @click="rf.clearCart(); showToast('Carrito vaciado', 'info')">
        <Trash2 class="w-4 h-4" /> Vaciar
      </button>
    </div>

    <EmptyState
      v-if="!rf.cart.length"
      icon="ShoppingCart"
      title="Tu carrito está vacío"
      description="Añade bebidas, snacks y comidas desde el catálogo."
      cta-label="Ir a catálogo"
      @cta="$router.push({ name: 'client-refreshments' })"
    />

    <template v-else>
      <div class="space-y-3">
        <div v-for="it in rf.cart" :key="it.product_id" class="card flex items-center gap-3">
          <div class="w-14 h-14 rounded-lg bg-club-gray-100 flex items-center justify-center">
            <Package class="w-6 h-6 text-club-gray-400" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="font-bold text-sm text-club-gray-900 truncate">{{ it.name }}</div>
            <div class="text-xs text-club-gray-500">Precio: ${{ Number(it.price).toLocaleString('es-CO') }}</div>
          </div>
          <div class="flex items-center gap-1.5">
            <button class="btn-ghost !p-1.5" @click="rf.updateQuantity(it.product_id, it.quantity - 1)"><Minus class="w-4 h-4" /></button>
            <span class="w-6 text-center font-bold">{{ it.quantity }}</span>
            <button class="btn-ghost !p-1.5" @click="rf.updateQuantity(it.product_id, it.quantity + 1)"><Plus class="w-4 h-4" /></button>
          </div>
          <div class="w-20 text-right font-black text-club-gray-900 text-sm">
            ${{ (it.price * it.quantity).toLocaleString('es-CO') }}
          </div>
        </div>
      </div>

      <div class="card bg-gradient-to-br from-club-gray-50 to-white">
        <div class="section-title !mb-3">Resumen del pedido</div>
        <div class="space-y-1.5 text-sm">
          <div class="flex justify-between text-club-gray-600"><span>Subtotal</span><span>${{ rf.cartSubtotal.toLocaleString('es-CO') }}</span></div>
          <div class="flex justify-between text-club-gray-600"><span>Servicio</span><span>$0</span></div>
          <div class="flex justify-between text-club-gray-600"><span>Descuento membresía</span><span>${{ discountAmount.toLocaleString('es-CO') }}</span></div>
          <hr class="my-2" />
          <div class="flex justify-between text-lg font-black text-club-green"><span>Total</span><span>${{ total.toLocaleString('es-CO') }}</span></div>
        </div>

        <div class="mt-4">
          <label class="label">Método de pago</label>
          <select v-model="paymentMethod" class="input">
            <option value="CASH">Efectivo (en barra)</option>
            <option value="TRANSFER">Transferencia Bancolombia</option>
            <option value="CARD">Tarjeta débito/crédito</option>
            <option value="MEMBERSHIP">Saldo membresía prepagada</option>
          </select>
        </div>
        <textarea v-model="notes" rows="2" placeholder="Notas para la barra (opcional)" class="input mt-3 resize-none" />

        <button class="btn-success w-full mt-4 !py-3" :disabled="submitting" @click="submit">
          <Loader2 v-if="submitting" class="w-4 h-4 animate-spin" />
          Confirmar pedido (retiro en barra)
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Trash2, Plus, Minus, Package, Loader2 } from 'lucide-vue-next'
import { useRefreshmentsStore } from '@/stores/refreshments'
import { useAuthStore } from '@/stores/auth'
import EmptyState from '@/components/EmptyState.vue'
import { showToast } from '@/utils/toast'

const rf = useRefreshmentsStore()
const auth = useAuthStore()
const router = useRouter()

const paymentMethod = ref('CASH')
const notes = ref('')
const submitting = ref(false)

const discountPercent = computed(() => Number(auth.tierInfo?.discount_percent || 0))
const discountAmount = computed(() => Math.round(rf.cartSubtotal * discountPercent.value / 100))
const total = computed(() => rf.cartSubtotal - discountAmount.value)

async function submit() {
  submitting.value = true
  try {
    const order = await rf.createOrder({ payment_method: paymentMethod.value, notes: notes.value })
    showToast('Pedido #' + (order.id || '') + ' creado! Paga y retira en barra.', 'success', '¡Gracias por tu compra!')
    router.replace({ name: 'client-orders' })
  } catch (e) {
    showToast(e || 'No se pudo procesar tu pedido.', 'error')
  } finally {
    submitting.value = false
  }
}
</script>
