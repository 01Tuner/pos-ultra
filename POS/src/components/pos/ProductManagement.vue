<template>
	<!-- Full Page Overlay -->
	<Transition name="fade">
		<div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 z-[300]" @click.self="handleClose">
			<!-- Main Container -->
			<div class="fixed inset-0 flex items-center justify-center sm:p-4 z-50">
				<div class="w-full h-full sm:max-w-[95vw] sm:max-h-[95vh] bg-white sm:rounded-lg shadow-2xl overflow-hidden flex flex-col pt-safe pb-safe">
					<!-- Header -->
					<div class="flex items-center justify-between px-6 py-5 border-b bg-gradient-to-r from-purple-50 to-indigo-50">
						<div class="flex items-center gap-3">
							<div class="p-2 bg-purple-100 rounded-lg">
								<svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
								</svg>
							</div>
							<div>
								<h2 class="text-xl font-bold text-gray-900">{{ __('Item Management') }}</h2>
								<p class="text-sm text-gray-600 mt-0.5">{{ __('Manage items, prices and availability') }}</p>
							</div>
						</div>
						<div class="flex items-center gap-2">
							<!-- Create Product Button -->
							<Button v-if="settingsStore.allowAddItem" @click="openCreateProduct" variant="solid" theme="blue" size="sm">
								<template #prefix>
									<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
									</svg>
								</template>
								{{ __('New Item') }}
							</Button>
							<Button @click="loadProducts" :loading="loading" variant="ghost" size="sm">
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
						<!-- Search & Filter Bar -->
						<div class="p-4 border-b bg-white flex flex-wrap gap-3">
							<div class="relative flex-1 min-w-48">
								<div class="absolute inset-y-0 start-0 pl-3 flex items-center pointer-events-none">
									<svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
									</svg>
								</div>
								<input
									type="text"
									v-model="searchQuery"
									@input="debouncedSearch"
									:placeholder="__('Search by name or item code...')"
									class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-sm bg-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out"
								/>
							</div>
							<!-- Status Filter -->
							<select
								v-model="statusFilter"
								@change="loadProducts"
								class="px-3 py-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
							>
								<option value="">{{ __('All Items') }}</option>
								<option value="enabled">{{ __('Enabled') }}</option>
								<option value="disabled">{{ __('Disabled') }}</option>
							</select>
							<!-- Group Filter -->
							<select
								v-model="groupFilter"
								@change="loadProducts"
								class="px-3 py-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
							>
								<option value="">{{ __('All Groups') }}</option>
								<option v-for="g in itemGroups" :key="g" :value="g">{{ g }}</option>
							</select>
						</div>

						<!-- Loading State -->
						<div v-if="loading && products.length === 0" class="flex flex-col items-center justify-center py-16 flex-1">
							<div class="animate-spin rounded-full h-12 w-12 border-b-3 border-purple-500 mb-4"></div>
							<p class="text-sm font-medium text-gray-600">{{ __('Loading Items...') }}</p>
						</div>

						<!-- Empty State -->
						<div v-else-if="products.length === 0" class="flex flex-col items-center justify-center py-16 text-center flex-1">
							<svg class="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
							</svg>
							<p class="text-gray-600 font-medium">{{ __('No Items Found') }}</p>
							<p class="text-gray-500 text-sm mt-1">{{ settingsStore.allowAddItem ? __('Try adjusting your search filters or create a new item') : __('Try adjusting your search filters') }}</p>
							<Button v-if="settingsStore.allowAddItem" @click="openCreateProduct" variant="solid" theme="blue" size="sm" class="mt-4">
								<template #prefix>
									<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
									</svg>
								</template>
								{{ __('Create Item') }}
							</Button>
						</div>

						<!-- Products Table/Cards -->
						<div v-else class="flex-1 overflow-y-auto px-0 sm:px-4 py-2 sm:py-4">
							<div class="bg-transparent sm:bg-white sm:shadow sm:rounded-lg sm:border sm:border-gray-200 overflow-hidden">

								<!-- Mobile Card View -->
								<div class="block sm:hidden space-y-3 px-3">
									<div
										v-for="product in products"
										:key="'mob-' + product.name"
										:class="['bg-white border rounded-xl shadow-sm p-4 hover:shadow-md transition-shadow', product.disabled ? 'border-red-200 opacity-75' : 'border-gray-200']"
									>
										<div class="flex items-start gap-3 mb-3">
											<!-- Product Image -->
											<div class="h-12 w-12 shrink-0 rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center">
												<img v-if="product.image" :src="product.image" :alt="product.item_name" class="w-full h-full object-cover" />
												<svg v-else class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
												</svg>
											</div>
											<div class="flex-1 min-w-0">
												<div class="flex items-center gap-2">
													<h3 class="text-sm font-bold text-gray-900 truncate">{{ product.item_name }}</h3>
													<span v-if="product.disabled" class="px-1.5 py-0.5 bg-red-100 text-red-700 text-xs rounded-full shrink-0">{{ __('Disabled') }}</span>
													<span v-else class="px-1.5 py-0.5 bg-green-100 text-green-700 text-xs rounded-full shrink-0">{{ __('Active') }}</span>
												</div>
												<p class="text-xs text-gray-500 truncate">{{ product.name }}</p>
												<p class="text-xs text-gray-400">{{ product.item_group }}</p>
											</div>
										</div>

										<!-- Price Edit (Mobile) -->
										<div class="flex items-center gap-2 mb-3">
											<span class="text-xs text-gray-500">{{ __('Price') }}:</span>
											<div v-if="settingsStore.allowAddItem && editingPriceId === product.name" class="flex items-center gap-1 flex-1">
												<input
													:ref="el => { if (el) priceInputRefs[product.name] = el }"
													v-model="editingPriceValue"
													type="number"
													min="0"
													step="0.01"
													class="w-28 px-2 py-1 text-sm border border-blue-400 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
													@keydown.enter="savePriceEdit(product)"
													@keydown.escape="cancelPriceEdit"
												/>
												<button @click="savePriceEdit(product)" class="p-1 text-green-600 hover:bg-green-50 rounded">
													<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
												</button>
												<button @click="cancelPriceEdit" class="p-1 text-gray-500 hover:bg-gray-100 rounded">
													<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
												</button>
											</div>
											<button v-else-if="settingsStore.allowAddItem" @click="startPriceEdit(product)" class="font-semibold text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1">
												{{ formatCurrency(product.price) }}
												<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
											</button>
											<span v-else class="font-semibold text-gray-800 text-sm">
												{{ formatCurrency(product.price) }}
											</span>
										</div>

										<!-- Actions (Mobile) -->
										<div v-if="settingsStore.allowAddItem" class="flex items-center gap-2 pt-3 border-t border-gray-100">
											<button
												@click="openEditProduct(product)"
												class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg text-sm font-medium transition-colors"
											>
												<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
												{{ __('Edit') }}
											</button>
											<button
												@click="toggleProductStatus(product)"
												:class="['flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors', product.disabled ? 'bg-green-50 hover:bg-green-100 text-green-700' : 'bg-red-50 hover:bg-red-100 text-red-700']"
											>
												<svg v-if="product.disabled" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
												<svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
												{{ product.disabled ? __('Enable') : __('Disable') }}
											</button>
										</div>
									</div>
								</div>

								<!-- Desktop Table View -->
								<table class="hidden sm:table min-w-full divide-y divide-gray-200 w-full">
									<thead class="bg-gray-50">
										<tr>
											<th scope="col" class="w-2/5 px-4 py-3 text-start text-xs font-medium text-gray-500 uppercase tracking-wider">
												{{ __('Item') }}
											</th>
											<th scope="col" class="px-4 py-3 text-start text-xs font-medium text-gray-500 uppercase tracking-wider">
												{{ __('Group') }}
											</th>
											<th scope="col" class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
												{{ __('Type') }}
											</th>
											<th scope="col" class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
												{{ __('Price') }}
											</th>
											<th scope="col" class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
												{{ __('Status') }}
											</th>
											<th v-if="settingsStore.allowAddItem" scope="col" class="w-40 px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
												{{ __('Actions') }}
											</th>
										</tr>
									</thead>
									<tbody class="bg-white divide-y divide-gray-200">
										<tr
											v-for="product in products"
											:key="'desk-' + product.name"
											:class="['hover:bg-gray-50 transition-colors', product.disabled ? 'bg-red-50/30' : '']"
										>
											<!-- Product info -->
											<td class="px-4 py-3">
												<div class="flex items-center gap-3">
													<div class="h-10 w-10 flex-shrink-0 rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center">
														<img v-if="product.image" :src="product.image" :alt="product.item_name" class="w-full h-full object-cover" />
														<svg v-else class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
															<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
														</svg>
													</div>
													<div class="min-w-0">
														<div class="text-sm font-semibold text-gray-900 truncate">{{ product.item_name }}</div>
														<div class="text-xs text-gray-500 truncate">{{ product.name }}</div>
													</div>
												</div>
											</td>
											<!-- Group -->
											<td class="px-4 py-3">
												<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
													{{ product.item_group || '—' }}
												</span>
											</td>
											<!-- Type -->
											<td class="px-4 py-3 text-center">
												<span :class="['inline-flex items-center px-2 py-1 rounded-full text-xs font-medium', product.is_stock_item ? 'bg-blue-50 text-blue-700' : 'bg-amber-50 text-amber-700']">
													{{ product.is_stock_item ? __('Stock') : __('Non-Stock') }}
												</span>
											</td>
											<!-- Price (editable inline) -->
											<td class="px-4 py-3 text-center">
												<div v-if="settingsStore.allowAddItem && editingPriceId === product.name" class="flex items-center justify-center gap-1">
													<input
														:ref="el => { if (el) priceInputRefs[product.name] = el }"
														v-model="editingPriceValue"
														type="number"
														min="0"
														step="0.01"
														class="w-28 px-2 py-1 text-sm text-center border border-blue-400 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
														@keydown.enter="savePriceEdit(product)"
														@keydown.escape="cancelPriceEdit"
													/>
													<button @click="savePriceEdit(product)" class="p-1 text-green-600 hover:bg-green-50 rounded" :title="__('Save')">
														<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
													</button>
													<button @click="cancelPriceEdit" class="p-1 text-gray-500 hover:bg-gray-100 rounded" :title="__('Cancel')">
														<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
													</button>
												</div>
												<button
													v-else-if="settingsStore.allowAddItem"
													@click="startPriceEdit(product)"
													class="group inline-flex items-center gap-1.5 px-3 py-1 rounded-lg hover:bg-blue-50 transition-colors text-sm font-semibold text-gray-800"
													:title="__('Click to edit price')"
												>
													{{ formatCurrency(product.price) }}
													<svg class="w-3.5 h-3.5 text-gray-400 group-hover:text-blue-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
													</svg>
												</button>
											</td>
											<!-- Status badge -->
											<td class="px-4 py-3 text-center">
												<span
													:class="['inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold', product.disabled ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700']"
												>
													<span :class="['w-1.5 h-1.5 rounded-full', product.disabled ? 'bg-red-500' : 'bg-green-500']"></span>
													{{ product.disabled ? __('Disabled') : __('Active') }}
												</span>
											</td>
											<!-- Actions -->
											<td class="px-4 py-3 text-right">
												<div class="flex items-center justify-end gap-1.5">
													<button
														@click="openEditProduct(product)"
														class="p-2 rounded-lg text-blue-600 hover:bg-blue-50 transition-colors"
														:title="__('Edit Product')"
													>
														<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
													</button>
													<button
														@click="toggleProductStatus(product)"
														:class="['p-2 rounded-lg transition-colors', product.disabled ? 'text-green-600 hover:bg-green-50' : 'text-orange-500 hover:bg-orange-50']"
														:title="product.disabled ? __('Enable Product') : __('Disable Product')"
													>
														<svg v-if="product.disabled" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
														<svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/></svg>
													</button>
												</div>
											</td>
										</tr>
									</tbody>
								</table>
							</div>

							<!-- Load More / Pagination -->
							<div v-if="hasMore" class="flex justify-center mt-4">
								<Button @click="loadMore" :loading="loadingMore" variant="ghost" size="sm">
									{{ __('Load More') }}
								</Button>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</Transition>

	<!-- Edit Product Dialog (edit existing only) -->
	<Dialog v-model="showEditDialog" :options="{ title: __('Edit Product'), size: 'md' }">
		<template #body-content>
			<div v-if="editingProduct" class="flex flex-col gap-5">
				<!-- Item Name -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1.5">{{ __('Product Name') }} <span class="text-red-500">*</span></label>
					<Input v-model="editingProduct.item_name" type="text" :placeholder="__('Enter product name')" />
				</div>
				<!-- Item Code (readonly) -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1.5">{{ __('Item Code') }}</label>
					<Input v-model="editingProduct.name" type="text" :disabled="true" />
				</div>
				<!-- Item Group (select) -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1.5">{{ __('Item Group') }}</label>
					<select
						v-model="editingProduct.item_group"
						class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					>
						<option value="">{{ __('Select Item Group') }}</option>
						<option v-for="group in allItemGroups" :key="group" :value="group">{{ group }}</option>
					</select>
				</div>
				<!-- Price -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1.5">{{ __('Price') }}</label>
					<Input v-model="editingProduct.price" type="number" :placeholder="__('0.00')" min="0" step="0.01" />
				</div>
				<!-- Description -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1.5">{{ __('Description') }}</label>
					<textarea
						v-model="editingProduct.description"
						:placeholder="__('Optional product description')"
						rows="3"
						class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 resize-none"
					></textarea>
				</div>
				<!-- Disabled toggle -->
				<div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
					<div>
						<p class="text-sm font-medium text-gray-700">{{ __('Status') }}</p>
						<p class="text-xs text-gray-500">{{ editingProduct.disabled ? __('Product is disabled and hidden from POS') : __('Product is active and visible in POS') }}</p>
					</div>
					<button
						@click="editingProduct.disabled = !editingProduct.disabled"
						:class="['relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none', editingProduct.disabled ? 'bg-red-500' : 'bg-green-500']"
					>
						<span :class="['pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out', editingProduct.disabled ? 'translate-x-0' : 'translate-x-5']"></span>
					</button>
				</div>
			</div>
		</template>
		<template #actions>
			<div class="flex gap-2 justify-end">
				<Button @click="showEditDialog = false" variant="ghost">{{ __('Cancel') }}</Button>
				<Button @click="saveProduct" :loading="saving" variant="solid" theme="blue">
					{{ __('Save Changes') }}
				</Button>
			</div>
		</template>
	</Dialog>

	<!-- Create Item Dialog (reuses the existing one) -->
	<CreateItemDialog
		v-model="showCreateItemDialog"
		:pos-profile="posProfile"
		:price-list="priceList"
		:currency="currency"
		@item-created="handleItemCreated"
	/>
</template>

<script setup>
import { ref, watch, nextTick } from "vue";
import { Button, Dialog, Input, createResource } from "frappe-ui";
import { useToast } from "@/composables/useToast";
import { call } from "@/utils/apiWrapper";
import CreateItemDialog from "@/components/sale/CreateItemDialog.vue";
import { usePOSSettingsStore } from "@/stores/posSettings";

const settingsStore = usePOSSettingsStore();

const props = defineProps({
	modelValue: Boolean,
	posProfile: String,
	priceList: String,
	currency: String,
});

const emit = defineEmits(["update:modelValue"]);

const { showSuccess, showError } = useToast();

const show = ref(props.modelValue);
const products = ref([]);
const loading = ref(false);
const loadingMore = ref(false);
const saving = ref(false);
const searchQuery = ref("");
const statusFilter = ref("");
const groupFilter = ref("");
const itemGroups = ref([]);
const allItemGroups = ref([]); // For edit dialog select
const pageLimit = 50;
const currentOffset = ref(0);
const hasMore = ref(false);
let searchTimeout = null;

// Price editing state
const editingPriceId = ref(null);
const editingPriceValue = ref("");
const priceInputRefs = ref({});

// Product edit dialog
const showEditDialog = ref(false);
const editingProduct = ref(null);

// Create item dialog (uses existing CreateItemDialog)
const showCreateItemDialog = ref(false);

// Load all item groups for edit dialog select
const itemGroupsResource = createResource({
	url: "frappe.client.get_list",
	makeParams: () => ({
		doctype: "Item Group",
		fields: ["name"],
		filters: { is_group: 0 },
		limit_page_length: 500,
		order_by: "name asc",
	}),
	auto: false,
	onSuccess: (data) => {
		if (data?.length) {
			allItemGroups.value = data.map((d) => d.name);
		}
	},
});

// Watchers
watch(
	() => props.modelValue,
	(val) => {
		show.value = val;
		if (val) {
			loadProducts();
			if (!allItemGroups.value.length) itemGroupsResource.reload();
		}
	}
);

watch(show, (val) => {
	emit("update:modelValue", val);
});

// Methods
function handleClose() {
	cancelPriceEdit();
	show.value = false;
}

function formatCurrency(amount) {
	if (amount === null || amount === undefined) return "—";
	const curr = props.currency || "USD";
	try {
		return new Intl.NumberFormat(undefined, { style: "currency", currency: curr }).format(Number(amount) || 0);
	} catch {
		return `${curr} ${Number(amount || 0).toFixed(2)}`;
	}
}

function debouncedSearch() {
	if (searchTimeout) clearTimeout(searchTimeout);
	searchTimeout = setTimeout(() => {
		loadProducts();
	}, 400);
}

async function loadProducts(reset = true) {
	if (!props.posProfile) return;
	if (reset) {
		loading.value = true;
		currentOffset.value = 0;
		products.value = [];
	} else {
		loadingMore.value = true;
	}

	try {
		const result = await call("pos_next.api.product_management.get_pos_products", {
			pos_profile: props.posProfile,
			search_term: searchQuery.value || "",
			status_filter: statusFilter.value || "",
			group_filter: groupFilter.value || "",
			limit: pageLimit,
			offset: currentOffset.value,
		});

		const items = result?.items || result || [];
		if (reset) {
			products.value = items;
		} else {
			products.value.push(...items);
		}
		hasMore.value = items.length === pageLimit;

		// Collect item groups for filter
		if (reset && items.length > 0) {
			const groups = [...new Set(items.map((i) => i.item_group).filter(Boolean))];
			itemGroups.value = groups;
		}
	} catch (error) {
		showError(error.message || __("Failed to load products"));
	} finally {
		loading.value = false;
		loadingMore.value = false;
	}
}

async function loadMore() {
	currentOffset.value += pageLimit;
	await loadProducts(false);
}

// Price editing
function startPriceEdit(product) {
	cancelPriceEdit();
	editingPriceId.value = product.name;
	editingPriceValue.value = String(product.price || 0);
	nextTick(() => {
		const input = priceInputRefs.value[product.name];
		if (input) {
			input.focus();
			input.select();
		}
	});
}

function cancelPriceEdit() {
	editingPriceId.value = null;
	editingPriceValue.value = "";
}

async function savePriceEdit(product) {
	const newPrice = parseFloat(editingPriceValue.value);
	if (isNaN(newPrice) || newPrice < 0) {
		showError(__("Please enter a valid price"));
		return;
	}

	try {
		await call("pos_next.api.product_management.update_item_price", {
			item_code: product.name,
			price: newPrice,
			pos_profile: props.posProfile,
		});
		product.price = newPrice;
		cancelPriceEdit();
		showSuccess(__("Price updated successfully"));
	} catch (error) {
		showError(error.message || __("Failed to update price"));
	}
}

// Enable / Disable product
async function toggleProductStatus(product) {
	const newDisabled = !product.disabled;
	try {
		await call("pos_next.api.product_management.toggle_item_status", {
			item_code: product.name,
			disabled: newDisabled ? 1 : 0,
		});
		product.disabled = newDisabled;
		showSuccess(newDisabled ? __("Product disabled") : __("Product enabled"));
	} catch (error) {
		showError(error.message || __("Failed to update product status"));
	}
}

// Open create product — delegates to CreateItemDialog
function openCreateProduct() {
	showCreateItemDialog.value = true;
}

// Handle item created from CreateItemDialog
function handleItemCreated(newItem) {
	// Refresh list to show the newly created item
	loadProducts();
}

// Open edit product dialog
function openEditProduct(product) {
	editingProduct.value = { ...product };
	showEditDialog.value = true;
}

// Save product (edit existing only)
async function saveProduct() {
	if (!editingProduct.value) return;
	if (!editingProduct.value.item_name?.trim()) {
		showError(__("Product name is required"));
		return;
	}

	saving.value = true;
	try {
		await call("pos_next.api.product_management.update_item", {
			item_code: editingProduct.value.name,
			item_name: editingProduct.value.item_name,
			item_group: editingProduct.value.item_group,
			price: editingProduct.value.price,
			description: editingProduct.value.description,
			disabled: editingProduct.value.disabled ? 1 : 0,
			pos_profile: props.posProfile,
		});
		// Update in list
		const idx = products.value.findIndex((p) => p.name === editingProduct.value.name);
		if (idx >= 0) {
			products.value[idx] = { ...products.value[idx], ...editingProduct.value };
		}
		showSuccess(__("Product updated successfully"));
		showEditDialog.value = false;
	} catch (error) {
		showError(error.message || __("Failed to save product"));
	} finally {
		saving.value = false;
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
