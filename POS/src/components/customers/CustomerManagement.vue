<template>
	<!-- Full Page Overlay -->
	<Transition name="fade">
		<div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 z-[300]" @click.self="handleClose">
			<!-- Main Container -->
			<div class="fixed inset-0 flex items-center justify-center sm:p-4 z-50">
				<div class="w-full h-full sm:max-w-[95vw] sm:max-h-[95vh] bg-white sm:rounded-lg shadow-2xl overflow-hidden flex flex-col pt-safe pb-safe">
					<!-- Header -->
					<div class="flex items-center justify-between px-6 py-5 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
						<div class="flex items-center gap-3">
							<div class="p-2 bg-blue-100 rounded-lg">
								<svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
								</svg>
							</div>
							<div>
								<h2 class="text-xl font-bold text-gray-900">{{ __('Customer Management') }}</h2>
								<p class="text-sm text-gray-600 flex items-center mt-0.5">
									{{ __('View customers and outstanding balances') }}
								</p>
							</div>
						</div>
						<div class="flex items-center gap-2">
							<!-- Create Customer Button -->
							<Button @click="showCreateCustomer = true" variant="solid" theme="blue" size="sm">
								<template #prefix>
									<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
									</svg>
								</template>
								{{ __('New Customer') }}
							</Button>
							<Button @click="loadCustomers" :loading="loading" variant="ghost" size="sm">
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
					<div class="flex-1 flex flex-col overflow-hidden bg-gray-50">
						<!-- Search Bar -->
						<div class="p-4 border-b bg-white">
							<div class="relative max-w-md">
								<div class="absolute inset-y-0 start-0 pl-3 flex items-center pointer-events-none">
									<svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
									</svg>
								</div>
								<input 
									type="text" 
									v-model="searchQuery" 
									@input="debouncedSearch"
									:placeholder="__('Search customers by name, mobile or email...')" 
									class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition duration-150 ease-in-out" 
								/>
							</div>
						</div>

						<!-- Loading State -->
						<div v-if="loading && customers.length === 0" class="flex flex-col items-center justify-center py-16 flex-1">
							<div class="animate-spin rounded-full h-12 w-12 border-b-3 border-blue-500 mb-4"></div>
							<p class="text-sm font-medium text-gray-600">{{ __('Loading Customers...') }}</p>
						</div>

						<!-- Empty State -->
						<div v-else-if="customers.length === 0" class="flex flex-col items-center justify-center py-16 text-center flex-1">
							<svg class="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
							</svg>
							<p class="text-gray-600 font-medium">{{ __('No Customers found') }}</p>
						</div>

						<!-- Table (Desktop) / Cards (Mobile) -->
						<div v-else class="flex-1 overflow-y-auto px-0 sm:px-4 py-2 sm:py-4">
							<div class="bg-transparent sm:bg-white sm:shadow sm:rounded-lg sm:border sm:border-gray-200 overflow-hidden">
								
								<!-- Mobile List View -->
								<div class="block sm:hidden space-y-3 px-3 overflow-x-hidden">
									<div v-for="customer in customers" :key="'mob-'+customer.name" class="bg-white border border-gray-200 rounded-xl shadow-sm p-4 hover:shadow-md transition-shadow">
										<div class="flex items-start justify-between mb-3 border-b border-gray-100 pb-3">
											<div class="flex items-center gap-3 w-full">
												<div class="h-10 w-10 shrink-0 bg-blue-100 rounded-full flex items-center justify-center">
													<span class="text-blue-600 font-bold text-lg">{{ customer.customer_name ? customer.customer_name.charAt(0).toUpperCase() : 'C' }}</span>
												</div>
												<div class="flex-1 min-w-0">
													<h3 class="text-sm font-bold text-gray-900 truncate">{{ customer.customer_name || customer.name }}</h3>
													<p class="text-xs text-gray-500 truncate">{{ customer.name }}</p>
												</div>
											</div>
										</div>
										<div class="space-y-2 mb-4">
											<div class="text-sm flex items-center break-all" v-if="customer.mobile_no">
												<svg class="h-4 w-4 mr-2 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path></svg>
												<span class="text-gray-700 min-w-0 break-words">{{ customer.mobile_no }}</span>
											</div>
											<div class="text-sm flex items-center break-all" v-if="customer.email_id">
												<svg class="h-4 w-4 mr-2 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
												<span class="text-gray-700 min-w-0 break-words">{{ customer.email_id }}</span>
											</div>
										</div>
										<div class="flex items-center justify-between border-t border-gray-100 pt-3">
											<div>
												<span class="text-xs text-gray-500 block block mb-0.5">{{ __('Balance') }}</span>
												<span :class="customer.balance > 0 ? 'text-red-600 font-bold' : (customer.balance < 0 ? 'text-green-600 font-bold' : 'text-gray-700 font-medium')">
													{{ formatCurrency(customer.balance, currency) }}
												</span>
											</div>
											<button @click="emit('make-payment', customer)" class="w-auto bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center" v-if="customer.balance > 0">
												<svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
												{{ __('Pay') }}
											</button>
										</div>
									</div>
								</div>

								<!-- Desktop Table View -->
								<table class="hidden sm:table min-w-full divide-y divide-gray-200 w-full table-fixed">
									<thead class="bg-gray-50">
										<tr>
											<th scope="col" class="w-2/5 px-6 py-3 text-start text-xs font-medium text-gray-500 uppercase tracking-wider">
												{{ __('Customer Name') }}
											</th>
											<th scope="col" class="w-1/4 px-6 py-3 text-start text-xs font-medium text-gray-500 uppercase tracking-wider">
												{{ __('Contact Details') }}
											</th>
											<th scope="col" class="w-1/4 px-6 py-3 text-end text-xs font-medium text-gray-500 uppercase tracking-wider">
												{{ __('Outstanding Balance') }}
											</th>
											<th scope="col" class="w-16 px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
												{{ __('Actions') }}
											</th>
										</tr>
									</thead>
									<tbody class="bg-white divide-y divide-gray-200">
										<tr v-for="customer in customers" :key="'desk-'+customer.name" class="hover:bg-gray-50 transition-colors">
											<td class="px-6 py-4 px-6 py-4 overflow-hidden text-ellipsis">
												<div class="flex items-center">
													<div class="h-10 w-10 flex-shrink-0 bg-blue-100 rounded-full flex items-center justify-center hidden md:flex">
														<span class="text-blue-600 font-bold text-lg">{{ customer.customer_name ? customer.customer_name.charAt(0).toUpperCase() : 'C' }}</span>
													</div>
													<div class="md:ms-4 flex-1 min-w-0">
														<div class="text-sm font-medium text-gray-900 truncate">{{ customer.customer_name || customer.name }}</div>
														<div class="text-sm text-gray-500 truncate">{{ customer.name }}</div>
													</div>
												</div>
											</td>
											<td class="px-6 py-4 overflow-hidden text-ellipsis">
												<div class="text-sm text-gray-900 truncate" v-if="customer.mobile_no" :title="customer.mobile_no">
													<span class="inline-flex items-center max-w-full">
														<svg class="h-3 w-3 mr-1 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path></svg>
														<span class="truncate">{{ customer.mobile_no }}</span>
													</span>
												</div>
												<div class="text-sm text-gray-500 truncate mt-1" v-if="customer.email_id" :title="customer.email_id">
													<span class="inline-flex items-center max-w-full">
														<svg class="h-3 w-3 mr-1 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
														<span class="truncate">{{ customer.email_id }}</span>
													</span>
												</div>
												<div v-if="!customer.mobile_no && !customer.email_id" class="text-sm text-gray-400">
													{{ __('No contact info') }}
												</div>
											</td>
											<td class="px-6 py-4 whitespace-nowrap text-end text-sm font-medium">
												<span :class="customer.balance > 0 ? 'text-red-600 font-bold' : (customer.balance < 0 ? 'text-green-600 font-bold' : 'text-gray-500')">
													{{ formatCurrency(customer.balance, currency) }}
												</span>
											</td>
											<td class="px-6 py-4 whitespace-nowrap text-right text-sm">
												<button @click="emit('make-payment', customer)" class="text-blue-600 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-md transition-colors flex items-center justify-end ml-auto font-medium" v-if="customer.balance > 0">
													<svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
													{{ __('Pay') }}
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
	</Transition>

	<!-- Create Customer Dialog -->
	<CreateCustomerDialog
		v-model="showCreateCustomer"
		@customer-created="handleCustomerCreated"
	/>
</template>

<script setup>
import { ref, watch } from "vue";
import { Button } from "frappe-ui";
import { formatCurrency as formatCurrencyUtil } from "@/utils/currency"; 
import { useToast } from "@/composables/useToast";
import { call } from "@/utils/apiWrapper";
import CreateCustomerDialog from "@/components/sale/CreateCustomerDialog.vue";

const props = defineProps({
	modelValue: Boolean,
	posProfile: String,
    currency: String
});

const emit = defineEmits(["update:modelValue", "make-payment"]);

const { showSuccess, showError } = useToast();

const show = ref(props.modelValue);
const customers = ref([]);
const loading = ref(false);
const searchQuery = ref("");
const showCreateCustomer = ref(false);
let searchTimeout = null;

// Watchers
watch(
	() => props.modelValue,
	(val) => {
		show.value = val;
		if (val) {
			loadCustomers();
		}
	}
);

watch(show, (val) => {
	emit("update:modelValue", val);
});

// Methods
function handleClose() {
	show.value = false;
}

function formatCurrency(amount, curr) {
    if (!curr) curr = props.currency || 'USD';
    return formatCurrencyUtil(amount, curr);
}

function debouncedSearch() {
	if (searchTimeout) clearTimeout(searchTimeout);
	searchTimeout = setTimeout(() => {
		loadCustomers();
	}, 500);
}

async function loadCustomers() {
    if (!props.posProfile) return;
    loading.value = true;
    try {
        const result = await call("pos_next.api.customer_dashboard.get_customers_with_balances", {
            pos_profile: props.posProfile,
            search_term: searchQuery.value,
			limit: 100
        });
        customers.value = result || [];
    } catch (error) {
        showError(error.message || __("Failed to load customers"));
    } finally {
        loading.value = false;
    }
}

function handleCustomerCreated(customer) {
	showCreateCustomer.value = false;
	loadCustomers();
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
