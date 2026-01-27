<template>
	<!-- Icon-Only Management Bar - Sidebar on Desktop, Fixed Footer on Mobile -->
	<div
		class="fixed bottom-0 left-0 right-0 z-[110] h-16 bg-white border-t border-gray-200 flex flex-row items-center justify-around xl:justify-start px-2 xl:static xl:h-full xl:w-16 xl:flex-shrink-0 xl:border-t-0 xl:border-e xl:flex-col xl:py-4 xl:gap-2 xl:shadow-none shadow-[0_-2px_10px_rgba(0,0,0,0.05)]">
		<!-- Dashboard (Hidden for now)
		<button
			@click="handleMenuClick('dashboard')"
			:class="[
				'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
				activeMenu === 'dashboard'
					? 'bg-blue-100 text-blue-600'
					: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
			]"
			:title="__('Dashboard')"
		>
			<FeatherIcon name="layout" class="w-5 h-5" />
			<div class="absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('Dashboard') }}
			</div>
		</button>
		-->

		<!-- Promotions -->
		<button @click="handleMenuClick('promotions')" :class="[
			'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
			activeMenu === 'promotions'
				? 'bg-green-100 text-green-600'
				: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
		]" :title="__('Promotions')">
			<FeatherIcon name="tag" class="w-5 h-5" />
			<div
				class="invisible xl:visible absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('Promotions') }}
			</div>
		</button>

		<!-- Products -->
		<button @click="handleMenuClick('products')" :class="[
			'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
			activeMenu === 'products'
				? 'bg-purple-100 text-purple-600'
				: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
		]" :title="__('Products')">
			<FeatherIcon name="package" class="w-5 h-5" />
			<div
				class="invisible xl:visible absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('Products') }}
			</div>
		</button>

		<!-- Reports -->
		<button @click="handleMenuClick('reports')" :class="[
			'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
			activeMenu === 'reports'
				? 'bg-orange-100 text-orange-600'
				: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
		]" :title="__('Reports')">
			<FeatherIcon name="bar-chart-2" class="w-5 h-5" />
			<div
				class="invisible xl:visible absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('Reports') }}
			</div>
		</button>

		<!-- Invoices -->
		<button @click="handleMenuClick('invoices')" :class="[
			'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
			activeMenu === 'invoices'
				? 'bg-indigo-100 text-indigo-600'
				: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
		]" :title="__('Invoice Management')">
			<FeatherIcon name="file-text" class="w-5 h-5" />
			<div
				class="invisible xl:visible absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('Invoice Management') }}
			</div>
		</button>

		<!-- Divider -->
		<div class="hidden xl:block w-8 border-t border-gray-200 my-2"></div>

		<!-- Settings -->
		<button @click="handleMenuClick('settings')" :class="[
			'w-12 h-12 rounded-lg flex items-center justify-center transition-all relative group',
			activeMenu === 'settings'
				? 'bg-gray-100 text-gray-900'
				: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
		]" :title="__('Settings')">
			<FeatherIcon name="settings" class="w-5 h-5" />
			<div
				class="invisible xl:visible absolute start-full ms-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{{ __('Settings') }}
			</div>
		</button>
	</div>
</template>

<script setup>
import { FeatherIcon } from "frappe-ui"
import { ref } from "vue"

const emit = defineEmits(["menu-clicked"])

const activeMenu = ref("")

function handleMenuClick(menuItem) {
	activeMenu.value = menuItem
	emit("menu-clicked", menuItem)
}
</script>
