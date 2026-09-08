<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.budgetTitle') }}</h3>
        </div>
        <div class="budget-control">
          <label class="budget-label" for="budget-slider">{{ t('restocking.budgetLabel') }}</label>
          <div class="budget-amount">{{ formatCurrency(budget) }}</div>
          <input
            id="budget-slider"
            v-model.number="budget"
            class="budget-slider"
            type="range"
            min="0"
            :max="maxBudget"
            :step="sliderStep"
          />
          <div class="budget-scale">
            <span>{{ formatCurrency(0) }}</span>
            <span>{{ t('restocking.coversAll', { amount: formatCurrency(maxBudget) }) }}</span>
          </div>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.stats.budget') }}</div>
          <div class="stat-value">{{ formatCurrency(budget) }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t('restocking.stats.allocated') }}</div>
          <div class="stat-value">{{ formatCurrency(allocation.totalCost) }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('restocking.stats.remaining') }}</div>
          <div class="stat-value">{{ formatCurrency(allocation.budgetRemaining) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.stats.items') }}</div>
          <div class="stat-value">{{ allocation.itemsRecommended }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            {{ t('restocking.recommendations') }} ({{ allocation.itemsRecommended }})
          </h3>
          <button
            class="place-order-btn"
            :disabled="!canSubmit"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.placing') : t('restocking.placeOrder') }}
          </button>
        </div>

        <div v-if="submitError" class="error">{{ submitError }}</div>
        <div v-if="lastOrder" class="submit-success">
          {{ t('restocking.orderPlaced', { orderNumber: lastOrder.order_number }) }}
        </div>

        <div v-if="allocation.itemsRecommended === 0" class="empty-state">
          {{ t('restocking.noRecommendations') }}
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.shortfall') }}</th>
                <th>{{ t('restocking.table.quantity') }}</th>
                <th>{{ t('restocking.table.unitCost') }}</th>
                <th>{{ t('restocking.table.lineTotal') }}</th>
                <th>{{ t('restocking.table.leadTime') }}</th>
                <th>{{ t('restocking.table.funding') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in allocation.recommendations" :key="item.item_sku">
                <td><strong>{{ item.item_sku }}</strong></td>
                <td>{{ translateProductName(item.item_name) }}</td>
                <td>{{ item.shortfall }}</td>
                <td><strong>{{ item.recommended_quantity }}</strong></td>
                <td>{{ formatUnitCost(item.unit_cost) }}</td>
                <td><strong>{{ formatCurrency(item.line_total) }}</strong></td>
                <td>{{ t('restocking.days', { count: item.lead_time_days }) }}</td>
                <td>
                  <span :class="['badge', item.fully_funded ? 'success' : 'warning']">
                    {{ item.fully_funded ? t('restocking.full') : t('restocking.partial') }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { buildRecommendations } from '../utils/restocking'
import { formatCurrency as formatCurrencyUtil, formatCurrencyWithDecimals } from '../utils/currency'

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency, translateProductName } = useI18n()

    const loading = ref(true)
    const error = ref(null)
    const submitting = ref(false)
    const submitError = ref(null)
    const lastOrder = ref(null)
    const candidates = ref([])
    const maxBudget = ref(0)
    const budget = ref(0)

    // A hundred steps across the full range, rounded to whole currency units so
    // the readout never shows fractional cents while dragging.
    const sliderStep = computed(() => Math.max(1, Math.round(maxBudget.value / 100)))

    // Re-allocated locally on every drag; the server recomputes the same
    // allocation on submit, so this is a preview rather than the source of truth.
    const allocation = computed(() => buildRecommendations(candidates.value, budget.value))

    const canSubmit = computed(
      () => !submitting.value && allocation.value.itemsRecommended > 0
    )

    const formatCurrency = (value) => formatCurrencyUtil(value, currentCurrency.value)
    // Unit costs need the cents that formatCurrency drops, or $18.99 reads $19.
    const formatUnitCost = (value) => formatCurrencyWithDecimals(value, currentCurrency.value, 2)

    const loadCandidates = async () => {
      try {
        loading.value = true
        // A budget large enough to fund every shortfall returns the complete
        // candidate set, which is the only response carrying lead_time_days.
        const data = await api.getRestockingRecommendations(Number.MAX_SAFE_INTEGER)
        candidates.value = data.recommendations
        maxBudget.value = Math.ceil(data.cost_to_cover_all)
        budget.value = Math.round(maxBudget.value / 2)
        error.value = null
      } catch (err) {
        error.value = 'Failed to load restocking recommendations: ' + err.message
      } finally {
        loading.value = false
      }
    }

    const placeOrder = async () => {
      if (!canSubmit.value) return
      try {
        submitting.value = true
        submitError.value = null
        lastOrder.value = await api.submitRestockOrder(
          allocation.value.recommendations.map(item => ({
            item_sku: item.item_sku,
            item_name: item.item_name,
            quantity: item.recommended_quantity,
            unit_cost: item.unit_cost
          }))
        )
      } catch (err) {
        submitError.value = 'Failed to place order: ' + err.message
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadCandidates)

    return {
      t,
      translateProductName,
      loading,
      error,
      submitting,
      submitError,
      lastOrder,
      budget,
      maxBudget,
      sliderStep,
      allocation,
      canSubmit,
      formatCurrency,
      formatUnitCost,
      placeOrder
    }
  }
}
</script>

<style scoped>
.budget-control {
  padding: 0.5rem 0 0.25rem;
}

.budget-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 0.375rem;
}

.budget-amount {
  font-size: 2.25rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.75rem;
}

.budget-slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #e2e8f0;
  outline: none;
  appearance: none;
  -webkit-appearance: none;
  cursor: pointer;
}

.budget-slider::-webkit-slider-thumb {
  appearance: none;
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.25);
  cursor: pointer;
}

.budget-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.25);
  cursor: pointer;
}

.budget-slider:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.budget-scale {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #64748b;
}

.place-order-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.813rem;
  font-weight: 600;
  color: white;
  background: #3b82f6;
  cursor: pointer;
  transition: all 0.2s;
}

.place-order-btn:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.place-order-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.submit-success {
  background: #d1fae5;
  color: #065f46;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: #64748b;
  font-size: 0.938rem;
}
</style>
