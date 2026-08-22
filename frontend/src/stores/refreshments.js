import { defineStore } from 'pinia'
import api, { extractError } from '@/api/client'
import { computed, ref } from 'vue'

export const useRefreshmentsStore = defineStore('refreshments', () => {
  const catalog = ref([])
  const cart = ref(loadCart())
  const orders = ref([])
  const loading = ref(false)
  const error = ref('')

  function loadCart() {
    try {
      const raw = localStorage.getItem('fh_cart')
      return raw ? JSON.parse(raw) : []
    } catch (_) { return [] }
  }
  function persistCart() {
    localStorage.setItem('fh_cart', JSON.stringify(cart.value))
  }

  const cartItemsCount = computed(() =>
    cart.value.reduce((a, it) => a + it.quantity, 0)
  )
  const cartSubtotal = computed(() =>
    cart.value.reduce((a, it) => a + (it.price * it.quantity), 0)
  )
  const cartCount = cartItemsCount

  async function listCatalog() {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.get('/refreshments/products/available-catalog/')
      catalog.value = resp.data?.results || resp.data || []
      return catalog.value
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  function findInCart(productId) {
    return cart.value.find((it) => it.product_id === productId)
  }

  function addToCart(product, quantity = 1) {
    const existing = findInCart(product.id)
    if (existing) {
      existing.quantity = Math.min(existing.quantity + quantity, product.stock || 999)
    } else {
      cart.value.push({
        product_id: product.id,
        name: product.name,
        sku: product.sku,
        image: product.image,
        price: Number(product.price),
        quantity,
        stock: product.stock,
      })
    }
    persistCart()
  }

  function updateQuantity(productId, quantity) {
    if (quantity <= 0) {
      removeFromCart(productId)
      return
    }
    const it = findInCart(productId)
    if (it) {
      it.quantity = Math.min(quantity, it.stock || 999)
      persistCart()
    }
  }

  function removeFromCart(productId) {
    cart.value = cart.value.filter((it) => it.product_id !== productId)
    persistCart()
  }

  function clearCart() {
    cart.value = []
    persistCart()
  }

  async function createOrder(payload) {
    loading.value = true
    error.value = ''
    try {
      const body = {
        items: cart.value.map((it) => ({
          product_id: it.product_id,
          quantity: it.quantity,
        })),
        ...payload,
      }
      const resp = await api.post('/refreshments/orders/', body)
      clearCart()
      return resp.data
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function listMyOrders() {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.get('/refreshments/orders/')
      orders.value = resp.data?.results || resp.data || []
      return orders.value
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  return {
    catalog, cart, orders, loading, error,
    cartCount, cartItemsCount, cartSubtotal,
    listCatalog, addToCart, updateQuantity, removeFromCart,
    clearCart, createOrder, listMyOrders, findInCart,
  }
})
