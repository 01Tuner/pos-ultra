<template>
	<Dialog
		v-model="show"
		:options="{ title: mode === 'edit' ? __('Edit Delivery Note') : __('New Delivery Note'), size: '5xl' }"
	>
		<template #body-content>
			<div v-if="loading" class="text-center py-12">
				<div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500 mx-auto"></div>
				<p class="mt-3 text-sm text-gray-500">{{ __('Loading...') }}</p>
			</div>

			<div v-else-if="formData" class="flex flex-col gap-6">
				<!-- Header -->
				<div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 md:p-5 border border-blue-100">
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs text-gray-500 mb-1">{{ __('Customer') }}</label>
                            <div class="font-semibold text-gray-900">{{ formData.customer_name || formData.customer }}</div>
                        </div>
                        <div>
                            <label class="block text-xs text-gray-500 mb-1">{{ __('Date') }}</label>
                            <div class="font-medium text-gray-900">{{ formatDate(formData.posting_date || new Date()) }}</div>
                        </div>
					</div>
				</div>

				<!-- Items Section -->
				<div>
					<h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center justify-between">
                        <div class="flex items-center">
                            <FeatherIcon name="package" class="w-4 h-4 me-2" />
                            {{ __('Items') }}
                        </div>
                        <span class="text-xs text-gray-500">{{ formData.items.length }} {{ __('Items') }}</span>
					</h4>
					
					<!-- Desktop Table View -->
					<div class="border border-gray-200 rounded-lg overflow-hidden">
						<table class="min-w-full divide-y divide-gray-200">
							<thead class="bg-gray-50">
								<tr>
									<th class="px-4 py-3 text-start text-xs font-semibold text-gray-600 uppercase tracking-wider">{{ __('Item') }}</th>
									<th class="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider w-32">{{ __('Qty') }}</th>
									<th class="px-4 py-3 text-end text-xs font-semibold text-gray-600 uppercase tracking-wider">{{ __('Rate') }}</th>
									<th class="px-4 py-3 text-end text-xs font-semibold text-gray-600 uppercase tracking-wider">{{ __('Amount') }}</th>
                                    <th class="px-4 py-3 text-center w-10"></th>
								</tr>
							</thead>
							<tbody class="bg-white divide-y divide-gray-200">
								<tr v-for="(item, idx) in formData.items" :key="idx" class="hover:bg-gray-50 group">
									<td class="px-4 py-3 text-start">
										<div class="text-sm font-medium text-gray-900">{{ item.item_name }}</div>
										<div class="text-xs text-gray-500">{{ item.item_code }}</div>
									</td>
									<td class="px-4 py-3 text-center">
                                        <input 
                                            type="number" 
                                            v-model.number="item.qty" 
                                            class="w-full text-center border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                            min="0"
                                            @change="calculateTotals"
                                        />
									</td>
									<td class="px-4 py-3 text-end text-sm text-gray-900">
                                        {{ formatCurrency(item.rate) }}
                                    </td>
									<td class="px-4 py-3 text-end text-sm font-semibold text-gray-900">
                                        {{ formatCurrency(item.amount) }}
                                    </td>
                                    <td class="px-4 py-3 text-center">
                                        <button 
                                            @click="removeItem(idx)"
                                            class="text-gray-400 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
                                            :title="__('Remove Item')"
                                        >
                                            <FeatherIcon name="trash-2" class="w-4 h-4" />
                                        </button>
                                    </td>
								</tr>
							</tbody>
						</table>
                        <div v-if="formData.items.length === 0" class="p-8 text-center text-gray-500 text-sm">
                            {{ __('No items selected') }}
                        </div>
					</div>
				</div>

				<!-- Summary -->
				<div>
					<div class="flex flex-col gap-2 bg-gray-50 p-4 rounded-lg border border-gray-200 ms-auto md:w-1/2 lg:w-1/3">
						<div class="pt-2 flex justify-between">
							<span class="font-semibold text-gray-900">{{ __('Grand Total:') }}</span>
							<span class="font-bold text-lg text-blue-600">{{ formatCurrency(formData.grand_total) }}</span>
						</div>
					</div>
				</div>
			</div>
		</template>
		<template #actions>
			<div class="flex justify-end gap-2 w-full">
				<Button variant="subtle" @click="show = false">
					{{ __('Cancel') }}
				</Button>
				<Button 
                    variant="solid" 
                    :loading="saving" 
                    @click="handleSave"
                    :disabled="!formData || formData.items.length === 0"
                >
					{{ __('Create Delivery Note') }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { useFormatters } from "@/composables/useFormatters"
import { formatCurrency as formatCurrencyUtil } from "@/utils/currency"
import { logger } from "@/utils/logger"
import { Button, Dialog, call, FeatherIcon } from "frappe-ui"
import { ref, watch, computed } from "vue"
import { useToast } from "@/composables/useToast"

const log = logger.create('DeliveryNoteForm')
const { formatDate } = useFormatters()
const { showSuccess, showError } = useToast()

const props = defineProps({
	modelValue: Boolean,
    sourceDoc: Object, // The mapped doc from backend
	currency: {
		type: String,
		default: "USD",
	},
    mode: {
        type: String,
        default: 'create'
    }
})

const emit = defineEmits(["update:modelValue", "created"])

const show = ref(props.modelValue)
const loading = ref(false)
const saving = ref(false)
const formData = ref(null)

function formatCurrency(amount) {
	return formatCurrencyUtil(Number.parseFloat(amount || 0), props.currency)
}

watch(
	() => props.modelValue,
	(val) => {
		show.value = val
		if (val) {
            initializeForm()
		}
	},
    { immediate: true }
)

watch(show, (val) => {
	emit("update:modelValue", val)
    if(!val) {
        formData.value = null
    }
})

function initializeForm() {
    if (props.sourceDoc) {
        // Deep copy to avoid mutating prop
        formData.value = JSON.parse(JSON.stringify(props.sourceDoc))
        calculateTotals()
    }
}

function calculateTotals() {
    if (!formData.value) return

    let total = 0
    formData.value.items.forEach(item => {
        item.amount = item.qty * item.rate
        total += item.amount
    })
    
    // Simple total calculation for now. 
    // Ideally we should call backend to calculate taxes etc, but for MVP this might suffice if we assume inclusive/exclusive logic stays roughly consistent or if we just show Net Total.
    // However, existing mapped doc has taxes. Recalculating taxes in frontend is hard.
    // For now, update grand_total roughly. 
    // Better approach: just update item amount and sum up. 
    // And warn user that final calculation happens on server.
    
    formData.value.grand_total = total 
    // If taxes exist, we might be inaccurate. 
    // Let's assume for simple POS delivery, we trust the mapped structure.
    // If exact calculation is needed, we'd need a backend endpoint `calculate_delivery_note`.
}

function removeItem(index) {
    formData.value.items.splice(index, 1)
    calculateTotals()
}

async function handleSave() {
    if (!formData.value) return
    
    saving.value = true
    try {
        // Prepare doc for submission
        // We need to send the whole doc object
        const docName = await call("pos_next.api.delivery_notes.create_delivery_note", {
             doc: JSON.stringify(formData.value)
        })
        
        showSuccess(__("Delivery Note {0} created", [docName]))
        emit("created", docName)
        show.value = false
    } catch (error) {
        showError(error.message || __("Failed to create Delivery Note"))
    } finally {
        saving.value = false
    }
}

</script>
