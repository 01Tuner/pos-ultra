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
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
								</svg>
							</div>
							<div>
								<h2 class="text-xl font-bold text-gray-900">{{ __('Sales Order Management') }}</h2>
								<p class="text-sm text-gray-600 flex items-center mt-0.5">
									{{ __('View and manage sales orders') }}
								</p>
							</div>
						</div>
						<div class="flex items-center gap-2">
							<Button @click="loadSalesOrders" :loading="loading" variant="ghost" size="sm">
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
						<!-- Filters Component -->
						<div class="mb-6">
							<SalesOrderFilters
								:unique-customers="salesOrderFilters.uniqueCustomers.value"
								:unique-products="salesOrderFilters.uniqueProducts.value"
								:filter-stats="salesOrderFilters.filterStats.value"
							/>
						</div>

						<!-- Loading State -->
						<div v-if="loading && salesOrders.length === 0" class="flex flex-col items-center justify-center py-16">
							<div class="animate-spin rounded-full h-12 w-12 border-b-3 border-blue-500 mb-4"></div>
							<p class="text-sm font-medium text-gray-600">{{ __('Loading Sales Orders...') }}</p>
						</div>

						<!-- Empty State -->
						<div v-else-if="filteredOrders.length === 0" class="flex flex-col items-center justify-center py-16 text-center">
							<svg class="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
							</svg>
							<p class="text-gray-600 font-medium">{{ __('No Sales Orders found') }}</p>
						</div>

						<!-- Orders Grid -->
						<div v-else class="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
							<div v-for="order in filteredOrders" :key="order.name" class="bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-lg transition-all overflow-hidden flex flex-col cursor-default">
								<!-- Card Header -->
								<div class="bg-gradient-to-r from-gray-50 to-blue-50 px-5 py-4 border-b border-gray-200">
									<div class="flex items-start justify-between mb-2">
										<div class="flex-1">
											<h3 class="text-base font-bold text-gray-900">{{ order.name }}</h3>
											<div class="flex items-center gap-2 mt-1">
												<span :class="['text-xs px-2.5 py-1 rounded-full font-semibold', getStatusColor(order.status)]">
													{{ __(order.status) }}
												</span>
											</div>
										</div>
										<div class="text-end ms-3">
											<div class="text-xs text-gray-500 mb-1">{{ __('Total') }}</div>
											<div class="text-lg font-bold text-blue-600">{{ formatCurrency(order.grand_total, order.currency) }}</div>
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
											<div class="text-sm font-semibold text-gray-900">{{ order.customer_name || order.customer }}</div>
										</div>
									</div>

									<!-- Date & Time -->
									<div class="flex items-start">
										<svg class="w-5 h-5 text-gray-400 me-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
										</svg>
										<div class="flex-1">
											<div class="text-xs text-gray-500">{{ __('Date') }}</div>
											<div class="text-sm font-medium text-gray-900">{{ formatDate(order.transaction_date) }}</div>
										</div>
									</div>
								</div>

								<!-- Card Actions -->
								<div class="px-5 py-3 bg-gray-50 border-t border-gray-200 flex items-center justify-end gap-2 mt-auto">
									<!-- View Details (Eye Icon) -->
									<Button
										variant="subtle"
										size="sm"
                                        @click.stop="handleViewOrder(order)"
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
					</div>
				</div>
			</div>
		</div>
	</Transition>

    <!-- Details Dialog -->
    <SalesOrderDetailDialog
        v-model="showDetails"
        :order-name="selectedOrderName"
        :pos-profile="posProfile"
        :currency="currency"
        @print-order="handlePrintOrder"
        @order-cancelled="handleOrderCancelled"
		@invoice-created="handleClose"
    />

	<!-- Payment Dialog -->
	<PaymentDialog
		v-if="showPaymentDialog"
		v-model="showPaymentDialog"
		:pos-profile="posProfile"
		:grand-total="selectedPaymentOrder?.grand_total || 0"
		:currency="selectedPaymentOrder?.currency || currency"
		:customer="selectedPaymentOrder?.customer"
		:company="selectedPaymentOrder?.company"
		:allow-credit-sale="false" 
		:allow-partial-payment="true"
		is-sales-order
		@payment-completed="handlePaymentCompleted"
	/>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import { Button, createResource } from "frappe-ui";
import { useFormatters } from "@/composables/useFormatters";
import { formatCurrency as formatCurrencyUtil } from "@/utils/currency"; 
import { useToast } from "@/composables/useToast";
import { call } from "@/utils/apiWrapper";
import { printSalesOrderByName } from "@/utils/printInvoice";
import SalesOrderDetailDialog from "./SalesOrderDetailDialog.vue";
import SalesOrderFilters from "./SalesOrderFilters.vue";
import PaymentDialog from "@/components/sale/PaymentDialog.vue";
import { useSalesOrderFilters } from "@/composables/useSalesOrderFilters";

const props = defineProps({
	modelValue: Boolean,
	posProfile: String,
    currency: String
});

const emit = defineEmits(["update:modelValue"]);

const { formatDate } = useFormatters();
const { showSuccess, showError } = useToast();

const show = ref(props.modelValue);
const salesOrders = ref([]);
const loading = ref(false);
const showDetails = ref(false);
const selectedOrderName = ref("");
const showPaymentDialog = ref(false);
const selectedPaymentOrder = ref(null);

// Initialize filter composable
const salesOrdersRef = computed(() => salesOrders.value);
const salesOrderFilters = useSalesOrderFilters(salesOrdersRef);
const filteredOrders = salesOrderFilters.filteredOrders;

// Watchers
watch(
	() => props.modelValue,
	(val) => {
		show.value = val;
		if (val) {
			loadSalesOrders();
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
		case "To Deliver and Bill":
			return "bg-orange-100 text-orange-800";
		case "To Bill":
			return "bg-red-100 text-red-800";
		case "To Deliver":
			return "bg-yellow-100 text-yellow-800";
		case "Completed":
			return "bg-green-100 text-green-800";
		case "Cancelled":
			return "bg-red-100 text-red-800";
		default:
			return "bg-blue-100 text-blue-800";
	}
}

async function loadSalesOrders() {
    if (!props.posProfile) return;
    loading.value = true;
    try {
        const result = await call("pos_next.api.sales_orders.get_sales_orders", {
            pos_profile: props.posProfile
        });
        salesOrders.value = result || [];
    } catch (error) {
        showError(error.message || __("Failed to load sales orders"));
    } finally {
        loading.value = false;
    }
}

function handleViewOrder(order) {
    selectedOrderName.value = order.name;
    showDetails.value = true;
}

function handleOrderCancelled() {
    loadSalesOrders();
}

async function handlePrintOrder(order) {
    try {
        await printSalesOrderByName(order.name);
    } catch (error) {
        // Fallback or specific SO print
        console.error("Print failed", error);
        const printUrl = `/printview?doctype=Sales%20Order&name=${order.name}&format=Standard`;
        window.open(printUrl, '_blank');
    }
}

function canMakePayment(order) {
    // Show payment if not fully paid (advance < grand_total) and status allows (not Cancelled/Completed)
    // Adjust logic based on your exact status workflow
    const isFullyPaid = (order.advance_paid || 0) >= order.grand_total;
    const isCancelled = order.status === 'Cancelled';
	const isCompleted = order.status === 'Completed';
    return !isFullyPaid && !isCancelled && !isCompleted;
}

function canCancel(order) {
    return order.status !== 'Cancelled' && order.status !== 'Completed' && order.status !== 'Return';
}

function handleOpenPayment(order) {
    selectedPaymentOrder.value = order;
    showPaymentDialog.value = true;
}

async function handlePaymentCompleted(paymentData) {
    // Here we should call an API to create Payment Entry against Sales Order
    // PaymentDialog returns payment entries.
    // For now, let's assume we handle it or call an API here.
	// Since PaymentDialog usually handles the payment creation via an API call internally? 
	// CHECK PaymentDialog usage: It emits 'payment-completed' but does it save? 
	// In POSSale.vue URL: `submitOrder` handles it.
	// We need to implement `submitPayment` here.
	
	if (!selectedPaymentOrder.value) return;

	try {
        await call("pos_next.api.sales_orders.create_sales_order_payment", {
            sales_order: selectedPaymentOrder.value.name,
			payments: paymentData.payments
        });
		showSuccess(__("Payment created successfully"));
		showPaymentDialog.value = false;
		loadSalesOrders();
	} catch (error) {
		showError(error.message || __("Failed to create payment"));
	}
}

async function handleCancelOrder(order) {
     if (!confirm(__("Are you sure you want to cancel Sales Order {0}?", [order.name]))) {
        return;
    }

    try {
        await call("pos_next.api.sales_orders.cancel_sales_order", {
            name: order.name
        });
        showSuccess(__("Sales Order cancelled successfully"));
        loadSalesOrders();
    } catch (error) {
         showError(error.message || __("Failed to cancel sales order"));
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
