<template>
	<div>
	<Dialog
		v-model="show"
		:options="{ title: __('Sales Order Details'), size: '5xl' }"
	>
		<template #body-content>
			<div v-if="loading" class="text-center py-12">
				<div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500 mx-auto"></div>
				<p class="mt-3 text-sm text-gray-500">{{ __('Loading details...') }}</p>
			</div>

			<div v-else-if="orderData" class="flex flex-col gap-6">
				<!-- Header -->
				<div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 md:p-5 border border-blue-100">
					<div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
						<div class="flex-1">
							<div class="flex items-center gap-3 mb-2 flex-wrap">
								<h3 class="text-lg md:text-xl font-bold text-gray-900">{{ orderData.name }}</h3>
								<span
									:class="[
										'px-3 py-1 text-xs font-semibold rounded-full',
										getStatusColor(orderData.status)
									]"
								>
									{{ __(orderData.status) }}
								</span>
							</div>
							<div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
								<div class="text-start">
									<span class="text-gray-600">{{ __('Customer:') }}</span>
									<span class="ms-2 font-semibold text-gray-900">{{ orderData.customer_name || orderData.customer }}</span>
								</div>
								<div class="text-start">
									<span class="text-gray-600">{{ __('Date:') }}</span>
									<span class="ms-2 font-medium text-gray-900">{{ formatDate(orderData.transaction_date) }}</span>
								</div>
								<div v-if="orderData.delivery_date" class="text-start">
									<span class="text-gray-600">{{ __('Delivery Date:') }}</span>
									<span class="ms-2 font-medium text-gray-900">{{ formatDate(orderData.delivery_date) }}</span>
								</div>
							</div>
						</div>
						<div class="flex flex-col sm:items-end gap-3">
                            <!-- Action Buttons -->
                            <div class="flex gap-2">
                                <Dropdown
                                    v-if="orderData && orderData.status !== 'Completed' && orderData.status !== 'Cancelled'"
                                    :options="[
                                        ...(orderData.per_billed < 100 ? [{
                                            label: __('Invoice'),
                                            icon: 'file-text',
                                            onClick: handleCreateInvoice
                                        }] : []),
                                        ...(allowDeliveryNote && orderData.per_delivered < 100 ? [{
                                            label: __('Delivery Note'),
                                            icon: 'truck',
                                            onClick: handleCreateDeliveryNote
                                        }] : [])
                                    ].filter(Boolean)"
                                >
                                    <template #default="{ open }">
                                        <Button
                                            variant="subtle"
                                            theme="gray"
                                            size="sm"
                                            class="shadow-sm border border-gray-200"
                                        >
                                            <template #prefix>
                                                <FeatherIcon name="plus" class="w-4 h-4" />
                                            </template>
                                            {{ __('Create') }}
                                            <template #suffix>
                                                <FeatherIcon name="chevron-down" class="w-4 h-4 ml-1 transition-transform" :class="{ 'rotate-180': open }" />
                                            </template>
                                        </Button>
                                    </template>
                                </Dropdown>
                                <!-- Amend Button -->
                                <Button
                                    v-if="canAmend(orderData)"
                                    size="sm"
                                    theme="orange"
                                    variant="subtle"
                                    class="shadow-sm border border-orange-200"
                                    @click="handleAmend"
                                >
                                    <template #prefix>
                                        <FeatherIcon name="edit-2" class="w-4 h-4" />
                                    </template>
                                    {{ __('Amend') }}
                                </Button>
                                <Button
                                    v-if="orderData && canCancel(orderData)"
                                    size="sm"
                                    theme="red"
                                    variant="subtle"
                                    :loading="cancelling"
                                    class="shadow-sm border border-red-200"
                                    @click="handleCancel"
                                >
                                    {{ __('Cancel') }}
                                </Button>
                                <Button
                                    size="sm"
                                    variant="subtle"
                                    @click="handlePrint"
                                >
                                    <template #prefix>
                                        <FeatherIcon name="printer" class="w-4 h-4" />
                                    </template>
                                    {{ __('Print') }}
                                </Button>
                            </div>
							<div class="text-start sm:text-end">
								<div class="text-xs text-gray-500 mb-1">{{ __('Grand Total') }}</div>
								<div class="text-xl md:text-2xl font-bold text-blue-600">
									{{ formatCurrency(orderData.grand_total) }}
								</div>
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
							v-for="(item, idx) in orderData.items"
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
								<tr v-for="(item, idx) in orderData.items" :key="idx" class="hover:bg-gray-50">
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

                <!-- Related Documents -->
                 <div v-if="(orderData.related_invoices && orderData.related_invoices.length) || (orderData.related_delivery_notes && orderData.related_delivery_notes.length)" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Related Invoices -->
                    <div v-if="orderData.related_invoices && orderData.related_invoices.length">
                        <h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                            <FeatherIcon name="file-text" class="w-4 h-4 me-2" />
                            {{ __('Related Invoices') }}
                        </h4>
                        <div class="flex flex-col gap-2">
                            <div
                                v-for="invoice in orderData.related_invoices"
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

                    <!-- Related Delivery Notes -->
                    <div v-if="orderData.related_delivery_notes && orderData.related_delivery_notes.length">
                        <h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                            <FeatherIcon name="truck" class="w-4 h-4 me-2" />
                            {{ __('Related Delivery Notes') }}
                        </h4>
                        <div class="flex flex-col gap-2">
                            <div
                                v-for="dn in orderData.related_delivery_notes"
                                :key="dn"
                                class="flex justify-between items-center p-3 bg-white border border-gray-200 rounded-lg shadow-sm"
                            >
                                <span class="text-sm font-medium text-gray-900">{{ dn }}</span>
                                <Button
                                    size="sm"
                                    variant="subtle"
                                    @click="openDocument('Delivery Note', dn)"
                                >
                                    {{ __('View') }}
                                </Button>
                            </div>
                        </div>
                    </div>
                 </div>

				<!-- Summary -->
				<div>
					<h4 class="text-sm font-semibold text-gray-700 mb-3 text-start">{{ __('Summary') }}</h4>
					<div class="flex flex-col gap-2 bg-gray-50 p-4 rounded-lg border border-gray-200">
						<div class="flex justify-between text-sm">
							<span class="text-gray-600">{{ __('Net Total:') }}</span>
							<span class="font-medium text-gray-900">{{ formatCurrency(orderData.net_total || orderData.total) }}</span>
						</div>
						<div v-if="orderData.total_taxes_and_charges" class="flex justify-between text-sm">
							<span class="text-gray-600">{{ __('Taxes:') }}</span>
							<span class="font-medium text-gray-900">{{ formatCurrency(orderData.total_taxes_and_charges) }}</span>
						</div>
						<div class="pt-2 border-t border-gray-300 flex justify-between">
							<span class="font-semibold text-gray-900">{{ __('Grand Total:') }}</span>
							<span class="font-bold text-lg text-blue-600">{{ formatCurrency(orderData.grand_total) }}</span>
						</div>
						<div v-if="orderData.advance_paid" class="flex justify-between text-sm">
							<span class="text-gray-600">{{ __('Advance Paid:') }}</span>
							<span class="font-semibold text-green-600">{{ formatCurrency(orderData.advance_paid) }}</span>
						</div>
					</div>
				</div>
			</div>

			<div v-else class="text-center py-12">
				<p class="mt-2 text-sm text-gray-500">{{ __('Failed to load details') }}</p>
			</div>
		</template>
		<template #actions>
			<div class="flex justify-end items-center w-full">
				<Button variant="subtle" @click="show = false">
					{{ __('Close') }}
				</Button>
			</div>
		</template>
	</Dialog>


	</div>
</template>

<script setup>
import { useFormatters } from "@/composables/useFormatters"
import { formatCurrency as formatCurrencyUtil } from "@/utils/currency"
import { logger } from "@/utils/logger"
import { Button, Dialog, call, FeatherIcon, Dropdown } from "frappe-ui"
import { ref, watch, computed } from "vue"
import { useToast } from "@/composables/useToast"

import { usePOSCartStore } from "@/stores/posCart"
import { usePOSSettingsStore } from "@/stores/posSettings"

const cartStore = usePOSCartStore()
const settingsStore = usePOSSettingsStore()
const allowDeliveryNote = computed(() => settingsStore.enableDeliveryNote)

const log = logger.create('SalesOrderDetailDialog')
const { formatDate, formatTime } = useFormatters()
const { showSuccess, showError } = useToast()

const props = defineProps({
	modelValue: Boolean,
	orderName: String,
	posProfile: String,
	currency: {
		type: String,
		default: "USD",
	},
})

function formatCurrency(amount) {
	return formatCurrencyUtil(Number.parseFloat(amount || 0), props.currency)
}

const emit = defineEmits(["update:modelValue", "print-order", "order-cancelled", "invoice-created", "open-invoice", "open-delivery-note", "delivery-note-prepared", "amend-order"])

const show = ref(props.modelValue)
const loading = ref(false)
const orderData = ref(null)
const cancelling = ref(false)





watch(
	() => props.modelValue,
	(val) => {
		show.value = val
		if (val && props.orderName) {
			loadOrderDetails()
		}
	},
)

watch(show, async (val) => {
	emit("update:modelValue", val)
	if (!val) {
		orderData.value = null
	}
})

async function loadOrderDetails() {
	if (!props.orderName) return

	loading.value = true
	try {
		const result = await call("pos_next.api.sales_orders.get_sales_order", {
			name: props.orderName,
		})
		orderData.value = result
	} catch (error) {
		log.error("Error loading details:", error)
		orderData.value = null
	} finally {
		loading.value = false
	}
}

function handlePrint() {
	if (!orderData.value) return
	emit("print-order", orderData.value)
}

function getStatusColor(status) {
	switch (status) {
		case "Draft": return "bg-gray-100 text-gray-800"
		case "To Deliver and Bill": return "bg-orange-100 text-orange-800"
		case "To Bill": return "bg-red-100 text-red-800"
		case "To Deliver": return "bg-yellow-100 text-yellow-800"
		case "Completed": return "bg-green-100 text-green-800"
		case "Cancelled": return "bg-red-100 text-red-800"
		default: return "bg-blue-100 text-blue-800"
	}
}

function canCancel(order) {
    return order.status !== 'Cancelled' && order.status !== 'Completed'
}

/**
 * Amend is allowed ONLY for Cancelled Sales Orders.
 * Creates a new SO with amended_from pointing to the cancelled one.
 */
function canAmend(order) {
    if (!order) return false
    return order.status === 'Cancelled'
}

function handleAmend() {
    if (!orderData.value) return
    emit('amend-order', orderData.value)
    show.value = false
}

async function handleCancel() {
    if (!orderData.value) return
    if (!confirm(__("Are you sure you want to cancel Sales Order {0}?", [orderData.value.name]))) {
        return
    }

    cancelling.value = true
    try {
        await call("pos_next.api.sales_orders.cancel_sales_order", {
            name: orderData.value.name
        })
        showSuccess(__("Sales Order cancelled successfully"))
        emit("order-cancelled")
        show.value = false
    } catch (error) {
         showError(error.message || __("Failed to cancel sales order"))
    } finally {
        cancelling.value = false
    }
}
async function handleCreateInvoice() {
    if (!orderData.value) return
    try {
        const mappedDoc = await call("pos_next.api.sales_orders.make_invoice_from_sales_order", {
            source_name: orderData.value.name
        })
        
        // Clear existing cart
        cartStore.clearCart()

        // Set target doctype to Invoice
        cartStore.setTargetDoctype('Sales Invoice')

        // Respect update_stock flag from backend (backend sets 0 when items are already delivered)
        if (mappedDoc.update_stock !== undefined) {
            cartStore.setUpdateStockOverride(mappedDoc.update_stock)
        }

        // Set customer
        if (mappedDoc.customer) {
            cartStore.setCustomer({
                name: mappedDoc.customer,
                customer_name: mappedDoc.customer_name || mappedDoc.customer
            })
        }

        // Add items to cart
        if (mappedDoc.items && mappedDoc.items.length) {
            mappedDoc.items.forEach(item => {
                cartStore.addItem({
                    item_code: item.item_code,
                    item_name: item.item_name,
                    description: item.description,
                    uom: item.uom,
                    rate: item.rate,
                    price_list_rate: item.price_list_rate || item.rate,
                    is_stock_item: item.is_stock_item,
                    stock_uom: item.stock_uom,
                    conversion_factor: item.conversion_factor,
                    item_group: item.item_group,
                    discount_percentage: item.discount_percentage,
                    discount_amount: item.discount_amount,
                    // Reference fields
                    sales_order: item.sales_order || item.against_sales_order,
                    against_sales_order: item.against_sales_order || item.sales_order,
                    so_detail: item.so_detail,
                    against_sales_invoice: item.against_sales_invoice,
                    si_detail: item.si_detail,
                    delivery_note: item.delivery_note,
                    dn_detail: item.dn_detail,
                }, item.qty || item.quantity || 1)
            })
        }

        // Set target doctype to Invoice AFTER adding items so it's not overridden by addItem
        cartStore.setTargetDoctype('Sales Invoice')

        showSuccess(__("Invoice created from Sales Order"))
        emit("invoice-created")
        show.value = false

    } catch (error) {
        showError(error.message || __("Failed to prepare invoice"))
    }
}

async function handleCreateDeliveryNote() {
    if (!orderData.value) return
    try {
        const mappedDoc = await call("pos_next.api.sales_orders.make_delivery_note_from_sales_order", {
            source_name: orderData.value.name
        })
        
        // Clear existing cart
        cartStore.clearCart()

        // Set customer
        if (mappedDoc.customer) {
            cartStore.setCustomer({
                name: mappedDoc.customer,
                customer_name: mappedDoc.customer_name || mappedDoc.customer
            })
        }

        // Add items to cart
        if (mappedDoc.items && mappedDoc.items.length) {
            mappedDoc.items.forEach(item => {
                cartStore.addItem({
                    item_code: item.item_code,
                    item_name: item.item_name,
                    description: item.description,
                    uom: item.uom,
                    rate: item.rate,
                    price_list_rate: item.price_list_rate || item.rate,
                    is_stock_item: item.is_stock_item,
                    stock_uom: item.stock_uom,
                    conversion_factor: item.conversion_factor,
                    item_group: item.item_group,
                    discount_percentage: item.discount_percentage,
                    discount_amount: item.discount_amount,
                    // Reference fields
                    sales_order: item.sales_order,
                    against_sales_order: item.against_sales_order,
                    so_detail: item.so_detail,
                    against_sales_invoice: item.against_sales_invoice,
                    si_detail: item.si_detail,
                    delivery_note: item.delivery_note,
                    dn_detail: item.dn_detail,
                }, item.qty || item.quantity || 1)
            })
        }

        // Set target doctype to Delivery Note AFTER adding items so it's not overridden by addItem
        cartStore.setTargetDoctype('Delivery Note')

        showSuccess(__("Delivery Note prepared in Cart"))
        emit("delivery-note-prepared")
        show.value = false
    } catch (error) {
        console.error(error)
        showError(error.message || __("Failed to prepare delivery note"))
    }
}



function openDocument(doctype, name) {
    if (doctype === 'Sales Invoice') {
        emit('open-invoice', name)
    } else if (doctype === 'Delivery Note') {
        emit('open-delivery-note', name)
    } else {
        const slug = doctype.toLowerCase().trim().replace(/\s+/g, '-')
        const url = `/app/${slug}/${name}`
        window.open(url, '_blank')
    }
}
</script>
