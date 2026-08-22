import { defineStore } from 'pinia'
import api, { extractError } from '@/api/client'
import { ref } from 'vue'

export const useRewardsStore = defineStore('rewards', () => {
  const catalog = ref([])
  const tiers = ref([])
  const rules = ref([])
  const transactions = ref([])
  const loading = ref(false)
  const error = ref('')

  async function listCatalog() {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.get('/rewards/catalog/')
      catalog.value = resp.data?.results || resp.data || []
      return catalog.value
    } catch (e) {
      error.value = extractError(e)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function listTiers() {
    try {
      const resp = await api.get('/rewards/tiers/')
      tiers.value = resp.data?.results || resp.data || []
      return tiers.value
    } catch (_) { return tiers.value }
  }

  async function listMyTransactions() {
    try {
      const resp = await api.get('/rewards/transactions/my/')
      transactions.value = resp.data?.results || resp.data || []
      return transactions.value
    } catch (_) { return transactions.value }
  }

  async function redeem(itemId) {
    loading.value = true
    error.value = ''
    try {
      const resp = await api.post(`/rewards/catalog/${itemId}/redeem/`)
      return resp.data
    } catch (e) {
      error.value = extractError(e, 'No se pudo canjear el premio.')
      throw error.value
    } finally {
      loading.value = false
    }
  }

  return {
    catalog, tiers, rules, transactions, loading, error,
    listCatalog, listTiers, listMyTransactions, redeem,
  }
})
