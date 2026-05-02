<template>
	<!-- Management Bar Container -->
	<!-- Desktop: Sidebar on the left (visible on xl and up) -->
	<!-- Mobile: Fixed footer at the bottom (hidden on xl and up) -->
	<div
		class="management-bar fixed bottom-0 left-0 right-0 z-[110] h-16 bg-white border-t border-gray-200 flex flex-row items-center px-2 xl:static xl:h-full xl:w-16 xl:flex-shrink-0 xl:border-t-0 xl:border-e xl:flex-col xl:py-4 xl:gap-2 xl:shadow-none shadow-[0_-2px_10px_rgba(0,0,0,0.05)]"
	>
		<!-- Desktop View (xl+) -->
		<template v-if="settingsStore">
			<div class="hidden xl:flex flex-col gap-2 items-center w-full">
				<!-- Dashboard -->
				<button @click="handleMenuClick('dashboard')" :class="getMenuClass('dashboard')" :title="__('Dashboard')">
					<FeatherIcon name="layout" class="w-5 h-5" />
					<div class="tooltip">{{ __('Dashboard') }}</div>
				</button>

				<!-- Promotions -->
				<button v-if="settingsStore.allowPromotion" @click="handleMenuClick('promotions')" :class="getMenuClass('promotions')" :title="__('Promotions')">
					<FeatherIcon name="tag" class="w-5 h-5" />
					<div class="tooltip">{{ __('Promotions') }}</div>
				</button>

				<!-- Products -->
				<button @click="handleMenuClick('products')" :class="getMenuClass('products')" :title="__('Products')">
					<FeatherIcon name="package" class="w-5 h-5" />
					<div class="tooltip">{{ __('Products') }}</div>
				</button>

				<!-- Customers -->
				<button @click="handleMenuClick('customers')" :class="getMenuClass('customers')" :title="__('Customers')">
					<FeatherIcon name="users" class="w-5 h-5" />
					<div class="tooltip">{{ __('Customers') }}</div>
				</button>

				<!-- Payments -->
				<button @click="handleMenuClick('payments')" :class="getMenuClass('payments')" :title="__('Payments')">
					<FeatherIcon name="dollar-sign" class="w-5 h-5" />
					<div class="tooltip">{{ __('Payments') }}</div>
				</button>

				<!-- Reports -->
				<button @click="handleMenuClick('reports')" :class="getMenuClass('reports')" :title="__('Reports')">
					<FeatherIcon name="bar-chart-2" class="w-5 h-5" />
					<div class="tooltip">{{ __('Reports') }}</div>
				</button>

				<!-- Invoices -->
				<button @click="handleMenuClick('invoices')" :class="getMenuClass('invoices')" :title="__('Invoice Management')">
					<FeatherIcon name="file-text" class="w-5 h-5" />
					<div class="tooltip">{{ __('Invoice Management') }}</div>
				</button>

				<!-- Sales Orders -->
				<button v-if="settingsStore.allowSalesOrder" @click="handleMenuClick('sales_orders')" :class="getMenuClass('sales_orders')" :title="__('Sales Orders')">
					<FeatherIcon name="shopping-bag" class="w-5 h-5" />
					<div class="tooltip">{{ __('Sales Orders') }}</div>
				</button>

				<!-- Stock Transfer -->
				<button v-if="settingsStore.enableStockTransfer" @click="handleMenuClick('stock_transfer')" :class="getMenuClass('stock_transfer')" :title="__('Stock Transfer')">
					<FeatherIcon name="refresh-cw" class="w-5 h-5" />
					<div class="tooltip">{{ __('Stock Transfer') }}</div>
				</button>

				<!-- Delivery Notes -->
				<button v-if="settingsStore.enableDeliveryNote" @click="handleMenuClick('delivery_notes')" :class="getMenuClass('delivery_notes')" :title="__('Delivery Notes')">
					<FeatherIcon name="truck" class="w-5 h-5" />
					<div class="tooltip">{{ __('Delivery Notes') }}</div>
				</button>

				<!-- Divider -->
				<div class="w-8 border-t border-gray-200 my-2"></div>

				<!-- Settings -->
				<button @click="handleMenuClick('settings')" :class="getMenuClass('settings', 'gray')" :title="__('Settings')">
					<FeatherIcon name="settings" class="w-5 h-5" />
					<div class="tooltip">{{ __('Settings') }}</div>
				</button>
			</div>

			<!-- Mobile View (Default, hidden on xl) -->
			<div class="flex xl:hidden w-full items-center justify-around relative">
				<!-- Dashboard -->
				<button @click="handleMenuClick('dashboard')" :class="getMenuClass('dashboard')" class="mobile-nav-item">
					<FeatherIcon name="layout" class="w-5 h-5" />
				</button>

				<!-- Customers -->
				<button @click="handleMenuClick('customers')" :class="getMenuClass('customers')" class="mobile-nav-item">
					<FeatherIcon name="users" class="w-5 h-5" />
				</button>

				<!-- CENTRAL PLUS BUTTON -->
				<div class="relative -mt-8">
					<button
						@click="togglePlusMenu"
						class="w-14 h-14 bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-full flex items-center justify-center shadow-lg border-4 border-white active:scale-95 transition-all z-[120]"
						:class="{ 'rotate-45': showPlusMenu }"
					>
						<FeatherIcon name="plus" class="w-7 h-7" stroke-width="3" />
					</button>

					<!-- Plus Menu Popover -->
					<Transition name="slide-up">
						<div v-if="showPlusMenu" class="absolute bottom-20 left-1/2 -translate-x-1/2 w-64 bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden z-[130]">
							<div class="p-2 grid grid-cols-1 gap-1">
								<!-- Invoices -->
								<button @click="handleMenuClick('invoices')" class="plus-menu-item">
									<div class="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
										<FeatherIcon name="file-text" class="w-5 h-5" />
									</div>
									<span class="font-medium text-gray-700">{{ __('Sales Invoices') }}</span>
								</button>

								<!-- Sales Orders -->
								<button v-if="settingsStore.allowSalesOrder" @click="handleMenuClick('sales_orders')" class="plus-menu-item">
									<div class="w-10 h-10 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center">
										<FeatherIcon name="shopping-bag" class="w-5 h-5" />
									</div>
									<span class="font-medium text-gray-700">{{ __('Sales Orders') }}</span>
								</button>

								<!-- Stock Transfer -->
				<button v-if="settingsStore.enableStockTransfer" @click="handleMenuClick('stock_transfer')" :class="getMenuClass('stock_transfer')" :title="__('Stock Transfer')">
					<FeatherIcon name="refresh-cw" class="w-5 h-5" />
					<div class="tooltip">{{ __('Stock Transfer') }}</div>
				</button>

				<!-- Delivery Notes -->
								<button v-if="settingsStore.enableDeliveryNote" @click="handleMenuClick('delivery_notes')" class="plus-menu-item">
									<div class="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
										<FeatherIcon name="truck" class="w-5 h-5" />
									</div>
									<span class="font-medium text-gray-700">{{ __('Delivery Notes') }}</span>
								</button>

								<!-- Payments -->
								<button @click="handleMenuClick('payments')" class="plus-menu-item">
									<div class="w-10 h-10 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center">
										<FeatherIcon name="dollar-sign" class="w-5 h-5" />
									</div>
									<span class="font-medium text-gray-700">{{ __('Payments') }}</span>
								</button>

								<div class="border-t border-gray-100 my-1"></div>

								<!-- Products -->
								<button @click="handleMenuClick('products')" class="plus-menu-item">
									<div class="w-10 h-10 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center">
										<FeatherIcon name="package" class="w-5 h-5" />
									</div>
									<span class="font-medium text-gray-700">{{ __('Stock Lookup') }}</span>
								</button>

								<!-- Promotions -->
								<button v-if="settingsStore.allowPromotion" @click="handleMenuClick('promotions')" class="plus-menu-item">
									<div class="w-10 h-10 rounded-lg bg-green-50 text-green-600 flex items-center justify-center">
										<FeatherIcon name="tag" class="w-5 h-5" />
									</div>
									<span class="font-medium text-gray-700">{{ __('Promotions') }}</span>
								</button>
							</div>
						</div>
					</Transition>
				</div>

				<!-- Reports -->
				<button @click="handleMenuClick('reports')" :class="getMenuClass('reports')" class="mobile-nav-item">
					<FeatherIcon name="bar-chart-2" class="w-5 h-5" />
				</button>

				<!-- Settings -->
				<button @click="handleMenuClick('settings')" :class="getMenuClass('settings', 'gray')" class="mobile-nav-item">
					<FeatherIcon name="settings" class="w-5 h-5" />
				</button>
			</div>
		</template>
	</div>

	<!-- Backdrop for mobile plus menu -->
	<Transition name="fade">
		<div v-if="showPlusMenu" @click="showPlusMenu = false" class="fixed inset-0 bg-black/20 backdrop-blur-[2px] z-[105] xl:hidden"></div>
	</Transition>
</template>

<script setup>
import { FeatherIcon } from "frappe-ui"
import { ref, watch } from "vue"
import { usePOSSettingsStore } from "@/stores/posSettings"

const props = defineProps({
	activeTab: {
		type: String,
		default: ""
	}
})

const emit = defineEmits(["menu-clicked"])
const settingsStore = usePOSSettingsStore()

const activeMenu = ref(props.activeTab)
const showPlusMenu = ref(false)

watch(() => props.activeTab, (val) => {
	activeMenu.value = val
})

function handleMenuClick(menuItem) {
	activeMenu.value = menuItem
	showPlusMenu.value = false
	emit("menu-clicked", menuItem)
}

function togglePlusMenu() {
	showPlusMenu.value = !showPlusMenu.value
}

function getMenuClass(menuName, defaultColor = 'blue') {
	const isActive = activeMenu.value === menuName
	const colorMap = {
		dashboard: isActive ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100',
		promotions: isActive ? 'bg-green-100 text-green-600' : 'text-gray-600 hover:bg-gray-100',
		products: isActive ? 'bg-purple-100 text-purple-600' : 'text-gray-600 hover:bg-gray-100',
		customers: isActive ? 'bg-emerald-100 text-emerald-600' : 'text-gray-600 hover:bg-gray-100',
		payments: isActive ? 'bg-rose-100 text-rose-600' : 'text-gray-600 hover:bg-gray-100',
		reports: isActive ? 'bg-orange-100 text-orange-600' : 'text-gray-600 hover:bg-gray-100',
		invoices: isActive ? 'bg-indigo-100 text-indigo-600' : 'text-gray-600 hover:bg-gray-100',
		sales_orders: isActive ? 'bg-teal-100 text-teal-600' : 'text-gray-600 hover:bg-gray-100',
		stock_transfer: isActive ? 'bg-orange-100 text-orange-600' : 'text-gray-600 hover:bg-gray-100',
		delivery_notes: isActive ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100',
		settings: isActive ? 'bg-gray-100 text-gray-900' : 'text-gray-600 hover:bg-gray-100'
	}

	const baseClasses = 'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group'
	return `${baseClasses} ${colorMap[menuName] || colorMap[defaultColor]}`
}
</script>

<style scoped>
.tooltip {
	@apply absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50;
}

.mobile-nav-item {
	@apply w-12 h-12 rounded-lg flex items-center justify-center transition-all;
}

.plus-menu-item {
	@apply flex items-center gap-3 p-2.5 rounded-xl hover:bg-gray-50 active:bg-gray-100 transition-colors w-full text-left;
}

/* Animations */
.fade-enter-active,
.fade-leave-active {
	transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
	opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
	transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
	transform: translate(-50%, 20px) scale(0.95);
	opacity: 0;
}
</style>
