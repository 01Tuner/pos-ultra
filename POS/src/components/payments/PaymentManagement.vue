<template>
	<!-- Full Page Overlay -->
	<Transition name="fade">
		<div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 z-[300]" @click.self="handleClose">
			<!-- Main Container -->
			<div class="fixed inset-0 flex items-center justify-center sm:p-4 z-50">
				<div class="w-full h-full sm:max-w-[95vw] sm:max-h-[95vh] bg-white sm:rounded-lg shadow-2xl overflow-hidden flex flex-col pt-safe pb-safe">
					<!-- Header -->
					<div class="flex items-center justify-between px-6 py-5 border-b bg-gradient-to-r from-blue-50 to-indigo-50 shrink-0">
						<div class="flex items-center gap-3">
							<div class="p-2 bg-blue-100 rounded-lg">
								<svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
								</svg>
							</div>
							<div>
								<h2 class="text-xl font-bold text-gray-900">{{ __('Payment Management') }}</h2>
								<p class="text-sm text-gray-600 flex items-center mt-0.5">
									{{ __('Settle outstanding balances and view payment history') }}
								</p>
							</div>
						</div>
						<div class="flex items-center gap-2">
							<button @click="handleClose" class="p-2 hover:bg-white/50 rounded-lg transition-colors">
								<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
								</svg>
							</button>
						</div>
					</div>

					<!-- Tabs -->
					<div class="flex border-b border-gray-200 bg-white shrink-0 px-6 pt-2">
						<button 
							@click="activeTab = 'new'"
							:class="['px-4 py-3 font-medium text-sm border-b-2 transition-colors', activeTab === 'new' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700']"
						>
							{{ __('New Payment') }}
						</button>
						<button 
							@click="activeTab = 'history'"
							:class="['px-4 py-3 font-medium text-sm border-b-2 transition-colors', activeTab === 'history' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700']"
						>
							{{ __('Payment History') }}
						</button>
					</div>

					<!-- Content Body -->
					<div class="flex-1 flex overflow-hidden bg-gray-50 relative">
						<!-- New Payment Tab -->
						<div v-show="activeTab === 'new'" class="absolute inset-0 grid grid-cols-1 md:grid-cols-3 md:grid-rows-[auto_1fr] overflow-y-auto md:overflow-hidden bg-white">
							
							<!-- Customer Selection -->
							<div class="md:col-span-2 md:col-start-1 md:row-start-1 order-1 flex flex-col shrink-0 border-b border-gray-100 p-6">
									<label class="block text-sm font-medium text-gray-700 mb-2">{{ __('Select Customer') }}</label>
									<div class="relative">
										<input 
											type="text" 
											v-model="customerSearch" 
											@focus="showCustomerDropdown = true"
											@input="debouncedSearchCustomer"
											:placeholder="__('Search for a customer...')"
											class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
										/>
										<svg class="absolute left-3 top-3.5 h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
											<path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
										</svg>
										<!-- Dropdown -->
										<div v-if="showCustomerDropdown && customerList.length > 0" class="absolute z-10 w-full mt-1 bg-white shadow-xl max-h-60 rounded-xl py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto sm:text-sm">
											<div v-for="cust in customerList" :key="'dd-'+cust.name" @click="selectCustomer(cust)" class="cursor-pointer select-none relative py-3 pl-4 pr-9 hover:bg-blue-50">
												<div class="flex items-center">
													<span class="font-normal block truncate w-1/2">{{ cust.customer_name }}</span>
													<span class="text-gray-500 text-xs ml-2 truncate w-1/2">{{ cust.name }}</span>
												</div>
											</div>
										</div>
									</div>
									<div class="mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between bg-blue-50 rounded-lg p-4 gap-3" v-if="selectedCustomer">
										<div class="min-w-0">
											<p class="text-sm font-semibold text-blue-900 truncate">{{ selectedCustomer.customer_name }}</p>
											<p class="text-xs text-blue-700 truncate">{{ selectedCustomer.name }}</p>
										</div>
										<div class="sm:text-right shrink-0">
											<p class="text-xs text-blue-700 uppercase tracking-wider">{{ __('Total Outstanding') }}</p>
											<p class="text-lg font-bold text-red-600">{{ formatCurrency(totalOutstanding, currency) }}</p>
										</div>
									</div>
								</div>

							<!-- Invoices List -->
							<div class="md:col-span-2 md:col-start-1 md:row-start-2 order-3 md:order-2 flex flex-col md:overflow-y-auto bg-gray-50 border-t border-gray-100 md:border-t-0 border-b md:border-b-0 border-gray-200 p-6">
								<h3 class="text-sm font-bold text-gray-700 uppercase tracking-wider mb-4" v-if="selectedCustomer">{{ __('Pending Invoices') }}</h3>
									
									<div v-if="loadingInvoices" class="flex justify-center p-8">
										<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
									</div>
									
									<div v-else-if="selectedCustomer && invoices.length === 0" class="text-center p-8 bg-white rounded-xl border border-dashed border-gray-300">
										<svg class="mx-auto h-12 w-12 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
										</svg>
										<p class="text-gray-500 font-medium">{{ __('No pending invoices to clear.') }}</p>
									</div>

									<div v-else-if="selectedCustomer" class="space-y-3 pb-8">
										<div v-for="inv in invoices" :key="'inv-'+inv.name" class="bg-white border rounded-lg p-4 shadow-sm flex flex-col lg:flex-row lg:items-center justify-between gap-4 transition-colors" :class="inv.allocated_amount > 0 ? 'border-blue-300 ring-1 ring-blue-100 bg-blue-50/20' : 'border-gray-200'">
											<div class="min-w-0">
												<h4 class="font-bold text-gray-900 truncate">{{ inv.name }}</h4>
												<p class="text-sm text-gray-500">{{ inv.posting_date }}</p>
											</div>
											<div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 sm:gap-6">
												<div class="flex justify-between sm:block sm:text-right">
													<p class="text-xs text-gray-500">{{ __('Invoice Total') }}</p>
													<p class="font-medium text-sm sm:text-base">{{ formatCurrency(inv.grand_total, inv.currency) }}</p>
												</div>
												<div class="flex justify-between sm:block sm:text-right">
													<p class="text-xs text-gray-500">{{ __('Outstanding') }}</p>
													<p class="font-bold text-red-600 text-sm sm:text-base">{{ formatCurrency(inv.outstanding_amount, inv.currency) }}</p>
												</div>
												<div class="w-full sm:w-32 mt-2 sm:mt-0">
													<label class="text-xs text-gray-500 mb-1 hidden sm:block">{{ __('Allocate') }}</label>
													<div class="relative">
														<span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 sm:hidden">{{ __('Alloc') }}:</span>
														<input type="number" v-model.number="inv.allocated_amount" @input="recalculateTotalAllocation" class="w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 text-right sm:text-sm pt-2 pb-2 pl-14 sm:pl-3" placeholder="0.00" min="0" :max="inv.outstanding_amount" />
													</div>
												</div>
											</div>
										</div>
									</div>
									
									<div v-else class="text-center p-12 text-gray-400">
										{{ __('Please select a customer first.') }}
									</div>
								</div>

							<!-- Right Pane: Payment Actions -->
							<div class="md:col-span-1 md:col-start-3 md:row-start-1 md:row-span-2 order-2 md:order-3 flex flex-col md:h-full bg-white md:border-l border-gray-200 border-b md:border-b-0 border-gray-200">
								<div class="p-6 flex-1">
									<h3 class="text-lg font-bold text-gray-900 mb-6">{{ __('Payment Summary') }}</h3>
									
									<div class="space-y-6">
										<div>
											<label class="block text-sm font-medium text-gray-700 mb-2">{{ __('Payment Amount') }}</label>
											<div class="relative rounded-md shadow-sm">
												<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
													<span class="text-gray-500 sm:text-sm">{{ getCurrencySymbol() }}</span>
												</div>
												<input type="number" v-model.number="paymentAmount" @input="autoAllocate" class="focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 pr-12 sm:text-lg text-right font-bold border-gray-300 rounded-xl pt-3 pb-3 bg-gray-50" placeholder="0.00" min="0" />
												<div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
													<span class="text-gray-500 sm:text-sm">{{ currency }}</span>
												</div>
											</div>
											<div class="mt-2 flex justify-between">
												<button @click="fillFullOutstanding" class="text-xs font-semibold text-blue-600 hover:text-blue-800">{{ __('Pay Full Outstanding') }}</button>
												<button @click="autoAllocate" class="text-xs font-semibold text-indigo-600 hover:text-indigo-800">{{ __('Auto Allocate') }}</button>
											</div>
										</div>
                                        
                                        <div class="mt-4">
											<label class="block text-sm font-medium text-gray-700 mb-2">{{ __('Write Off Amount') }}</label>
											<div class="relative">
												<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
													<span class="text-gray-500 sm:text-sm">{{ getCurrencySymbol() }}</span>
												</div>
												<input type="number" v-model.number="writeOffAmount" @input="autoAllocate" min="0" step="0.01" class="focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 pr-12 py-3 sm:text-lg text-right font-bold border-gray-300 rounded-xl bg-yellow-50" :placeholder="__('0.00')" />
												<div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
													<span class="text-gray-500 sm:text-sm">{{ currency }}</span>
												</div>
											</div>
                                            <div class="mt-2 flex justify-start">
												<button @click="fillWriteOffOutstanding" class="text-xs font-semibold text-yellow-600 hover:text-yellow-800">{{ __('Write Off Full Outstanding') }}</button>
											</div>
										</div>

										<div>
											<label class="block text-sm font-medium text-gray-700 mb-2">{{ __('Mode of Payment') }}</label>
											<select v-model="modeOfPayment" class="mt-1 block w-full pl-3 pr-10 py-3 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-xl bg-gray-50">
												<option v-for="mode in paymentModes" :key="mode.name" :value="mode.name">{{ mode.name }}</option>
											</select>
										</div>

										<div class="bg-gray-50 p-4 rounded-xl border border-gray-200 mt-6">
											<div class="flex justify-between items-center mb-2">
												<span class="text-sm text-gray-600">{{ __('Amount Allocated') }}:</span>
												<span class="font-medium" :class="totalAllocated > ((parseFloat(paymentAmount) || 0) + (parseFloat(writeOffAmount) || 0)) ? 'text-red-600' : 'text-gray-900'">{{ formatCurrency(totalAllocated, currency) }}</span>
											</div>
											<div class="flex justify-between items-center border-t border-gray-200 pt-2" v-if="((parseFloat(paymentAmount) || 0) + (parseFloat(writeOffAmount) || 0)) > totalAllocated">
												<span class="text-sm text-gray-600">{{ __('Unallocated Amount') }}:</span>
												<span class="font-medium text-green-600">{{ formatCurrency(((parseFloat(paymentAmount) || 0) + (parseFloat(writeOffAmount) || 0)) - totalAllocated, currency) }}</span>
											</div>
										</div>
									</div>
								</div>
								
								<div class="p-6 bg-gray-50 border-t border-gray-200 mt-auto shrink-0">
									<Button 
										variant="solid" 
										theme="blue" 
										class="w-full py-4 text-base font-bold rounded-xl shadow-lg hover:shadow-xl transition-all" 
										:loading="submitting"
										:disabled="((parseFloat(paymentAmount) || 0) + (parseFloat(writeOffAmount) || 0)) <= 0 || !selectedCustomer"
										@click="submitPayment"
									>
										{{ __('Submit Payment') }}
									</Button>
								</div>
							</div>
						</div>

						<!-- Payment History Tab -->
						<div v-show="activeTab === 'history'" class="absolute inset-0 flex flex-col p-6 overflow-y-auto">
							<div class="flex items-center justify-between mb-4">
								<h3 class="text-lg font-bold text-gray-900">{{ __('Recent Payments (This POS Profile)') }}</h3>
								<Button @click="loadPaymentHistory" :loading="loadingHistory" variant="ghost" size="sm">
									<template #prefix>
										<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
										</svg>
									</template>
									{{ __('Refresh') }}
								</Button>
							</div>
							
							<div v-if="loadingHistory && history.length === 0" class="flex justify-center p-12">
								<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
							</div>
							
							<div v-else-if="history.length === 0" class="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center text-gray-500">
								{{ __('No payments recorded from this terminal yet.') }}
							</div>
							
							<div v-else class="bg-transparent sm:bg-white sm:rounded-xl sm:shadow sm:border border-gray-200 overflow-hidden">
								<!-- Mobile View -->
								<div class="block sm:hidden space-y-4 px-1 pb-8">
									<div v-for="pay in history" :key="'mobpay-'+pay.name" class="bg-white border border-gray-200 rounded-xl p-4 shadow-sm flex flex-col gap-3">
										<div class="flex justify-between items-start border-b border-gray-50 pb-2">
											<div>
												<div class="text-sm font-bold text-blue-600">{{ pay.name }}</div>
												<div class="text-xs text-gray-500">{{ pay.posting_date }}</div>
											</div>
											<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
												{{ pay.mode_of_payment }}
											</span>
										</div>
										<div class="flex justify-between items-end">
											<div class="min-w-0 flex-1 pr-2">
												<div class="text-xs text-gray-500">{{ __('Customer') }}</div>
												<div class="text-sm font-medium text-gray-900 truncate">{{ pay.party_name || pay.party }}</div>
											</div>
											<div class="text-right shrink-0">
												<div class="text-lg font-bold text-gray-900">{{ formatCurrency(pay.paid_amount, currency) }}</div>
											</div>
										</div>
										<div class="pt-2 flex justify-end">
											<button @click="printPayment(pay)" class="text-blue-600 bg-blue-50 hover:bg-blue-100 px-4 py-1.5 rounded-lg text-sm font-medium flex items-center">
												<svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
												{{ __('Print') }}
											</button>
										</div>
									</div>
								</div>

								<!-- Desktop View -->
								<div class="hidden sm:block overflow-x-auto w-full">
									<table class="min-w-full divide-y divide-gray-200">
										<thead class="bg-gray-50">
											<tr>
												<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ __('Payment Entry') }}</th>
												<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ __('Date') }}</th>
												<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ __('Customer') }}</th>
												<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ __('Mode') }}</th>
												<th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">{{ __('Amount') }}</th>
												<th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">{{ __('Actions') }}</th>
											</tr>
										</thead>
										<tbody class="bg-white divide-y divide-gray-200">
											<tr v-for="pay in history" :key="'deskpay-'+pay.name" class="hover:bg-gray-50">
												<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">{{ pay.name }}</td>
												<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ pay.posting_date }}</td>
												<td class="px-6 py-4 overflow-hidden text-ellipsis max-w-[200px]">
													<div class="text-sm font-medium text-gray-900 truncate">{{ pay.party_name || pay.party }}</div>
												</td>
												<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
													<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
														{{ pay.mode_of_payment }}
													</span>
												</td>
												<td class="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900 text-right">
													{{ formatCurrency(pay.paid_amount, currency) }}
												</td>
												<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
													<button @click="printPayment(pay)" class="text-blue-600 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 px-3 py-1 rounded-md transition-colors flex items-center justify-end ml-auto">
														<svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
														{{ __('Print') }}
													</button>
												</td>
											</tr>
										</tbody>
									</table>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</Transition>
</template>

<script setup>
import { ref, watch, onMounted, computed } from "vue";
import { Button } from "frappe-ui";
import { formatCurrency as formatCurrencyUtil } from "@/utils/currency"; 
import { useToast } from "@/composables/useToast";
import { call } from "@/utils/apiWrapper";
import { usePOSSettingsStore } from "@/stores/posSettings";
import { printPaymentReceipt } from "@/utils/printInvoice";

const props = defineProps({
	modelValue: Boolean,
	posProfile: String,
    currency: String,
	defaultCustomer: Object,
	posOpeningShift: String
});

const emit = defineEmits(["update:modelValue"]);

const { showSuccess, showError, showWarning } = useToast();
const settingsStore = usePOSSettingsStore();

const show = ref(props.modelValue);
const activeTab = ref('new');

// New Payment State
const customerSearch = ref("");
const showCustomerDropdown = ref(false);
const customerList = ref([]);
const selectedCustomer = ref(null);
const invoices = ref([]);
const loadingInvoices = ref(false);
const paymentAmount = ref(0);
const writeOffAmount = ref(0);
const modeOfPayment = ref("");
const totalAllocated = ref(0);
const submitting = ref(false);
let searchTimeout = null;

// History State
const history = ref([]);
const loadingHistory = ref(false);

const paymentModes = computed(() => {
	if (settingsStore.currentProfile && settingsStore.currentProfile.payments) {
		return settingsStore.currentProfile.payments.map(p => ({
			name: p.mode_of_payment,
			type: p.type
		}));
	}
	return [{ name: "Cash", type: "Cash" }];
});

const totalOutstanding = computed(() => {
	return invoices.value.reduce((sum, inv) => sum + (inv.outstanding_amount || 0), 0);
});

// Watchers
watch(
	() => props.modelValue,
	(val) => {
		show.value = val;
		if (val) {
			if (!modeOfPayment.value && paymentModes.value.length > 0) {
				modeOfPayment.value = paymentModes.value[0].name;
			}
			if (props.defaultCustomer) {
				activeTab.value = 'new';
				selectCustomer(props.defaultCustomer);
			} else if (activeTab.value === 'history') {
				loadPaymentHistory();
			}
		}
	}
);

watch(
	() => props.defaultCustomer,
	(newVal) => {
		if (newVal) {
			activeTab.value = 'new';
			selectCustomer(newVal);
		}
	}
);

watch(show, (val) => {
	emit("update:modelValue", val);
});

watch(activeTab, (val) => {
	if(val === 'history') loadPaymentHistory();
});

// Methods
function handleClose() {
	show.value = false;
}

function formatCurrency(amount, curr) {
    if (!curr) curr = props.currency || 'USD';
    return formatCurrencyUtil(amount, curr);
}

function getCurrencySymbol() {
	// Simple fallback, actual formatting handles symbol
	return props.currency || '$';
}

function debouncedSearchCustomer() {
	showCustomerDropdown.value = true;
	if (searchTimeout) clearTimeout(searchTimeout);
	searchTimeout = setTimeout(async () => {
		if (customerSearch.value.length < 2) {
			customerList.value = [];
			return;
		}
		try {
			const res = await call("pos_next.api.customers.get_customers", {
				search_term: customerSearch.value,
				pos_profile: props.posProfile,
				limit: 10
			});
			customerList.value = res || [];
		} catch (e) {
			console.error(e);
		}
	}, 300);
}

function selectCustomer(cust) {
	selectedCustomer.value = cust;
	customerSearch.value = cust.customer_name;
	showCustomerDropdown.value = false;
	paymentAmount.value = 0;
	totalAllocated.value = 0;
	loadInvoices();
}

async function loadInvoices() {
	if(!selectedCustomer.value) return;
	loadingInvoices.value = true;
	try {
		const res = await call("pos_next.api.payments.get_customer_outstanding_invoices", {
			customer: selectedCustomer.value.name
		});
		invoices.value = (res || []).map(inv => ({
			...inv,
			allocated_amount: 0
		}));
	} catch(e) {
		showError(e.message || __("Error fetching invoices"));
	} finally {
		loadingInvoices.value = false;
	}
}

function recalculateTotalAllocation() {
	totalAllocated.value = invoices.value.reduce((sum, inv) => {
		// constrain to max outstanding and min 0
		let val = parseFloat(inv.allocated_amount) || 0;
		if (val > inv.outstanding_amount) val = inv.outstanding_amount;
		if (val < 0) val = 0;
		inv.allocated_amount = val;
		return sum + val;
	}, 0);
}

function fillFullOutstanding() {
	paymentAmount.value = parseFloat(totalOutstanding.value);
	writeOffAmount.value = 0;
	autoAllocate();
}

function fillWriteOffOutstanding() {
	let writeOff = parseFloat(totalOutstanding.value) - (parseFloat(paymentAmount.value) || 0);
	if (writeOff < 0) writeOff = 0;
	writeOffAmount.value = writeOff;
	autoAllocate();
}

function autoAllocate() {
	let remaining = (parseFloat(paymentAmount.value) || 0) + (parseFloat(writeOffAmount.value) || 0);
	invoices.value.forEach(inv => {
		if (remaining >= inv.outstanding_amount) {
			inv.allocated_amount = inv.outstanding_amount;
			remaining -= inv.outstanding_amount;
		} else if (remaining > 0) {
			inv.allocated_amount = remaining;
			remaining = 0;
		} else {
			inv.allocated_amount = 0;
		}
	});
	recalculateTotalAllocation();
}

async function submitPayment() {
	const totalInput = (parseFloat(paymentAmount.value) || 0) + (parseFloat(writeOffAmount.value) || 0);
	if(totalAllocated.value > totalInput) {
		showWarning(__("Allocated amount cannot exceed Payment Amount + Write Off"));
		return;
	}
	if(totalInput <= 0) {
		showWarning(__("Enter a valid payment or write off amount"));
		return;
	}

	submitting.value = true;
	const allocations = invoices.value
		.filter(inv => inv.allocated_amount > 0)
		.map(inv => ({
			name: inv.name,
			allocated_amount: inv.allocated_amount
		}));

	try {
		const res = await call("pos_next.api.payments.create_customer_payment", {
			customer: selectedCustomer.value.name,
			mode_of_payment: modeOfPayment.value,
			amount: paymentAmount.value || 0,
			write_off_amount: writeOffAmount.value || 0,
			pos_profile: props.posProfile,
			allocations: JSON.stringify(allocations),
			pos_opening_shift: props.posOpeningShift
		});
		
		showSuccess(__("Payment Successful!"));
		// Reset state
		selectedCustomer.value = null;
		customerSearch.value = "";
		invoices.value = [];
		paymentAmount.value = 0;
		writeOffAmount.value = 0;
		totalAllocated.value = 0;
		
	} catch(e) {
		showError(e.message || __("Failed to register payment"));
	} finally {
		submitting.value = false;
	}
}

async function loadPaymentHistory() {
	loadingHistory.value = true;
	try {
		const res = await call("pos_next.api.payments.get_pos_profile_payments", {
			pos_profile: props.posProfile,
			limit: 50
		});
		history.value = res || [];
	} catch(e) {
		showError(e.message || __("Error fetching payment history"));
	} finally {
		loadingHistory.value = false;
	}
}

async function printPayment(pay) {
	try {
		await printPaymentReceipt({
			voucher_type: "Payment Entry",
			voucher_no: pay.name
		});
	} catch (error) {
		console.error("Error printing payment:", error);
		showError(__("Failed to print payment receipt"));
	}
}

// Click outside dropdown handler
onMounted(() => {
	document.addEventListener('click', (e) => {
		const isInput = e.target.closest('input');
		const isDropdown = e.target.closest('.shadow-xl');
		if (!isInput && !isDropdown) {
			showCustomerDropdown.value = false;
		}
	});
});
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
input[type=number]::-webkit-inner-spin-button, 
input[type=number]::-webkit-outer-spin-button { 
  -webkit-appearance: none; 
  margin: 0; 
}
</style>
