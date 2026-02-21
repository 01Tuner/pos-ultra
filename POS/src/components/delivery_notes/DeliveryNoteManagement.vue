<template>
	<!-- Full Page Overlay -->
	<Transition name="fade">
		<div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 z-[300]" @click.self="handleClose">
			<!-- Main Container -->
			<div class="fixed inset-0 flex items-center justify-center p-4">
				<div class="w-full h-full max-w-[95vw] max-h-[95vh] bg-white rounded-lg shadow-2xl overflow-hidden flex flex-col">
					<!-- Header -->
					<div class="flex items-center justify-between px-6 py-5 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
						<div class="flex items-center gap-3">
							<div class="p-2 bg-blue-100 rounded-lg">
								<svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
								</svg>
							</div>
							<div>
								<h2 class="text-xl font-bold text-gray-900">{{ __('Delivery Note Management') }}</h2>
								<p class="text-sm text-gray-600 flex items-center mt-0.5">
									{{ __('View and manage delivery notes') }}
								</p>
							</div>
						</div>
						<div class="flex items-center gap-2">
							<Button @click="loadDeliveryNotes" :loading="loading" variant="ghost" size="sm">
								<template #prefix>
									<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
									</svg>
								</template>
								{{ __('Refresh') }}
							</Button>
							<button @click="handleClose" class="p-2 hover:bg-white/50 rounded-lg transition-colors">
								<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
								</svg>
							</button>
						</div>
					</div>

					<!-- Content Body -->
					<div class="flex-1 overflow-y-auto bg-gray-50 p-6">

						<!-- Loading State -->
						<div v-if="loading && deliveryNotes.length === 0" class="flex flex-col items-center justify-center py-16">
							<div class="animate-spin rounded-full h-12 w-12 border-b-3 border-blue-500 mb-4"></div>
							<p class="text-sm font-medium text-gray-600">{{ __('Loading Delivery Notes...') }}</p>
						</div>

						<!-- Empty State (No Data) -->
						<div v-else-if="deliveryNotes.length === 0" class="flex flex-col items-center justify-center py-16 text-center">
							<svg class="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
							</svg>
							<p class="text-gray-600 font-medium">{{ __('No Delivery Notes found') }}</p>
						</div>

						<template v-else>
							<!-- Filters Component -->
							<div class="mb-6">
								<DeliveryNoteFilters
									:unique-customers="uniqueCustomers"
									:unique-products="uniqueProducts"
									:filter-stats="filterStats"
								/>
							</div>

							<!-- Empty State (No Matches) -->
							<div v-if="filteredNotes.length === 0" class="flex flex-col items-center justify-center py-12 text-center">
								<svg class="w-12 h-12 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
								</svg>
								<p class="text-gray-500">{{ __('No delivery notes match your search') }}</p>
								<button @click="useDeliveryNoteFilters(deliveryNotes).store.clearAllFilters()" class="mt-2 text-blue-600 hover:text-blue-700 text-sm font-medium">
									{{ __('Clear filters') }}
								</button>
							</div>

							<!-- Grid -->
							<div v-else class="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
								<div v-for="dn in filteredNotes" :key="dn.name" class="bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-lg transition-all overflow-hidden flex flex-col cursor-default">
									<!-- Card Header -->
									<div class="bg-gradient-to-r from-gray-50 to-blue-50 px-5 py-4 border-b border-gray-200">
										<div class="flex items-start justify-between mb-2">
											<div class="flex-1">
												<h3 class="text-base font-bold text-gray-900">{{ dn.name }}</h3>
												<div class="flex items-center gap-2 mt-1">
													<span :class="['text-xs px-2.5 py-1 rounded-full font-semibold', getStatusColor(dn.status)]">
														{{ __(dn.status) }}
													</span>
												</div>
											</div>
											<div class="text-end ms-3">
												<div class="text-xs text-gray-500 mb-1">{{ __('Total') }}</div>
												<div class="text-lg font-bold text-blue-600">{{ formatCurrency(dn.grand_total, dn.currency) }}</div>
											</div>
										</div>
									</div>

									<!-- Card Body -->
									<div class="px-5 py-4 flex flex-col gap-3 flex-1">
										<!-- Customer Info -->
										<div class="flex items-start">
											<svg class="w-5 h-5 text-gray-400 me-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
											</svg>
											<div class="flex-1">
												<div class="text-xs text-gray-500">{{ __('Customer') }}</div>
												<div class="text-sm font-semibold text-gray-900">{{ dn.customer_name || dn.customer }}</div>
											</div>
										</div>

										<!-- Date & Time -->
										<div class="flex items-start">
											<svg class="w-5 h-5 text-gray-400 me-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
											</svg>
											<div class="flex-1">
												<div class="text-xs text-gray-500">{{ __('Date') }}</div>
												<div class="text-sm font-medium text-gray-900">{{ formatDate(dn.transaction_date) }}</div>
											</div>
										</div>
									</div>

									<!-- Card Actions -->
									<div class="px-5 py-3 bg-gray-50 border-t border-gray-200 flex items-center justify-end gap-2 mt-auto">
										<!-- View Details (Eye Icon) -->
										<Button
											variant="subtle"
											size="sm"
											@click.stop="handleViewDN(dn)"
											:title="__('View Details')"
										>
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
											</svg>
											<span>{{ __('View') }}</span>
										</Button>
									</div>
								</div>
							</div>
						</template>
					</div>
				</div>
			</div>
		</div>
	</Transition>

    <!-- Details Dialog -->
    <DeliveryNoteDetailDialog
        v-model="showDetails"
        :dn-name="selectedDNName"
        :pos-profile="posProfile"
        :currency="currency"
        @print-dn="handlePrintDN"
        @create-invoice="handleCreateInvoice"
        @open-invoice="(name) => emit('open-invoice', name)"
        @open-sales-order="(name) => emit('open-sales-order', name)"
    />

</template>

<script setup>
import { ref, watch } from "vue";
import { Button, createResource } from "frappe-ui";
import { useFormatters } from "@/composables/useFormatters";
import { formatCurrency as formatCurrencyUtil } from "@/utils/currency"; 
import { useToast } from "@/composables/useToast";
import { call } from "@/utils/apiWrapper";
import DeliveryNoteDetailDialog from "./DeliveryNoteDetailDialog.vue";
import DeliveryNoteFilters from "./DeliveryNoteFilters.vue";
import { useDeliveryNoteFilters } from "@/composables/useDeliveryNoteFilters";
import { usePOSCartStore } from "@/stores/posCart";
import { usePOSSettingsStore } from "@/stores/posSettings";

const props = defineProps({
	modelValue: Boolean,
	posProfile: String,
	currency: String
});

const emit = defineEmits(["update:modelValue", "open-invoice", "open-sales-order"]);

const { formatDate } = useFormatters();
const { showSuccess, showError } = useToast();
const cartStore = usePOSCartStore();

const show = ref(props.modelValue);
const deliveryNotes = ref([]);
const loading = ref(false);
const showDetails = ref(false);
const selectedDNName = ref("");

// Initialize filters
const { 
    filteredNotes, 
    uniqueCustomers, 
    uniqueProducts, 
    filterStats 
} = useDeliveryNoteFilters(deliveryNotes);

// Watchers
watch(
	() => props.modelValue,
	(val) => {
		show.value = val;
		if (val) {
			loadDeliveryNotes();
		}
	}
);

watch(show, (val) => {
	emit("update:modelValue", val);
});

// Methods
function handleClose() {
	show.value = false;
    showDetails.value = false;
}

function formatCurrency(amount, currency) {
    if (!currency) currency = props.currency || 'USD';
    return formatCurrencyUtil(amount, currency);
}

function getStatusColor(status) {
	switch (status) {
		case "Draft":
			return "bg-gray-100 text-gray-800";
		case "To Bill":
			return "bg-red-100 text-red-800";
		case "Completed":
			return "bg-green-100 text-green-800";
		case "Cancelled":
			return "bg-red-100 text-red-800";
		case "Return":
			return "bg-red-100 text-red-800";
		default:
			return "bg-blue-100 text-blue-800";
	}
}

async function loadDeliveryNotes() {
    if (!props.posProfile) return;
    loading.value = true;
    try {
        const result = await call("pos_next.api.delivery_notes.get_delivery_notes", {
            pos_profile: props.posProfile
        });
        deliveryNotes.value = result || [];
    } catch (error) {
        showError(error.message || __("Failed to load delivery notes"));
    } finally {
        loading.value = false;
    }
}

function handleViewDN(dn) {
    selectedDNName.value = dn.name;
    showDetails.value = true;
}

async function handlePrintDN(dn) {
    try {
         const printUrl = `/printview?doctype=Delivery%20Note&name=${dn.name}&format=Standard`;
         window.open(printUrl, '_blank');
    } catch (error) {
         console.error("Print failed", error);
    }
}

async function handleCreateInvoice(dn) {
    if (!dn) return;
    try {
        loading.value = true;
        
        // 1. Fetch mapped Sales Invoice items from backend
         const invoiceDoc = await call("pos_next.api.delivery_notes.make_invoice_from_delivery_note_mapped", {
             source_name: dn.name
         });
         
         if (!invoiceDoc) throw new Error(__("Failed to map invoice"));

         // 2. Clear current cart (resets mode to 'Sales Invoice' usually)
         cartStore.clearCart();

         // 3. Set Customer
         if (invoiceDoc.customer) {
             cartStore.setCustomer({
                 name: invoiceDoc.customer,
                 customer_name: invoiceDoc.customer_name || invoiceDoc.customer,
                 // customer_group, territory, etc. if needed
             });
         }
         
         // 4. Populate Cart
         if (invoiceDoc.items && invoiceDoc.items.length) {
             for (const item of invoiceDoc.items) {
                // Determine if stock item (usually yes for invoices from DN)
                // We use item.is_stock_item from mapped doc if available, or default to checking item details if needed.
                // Here we assume mapping is correct.
                
                await cartStore.addItem({
                    item_code: item.item_code,
                    item_name: item.item_name,
                    description: item.description,
                    uom: item.uom,
                    stock_uom: item.stock_uom,
                    conversion_factor: item.conversion_factor,
                    rate: item.rate, // Use mapped rate
                    price_list_rate: item.price_list_rate || item.rate,
                    is_stock_item: item.is_stock_item,
                    discount_percentage: item.discount_percentage,
                    discount_amount: item.discount_amount,
                    
                    // Reference fields for linking back to DN/SO
                    delivery_note: dn.name,
                    dn_detail: item.dn_detail,
                    sales_order: item.sales_order,
                    so_detail: item.so_detail,
                    against_sales_order: item.against_sales_order
                }, item.qty || 1, true, props.posProfile); // autoAdd=true to skip stock check? Or validation needed?
             }
         }
         
         // 5. Success feedback and close dialogs
         showSuccess(__("Invoice created from Delivery Note. Verify items and proceed to payment."));
         showDetails.value = false;
         show.value = false; // Close management overlay
         
    } catch (error) {
        showError(error.message || __("Failed to create Invoice"));
    } finally {
        loading.value = false;
    }
}

</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
	transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
	opacity: 0;
}
</style>
