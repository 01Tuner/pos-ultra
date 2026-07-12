<template>
	<Dialog v-model="show" :options="{ title: __('Add New Item'), size: 'md' }">
		<template #body-content>
			<div class="flex flex-col gap-5">
				<!-- Permission Warning -->
				<div v-if="!hasPermission && !checkingPermission" class="px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg">
					<div class="flex items-start gap-2">
						<svg class="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
							<path
								fill-rule="evenodd"
								d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
								clip-rule="evenodd"
							/>
						</svg>
						<div class="flex-1">
							<p class="text-sm font-medium text-amber-900">{{ __("Permission Required") }}</p>
							<p class="text-xs text-amber-700 mt-0.5">
								{{ __("You don't have permission to create Items. Contact your administrator.") }}
							</p>
						</div>
					</div>
				</div>

				<!-- Item Name -->
				<div>
					<label class="block text-start text-sm font-medium text-gray-700 mb-2">
						{{ __("Item Name") }} <span class="text-red-500">*</span>
					</label>
					<Input
						v-model="itemData.item_name"
						type="text"
						:placeholder="__('Enter item name')"
						required
					/>
				</div>

				<!-- Item Code (optional - auto-generated if empty) -->
				<div>
					<label class="block text-start text-sm font-medium text-gray-700 mb-2">
						{{ __("Item Code") }}
						<span class="text-xs text-gray-400 font-normal ms-1">{{ __("(auto-generated if empty)") }}</span>
					</label>
					<Input
						v-model="itemData.item_code"
						type="text"
						:placeholder="__('Leave blank to auto-generate')"
					/>
				</div>

				<!-- Item Group + UOM row -->
				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="block text-start text-sm font-medium text-gray-700 mb-2">
							{{ __("Item Group") }} <span class="text-red-500">*</span>
						</label>
						<select
							v-model="itemData.item_group"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
						>
							<option value="">{{ __("Select Item Group") }}</option>
							<option v-for="group in itemGroups" :key="group" :value="group">
								{{ group }}
							</option>
						</select>
					</div>
					<div>
						<label class="block text-start text-sm font-medium text-gray-700 mb-2">
							{{ __("UOM") }} <span class="text-red-500">*</span>
						</label>
						<select
							v-model="itemData.stock_uom"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
						>
							<option v-for="uom in uomList" :key="uom" :value="uom">
								{{ uom }}
							</option>
						</select>
					</div>
				</div>

				<!-- Standard Selling Rate -->
				<div>
					<label class="block text-start text-sm font-medium text-gray-700 mb-2">
						{{ __("Standard Selling Rate") }}
					</label>
					<Input
						v-model="itemData.standard_rate"
						type="number"
						:placeholder="__('0.00')"
						min="0"
						step="0.01"
					/>
					<p class="text-xs text-gray-400 mt-1">
						{{ __("Will be added to the current POS price list") }}
					</p>
				</div>

				<!-- Is Stock Item -->
				<div class="flex items-center gap-3">
					<input
						id="is-stock-item"
						v-model="itemData.is_stock_item"
						type="checkbox"
						class="h-4 w-4 text-blue-600 border-gray-300 rounded"
					/>
					<label for="is-stock-item" class="text-sm font-medium text-gray-700 cursor-pointer">
						{{ __("Is Stock Item") }}
					</label>
				</div>
			</div>
		</template>

		<template #actions>
			<div class="flex gap-2">
				<Button
					variant="solid"
					@click="handleCreate"
					:loading="creating || checkingPermission"
					:disabled="!itemData.item_name || !itemData.item_group || !itemData.stock_uom || !hasPermission"
				>
					{{ __("Create Item") }}
				</Button>
				<Button variant="subtle" @click="show = false">
					{{ __("Cancel") }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
/**
 * CreateItemDialog - Quick item creation from POS
 *
 * Features:
 * - Permission checking before allowing creation
 * - Creates an Item Price record if standard selling rate is provided
 * - Injects newly created item into the POS item list
 */

import { usePOSPermissions } from "@/composables/usePermissions"
import { useToast } from "@/composables/useToast"
import { logger } from "@/utils/logger"
import { Button, Dialog, Input, createResource } from "frappe-ui"
import { computed, onMounted, ref, watch } from "vue"

const log = logger.create("CreateItemDialog")

// =============================================================================
// Composables
// =============================================================================

const { canCreateItem } = usePOSPermissions()
const { showSuccess, showError } = useToast()

// =============================================================================
// Props & Emits
// =============================================================================

const props = defineProps({
	modelValue: Boolean,
	posProfile: String,
	priceList: String, // POS Profile's price list
	currency: { type: String, default: "SAR" },
})

const emit = defineEmits(["update:modelValue", "item-created"])

// =============================================================================
// State
// =============================================================================

const hasPermission = ref(true)
const checkingPermission = ref(false)
const creating = ref(false)

const itemGroups = ref([])
const uomList = ref(["Nos", "Kg", "Litre", "Meter", "Box", "Pcs", "Bag", "Unit"])

const itemData = ref({
	item_name: "",
	item_code: "",
	item_group: "",
	stock_uom: "Nos",
	standard_rate: "",
	is_stock_item: 1,
})

// =============================================================================
// Computed
// =============================================================================

const show = computed({
	get: () => props.modelValue,
	set: (val) => emit("update:modelValue", val),
})

// =============================================================================
// API Resources
// =============================================================================

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
			itemGroups.value = data.map((d) => d.name)
			// Pre-select "All Item Groups" or the first group
			if (!itemData.value.item_group) {
				itemData.value.item_group = itemGroups.value[0] || ""
			}
		}
	},
	onError: (err) => log.error("Error loading item groups", err),
})

// =============================================================================
// Methods
// =============================================================================

const checkPermissions = async () => {
	checkingPermission.value = true
	try {
		hasPermission.value = await canCreateItem()
	} catch (err) {
		log.error("Permission check failed", err)
		hasPermission.value = false
	} finally {
		checkingPermission.value = false
	}
}

const handleCreate = async () => {
	if (!itemData.value.item_name) return showError(__("Item Name is required"))
	if (!itemData.value.item_group) return showError(__("Item Group is required"))
	if (!itemData.value.stock_uom) return showError(__("UOM is required"))

	creating.value = true

	try {
		// Build item doc
		const itemDoc = {
			doctype: "Item",
			item_name: itemData.value.item_name,
			item_code: itemData.value.item_code || itemData.value.item_name,
			item_group: itemData.value.item_group,
			stock_uom: itemData.value.stock_uom,
			is_stock_item: itemData.value.is_stock_item ? 1 : 0,
		}

		const insertResource = createResource({
			url: "frappe.client.insert",
			params: { doc: itemDoc },
		})

		const newItem = await insertResource.submit()

		// If a selling rate was provided, create an Item Price
		const rate = parseFloat(itemData.value.standard_rate)
		if (rate > 0 && props.priceList) {
			try {
				const priceResource = createResource({
					url: "frappe.client.insert",
					params: {
						doc: {
							doctype: "Item Price",
							item_code: newItem.name,
							price_list: props.priceList,
							currency: props.currency,
							price_list_rate: rate,
						},
					},
				})
				await priceResource.submit()
			} catch (priceErr) {
				log.warn("Item created but failed to set price", priceErr)
			}
		}

		showSuccess(__("Item {0} created successfully", [newItem.item_name]))

		// Emit the created item to the parent so ItemsSelector can inject it
		emit("item-created", {
			...newItem,
			item_code: newItem.name,
			item_name: newItem.item_name,
			item_group: newItem.item_group,
			stock_uom: newItem.stock_uom,
			uom: newItem.stock_uom,
			rate: rate > 0 ? rate : 0,
			price_list_rate: rate > 0 ? rate : 0,
			is_stock_item: newItem.is_stock_item,
			actual_qty: 0,
			stock_qty: 0,
			image: null,
		})

		show.value = false
	} catch (err) {
		log.error("Error creating item", err)
		showError(err.message || __("Failed to create item"))
	} finally {
		creating.value = false
	}
}

const resetForm = () => {
	Object.assign(itemData.value, {
		item_name: "",
		item_code: "",
		item_group: itemGroups.value[0] || "",
		stock_uom: "Nos",
		standard_rate: "",
		is_stock_item: 1,
	})
}

const loadDialogData = async () => {
	await checkPermissions()
	if (!itemGroups.value.length) {
		await itemGroupsResource.reload()
	}
}

// =============================================================================
// Watchers
// =============================================================================

watch(
	() => props.modelValue,
	async (isOpen) => {
		if (isOpen) {
			await loadDialogData()
		} else {
			resetForm()
		}
	}
)

watch(show, (val) => emit("update:modelValue", val))

// =============================================================================
// Lifecycle
// =============================================================================

onMounted(() => {
	if (props.modelValue) {
		loadDialogData()
	}
})
</script>
