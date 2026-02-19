<template>
	<Dialog
		v-model="show"
		:options="{ title: __('Delivery Note Details'), size: '5xl' }"
	>
		<template #body-content>
			<div v-if="loading" class="text-center py-12">
				<div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500 mx-auto"></div>
				<p class="mt-3 text-sm text-gray-500">{{ __('Loading details...') }}</p>
			</div>

			<div v-else-if="dnData" class="flex flex-col gap-6">
				<!-- Header -->
				<div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 md:p-5 border border-blue-100">
					<div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
						<div class="flex-1">
							<div class="flex items-center gap-3 mb-2 flex-wrap">
								<h3 class="text-lg md:text-xl font-bold text-gray-900">{{ dnData.name }}</h3>
								<span
									:class="[
										'px-3 py-1 text-xs font-semibold rounded-full',
										getStatusColor(dnData.status)
									]"
								>
									{{ __(dnData.status) }}
								</span>
							</div>
							<div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
								<div class="text-start">
									<span class="text-gray-600">{{ __('Customer:') }}</span>
									<span class="ms-2 font-semibold text-gray-900">{{ dnData.customer_name || dnData.customer }}</span>
								</div>
								<div class="text-start">
									<span class="text-gray-600">{{ __('Date:') }}</span>
									<span class="ms-2 font-medium text-gray-900">{{ formatDate(dnData.transaction_date) }}</span>
								</div>
							</div>
						</div>
						<div class="text-start sm:text-end">
							<div class="text-xs text-gray-500 mb-1">{{ __('Grand Total') }}</div>
							<div class="text-xl md:text-2xl font-bold text-blue-600">
								{{ formatCurrency(dnData.grand_total) }}
							</div>
						</div>
					</div>
				</div>

				<!-- Items Section -->
				<div>
					<h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
						<svg class="w-4 h-4 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
						</svg>
						{{ __('Items') }}
					</h4>
					<!-- Mobile Cards View -->
					<div class="md:hidden flex flex-col gap-3">
						<div
							v-for="(item, idx) in dnData.items"
							:key="idx"
							class="bg-white border border-gray-200 rounded-lg p-3"
						>
							<div class="flex items-center justify-between gap-3 mb-2">
								<div class="flex-1 min-w-0 text-center">
									<div class="text-sm font-semibold text-gray-900">{{ item.item_name }}</div>
									<div class="text-xs text-gray-500">{{ item.item_code }}</div>
								</div>
							</div>
							<div class="grid grid-cols-3 gap-2 text-center border-t border-gray-100 pt-2">
								<div>
									<div class="text-xs text-gray-500">{{ __('Qty') }}</div>
									<div class="text-sm font-medium text-gray-900">{{ item.qty }}</div>
								</div>
								<div>
									<div class="text-xs text-gray-500">{{ __('Rate') }}</div>
									<div class="text-sm font-medium text-gray-900">{{ formatCurrency(item.rate) }}</div>
								</div>
								<div>
									<div class="text-xs text-gray-500">{{ __('Amount') }}</div>
									<div class="text-sm font-semibold text-gray-900">{{ formatCurrency(item.amount) }}</div>
								</div>
							</div>
						</div>
					</div>
					<!-- Desktop Table View -->
					<div class="hidden md:block border border-gray-200 rounded-lg overflow-hidden">
						<table class="min-w-full divide-y divide-gray-200">
							<thead class="bg-gray-50">
								<tr>
									<th class="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">{{ __('Item') }}</th>
									<th class="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">{{ __('Qty') }}</th>
									<th class="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">{{ __('Rate') }}</th>
									<th class="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">{{ __('Amount') }}</th>
								</tr>
							</thead>
							<tbody class="bg-white divide-y divide-gray-200">
								<tr v-for="(item, idx) in dnData.items" :key="idx" class="hover:bg-gray-50">
									<td class="px-4 py-3 text-center">
										<div class="text-sm font-medium text-gray-900">{{ item.item_name }}</div>
										<div class="text-xs text-gray-500">{{ item.item_code }}</div>
									</td>
									<td class="px-4 py-3 text-center text-sm text-gray-900">{{ item.qty }}</td>
									<td class="px-4 py-3 text-center text-sm text-gray-900">{{ formatCurrency(item.rate) }}</td>
									<td class="px-4 py-3 text-center text-sm font-semibold text-gray-900">{{ formatCurrency(item.amount) }}</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>

				<!-- Summary -->
				<div>
					<h4 class="text-sm font-semibold text-gray-700 mb-3 text-start">{{ __('Summary') }}</h4>
					<div class="flex flex-col gap-2 bg-gray-50 p-4 rounded-lg border border-gray-200">
						<div class="flex justify-between text-sm">
							<span class="text-gray-600">{{ __('Net Total:') }}</span>
							<span class="font-medium text-gray-900">{{ formatCurrency(dnData.net_total || dnData.total) }}</span>
						</div>
						<div v-if="dnData.total_taxes_and_charges" class="flex justify-between text-sm">
							<span class="text-gray-600">{{ __('Taxes:') }}</span>
							<span class="font-medium text-gray-900">{{ formatCurrency(dnData.total_taxes_and_charges) }}</span>
						</div>
						<div class="pt-2 border-t border-gray-300 flex justify-between">
							<span class="font-semibold text-gray-900">{{ __('Grand Total:') }}</span>
							<span class="font-bold text-lg text-blue-600">{{ formatCurrency(dnData.grand_total) }}</span>
						</div>
					</div>
				</div>

				<!-- Related Documents -->
				 <div v-if="(dnData.related_sales_orders && dnData.related_sales_orders.length) || (dnData.related_invoices && dnData.related_invoices.length)" class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<!-- Related Sales Orders -->
					<div v-if="dnData.related_sales_orders && dnData.related_sales_orders.length">
						<h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
							<svg class="w-4 h-4 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
							</svg>
							{{ __('Related Sales Orders') }}
						</h4>
						<div class="flex flex-col gap-2">
							<div
								v-for="so in dnData.related_sales_orders"
								:key="so"
								class="flex justify-between items-center p-3 bg-white border border-gray-200 rounded-lg shadow-sm"
							>
								<span class="text-sm font-medium text-gray-900">{{ so }}</span>
								<Button
									size="sm"
									variant="subtle"
									@click="openDocument('Sales Order', so)"
								>
									{{ __('View') }}
								</Button>
							</div>
						</div>
					</div>

					<!-- Related Invoices -->
					<div v-if="dnData.related_invoices && dnData.related_invoices.length">
						<h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
							<svg class="w-4 h-4 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
							</svg>
							{{ __('Related Invoices') }}
						</h4>
						<div class="flex flex-col gap-2">
							<div
								v-for="invoice in dnData.related_invoices"
								:key="invoice"
								class="flex justify-between items-center p-3 bg-white border border-gray-200 rounded-lg shadow-sm"
							>
								<span class="text-sm font-medium text-gray-900">{{ invoice }}</span>
								<Button
									size="sm"
									variant="subtle"
									@click="openDocument('Sales Invoice', invoice)"
								>
									{{ __('View') }}
								</Button>
							</div>
						</div>
					</div>
				 </div>
			</div>

			<div v-else class="text-center py-12">
				<p class="mt-2 text-sm text-gray-500">{{ __('Failed to load details') }}</p>
			</div>
		</template>
		<template #actions>
			<div class="flex justify-between items-center w-full">
				<Button variant="subtle" @click="show = false">
					{{ __('Close') }}
				</Button>
				<div class="flex gap-2">
                    <Button
                        v-if="dnData && dnData.status !== 'Completed' && dnData.status !== 'Cancelled' && dnData.docstatus === 1"
                        variant="solid"
                        @click="handleCreateInvoice"
                    >
                        {{ __('Create Invoice') }}
                    </Button>
					<Button @click="handlePrint">
						<template #prefix>
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/>
							</svg>
						</template>
						{{ __('Print') }}
					</Button>
				</div>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { useFormatters } from "@/composables/useFormatters"
import { formatCurrency as formatCurrencyUtil } from "@/utils/currency"
import { logger } from "@/utils/logger"
import { Button, Dialog, call } from "frappe-ui"
import { ref, watch, nextTick } from "vue"
import { useToast } from "@/composables/useToast"

const log = logger.create('DeliveryNoteDetailDialog')
const { formatDate, formatTime } = useFormatters()
const { showSuccess, showError } = useToast()

const props = defineProps({
	modelValue: Boolean,
	dnName: String,
	posProfile: String,
	currency: {
		type: String,
		default: "USD",
	},
})

function formatCurrency(amount) {
	return formatCurrencyUtil(Number.parseFloat(amount || 0), props.currency)
}

const emit = defineEmits(["update:modelValue", "print-dn", "create-invoice"])

const show = ref(props.modelValue)
const loading = ref(false)
const dnData = ref(null)

function openDocument(doctype, name) {
    if (doctype === 'Sales Invoice') {
         const slug = doctype.toLowerCase().trim().replace(/\s+/g, '-')
         const url = `/app/${slug}/${name}`
         window.open(url, '_blank')
    } else {
        const slug = doctype.toLowerCase().trim().replace(/\s+/g, '-')
        const url = `/app/${slug}/${name}`
        window.open(url, '_blank')
    }
}

watch(
	() => props.modelValue,
	(val) => {
		show.value = val
		if (val && props.dnName) {
			loadDNDetails()
		}
	},
)

watch(show, async (val) => {
	emit("update:modelValue", val)
	if (!val) {
		dnData.value = null
	}
})

async function loadDNDetails() {
	if (!props.dnName) return

	loading.value = true
	try {
        // NOTE: We need to implement this backend method
		const result = await call("pos_next.api.delivery_notes.get_delivery_note", {
			name: props.dnName,
		})
		dnData.value = result
	} catch (error) {
		log.error("Error loading details:", error)
		dnData.value = null
	} finally {
		loading.value = false
	}
}

function handlePrint() {
	if (!dnData.value) return
	emit("print-dn", dnData.value)
}

function handleCreateInvoice() {
    if (!dnData.value) return
    emit("create-invoice", dnData.value)
}

function getStatusColor(status) {
	switch (status) {
		case "Draft": return "bg-gray-100 text-gray-800"
		case "To Bill": return "bg-red-100 text-red-800"
		case "Completed": return "bg-green-100 text-green-800"
		case "Cancelled": return "bg-red-100 text-red-800"
        case "Return": return "bg-red-100 text-red-800"
		default: return "bg-blue-100 text-blue-800"
	}
}

</script>
