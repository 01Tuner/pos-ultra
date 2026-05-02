<template>
	<Dialog
		:modelValue="modelValue"
		@update:modelValue="emit('update:modelValue', $event)"
		:options="{
			title: __('Stock Transfer'),
			size: '2xl'
		}"
	>
		<template #body-content>
            <div v-if="successData" class="py-12 flex flex-col items-center justify-center text-center">
                <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                    <FeatherIcon name="check" class="w-8 h-8 text-green-600" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">{{ __('Transfer Successful') }}</h3>
                <p class="text-gray-500 mb-6">{{ __('Stock Entry') }} <span class="font-bold">{{ successData }}</span> {{ __('has been created.') }}</p>
                
                <div class="flex gap-3">
                    <Button @click="printEntry(successData)" variant="subtle">
                        <template #prefix><FeatherIcon name="printer" class="w-4 h-4" /></template>
                        {{ __('Print') }}
                    </Button>
                    <Button @click="resetForm" variant="solid" theme="blue">
                        {{ __('New Transfer') }}
                    </Button>
                </div>
            </div>
			<div v-else class="space-y-4 px-1 py-2">
				<!-- Warehouse Selection -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">{{ __('Source Warehouse') }}</label>
						<select v-model="sourceWarehouse" class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border">
							<option value="">{{ __('Select Source Warehouse') }}</option>
							<option v-for="w in allWarehouses" :key="w.name" :value="w.name">{{ w.name }}</option>
						</select>
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">{{ __('Target Warehouse') }}</label>
						<select v-model="targetWarehouse" class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border">
							<option value="">{{ __('Select Target Warehouse') }}</option>
							<option v-for="w in allWarehouses" :key="w.name" :value="w.name">{{ w.name }}</option>
						</select>
					</div>
				</div>

				<!-- Item Search -->
				<div>
                    <div class="flex justify-between items-center mb-1">
					    <label class="block text-sm font-medium text-gray-700">{{ __('Add Item') }}</label>
                        <button v-if="sourceWarehouse" @click="selectAllAvailable" :disabled="isLoadingAll" class="text-xs text-blue-600 hover:text-blue-800 font-medium disabled:opacity-50 flex items-center gap-1">
                            <svg v-if="isLoadingAll" class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            {{ __('Select All Available Items') }}
                        </button>
                    </div>
					<div class="relative">
						<input 
							type="text" 
							v-model="itemSearchQuery" 
							:placeholder="__('Search by Item Code or Name...')"
							class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 pl-10 p-2 border"
							@input="debouncedSearch"
						/>
						<FeatherIcon name="search" class="w-4 h-4 absolute left-3 top-3 text-gray-400" />
						
						<!-- Dropdown -->
						<div v-if="showSearchDropdown && searchResults.length > 0" class="absolute z-10 mt-1 w-full bg-white shadow-lg rounded-md border border-gray-200 max-h-60 overflow-y-auto">
							<div 
								v-for="item in searchResults" 
								:key="item.item_code"
								@click="addItem(item)"
								class="p-2 hover:bg-gray-50 cursor-pointer border-b last:border-b-0"
							>
								<div class="font-medium text-sm">{{ item.item_name }}</div>
								<div class="text-xs text-gray-500">{{ item.item_code }}</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Selected Items -->
				<div class="border rounded-lg overflow-x-auto">
					<table class="min-w-full divide-y divide-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th scope="col" class="px-2 sm:px-6 py-2 sm:py-3 text-left text-[10px] sm:text-xs font-medium text-gray-500 uppercase tracking-wider">{{ __('Item') }}</th>
								<th scope="col" class="px-2 sm:px-6 py-2 sm:py-3 text-right text-[10px] sm:text-xs font-medium text-gray-500 uppercase tracking-wider">{{ __('Qty') }}</th>
								<th scope="col" class="px-2 sm:px-6 py-2 sm:py-3 text-right text-[10px] sm:text-xs font-medium text-gray-500 uppercase tracking-wider">{{ __('Action') }}</th>
							</tr>
						</thead>
						<tbody class="bg-white divide-y divide-gray-200">
							<tr v-if="selectedItems.length === 0">
								<td colspan="3" class="px-2 sm:px-6 py-4 text-center text-xs sm:text-sm text-gray-500">{{ __('No items added yet.') }}</td>
							</tr>
							<tr v-for="(item, index) in selectedItems" :key="index">
								<td class="px-2 sm:px-6 py-2 sm:py-4">
									<div class="text-xs sm:text-sm font-medium text-gray-900 truncate max-w-[120px] sm:max-w-xs">{{ item.item_name }}</div>
									<div class="text-[10px] sm:text-xs text-gray-500">{{ item.item_code }}</div>
								</td>
								<td class="px-2 sm:px-6 py-2 sm:py-4 text-right">
                                    <div class="flex flex-col sm:flex-row items-end justify-end gap-1 sm:gap-2">
                                        <div v-if="item.max_qty !== undefined" class="text-[9px] sm:text-[10px] text-gray-500 bg-gray-100 px-1 sm:px-1.5 py-0.5 rounded whitespace-nowrap">
                                            Max: {{ item.max_qty }}
                                        </div>
									    <input type="number" v-model.number="item.qty" @input="validateQty(item)" min="1" :max="item.max_qty" class="w-16 sm:w-20 rounded border-gray-300 text-right p-1 text-sm border shadow-sm focus:border-blue-500 focus:ring-blue-500" />
                                    </div>
								</td>
								<td class="px-2 sm:px-6 py-2 sm:py-4 text-right text-sm font-medium">
									<button @click="removeItem(index)" class="text-red-600 hover:text-red-900 p-1">
										<FeatherIcon name="trash-2" class="w-4 h-4 inline" />
									</button>
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>
		</template>
		
		<template #actions>
			<div v-if="!successData" class="flex gap-2 justify-end w-full">
				<Button @click="emit('update:modelValue', false)" variant="subtle">
					{{ __('Cancel') }}
				</Button>
				<Button @click="submitTransfer" variant="solid" theme="blue" :loading="isSubmitting" :disabled="!canSubmit">
					{{ __('Transfer Stock') }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { Dialog, Button, FeatherIcon } from "frappe-ui"
import { ref, computed, watch, onMounted, onUnmounted } from "vue"
import { call } from "frappe-ui"
import { usePOSShiftStore } from "@/stores/posShift"
import { usePOSCartStore } from "@/stores/posCart"
import { usePOSUIStore } from "@/stores/posUI"
import { useToast } from "@/composables/useToast"

const props = defineProps({
	modelValue: Boolean
})

const emit = defineEmits(["update:modelValue"])

const shiftStore = usePOSShiftStore()
const uiStore = usePOSUIStore()
const toast = useToast()

const sourceWarehouse = ref("")
const targetWarehouse = ref("")
const allWarehouses = ref([])

const itemSearchQuery = ref("")
const searchResults = ref([])
const showSearchDropdown = ref(false)
const selectedItems = ref([])
const isSubmitting = ref(false)
const successData = ref(null)

let searchTimeout = null

// Load warehouses from POS profile
onMounted(() => {
	// Usually the profile has a list of allowed warehouses, but for now we can just fetch all or use the ones in shiftStore
    loadWarehouses()
	document.addEventListener('click', closeDropdown)
})

onUnmounted(() => {
	document.removeEventListener('click', closeDropdown)
})

async function loadWarehouses() {
    try {
        const res = await call("pos_next.api.pos_profile.get_warehouses", {
            pos_profile: shiftStore.profileName
        });
        allWarehouses.value = res || [];
        
        // Default source warehouse
        if (allWarehouses.value.length > 0) {
            sourceWarehouse.value = shiftStore.profileWarehouse || allWarehouses.value[0].name;
        }
    } catch (e) {
        console.error("Failed to load warehouses", e);
    }
}

function closeDropdown(e) {
	if (!e.target.closest('.relative')) {
		showSearchDropdown.value = false
	}
}

const canSubmit = computed(() => {
	return sourceWarehouse.value && 
		   targetWarehouse.value && 
		   sourceWarehouse.value !== targetWarehouse.value && 
		   selectedItems.value.length > 0
})

function debouncedSearch() {
	showSearchDropdown.value = true
	if (searchTimeout) clearTimeout(searchTimeout)
	searchTimeout = setTimeout(async () => {
		if (itemSearchQuery.value.length < 2) {
			searchResults.value = []
			return
		}
		try {
			const res = await call("pos_next.api.items.get_items", {
				search_term: itemSearchQuery.value,
				pos_profile: shiftStore.profileName,
                limit: 10
			})
			searchResults.value = res || []
		} catch (e) {
			console.error(e)
		}
	}, 300)
}

async function addItem(item) {
    if (!sourceWarehouse.value) {
        toast.showError(__("Please select Source Warehouse first"));
        return;
    }

    try {
        const res = await call("pos_next.api.items.get_stock_quantities", {
            item_codes: [item.item_code],
            warehouse: sourceWarehouse.value
        });
        
        const actualQty = res && res.length > 0 ? res[0].actual_qty : 0;
        
        if (actualQty <= 0) {
            toast.showWarning(__("Item {0} has no available stock in {1}", [item.item_name, sourceWarehouse.value]));
            return;
        }

        const existing = selectedItems.value.find(i => i.item_code === item.item_code)
        if (existing) {
            if (existing.qty + 1 > actualQty) {
                toast.showWarning(__("Cannot transfer more than available quantity ({0})", [actualQty]));
                existing.qty = actualQty;
            } else {
                existing.qty++;
            }
        } else {
            selectedItems.value.push({
                item_code: item.item_code,
                item_name: item.item_name,
                qty: 1,
                max_qty: actualQty,
                uom: item.stock_uom || item.uom
            })
        }
    } catch (e) {
        console.error(e);
        toast.showError(__("Failed to fetch stock quantity"));
    }

	itemSearchQuery.value = ""
	showSearchDropdown.value = false
}

function validateQty(item) {
    if (item.max_qty !== undefined && item.qty > item.max_qty) {
        item.qty = item.max_qty;
        toast.showWarning(__("Cannot transfer more than available quantity ({0})", [item.max_qty]));
    } else if (item.qty < 1 || !item.qty) {
        item.qty = 1;
    }
}

function removeItem(index) {
	selectedItems.value.splice(index, 1)
}

async function submitTransfer() {
	if (!canSubmit.value) return
	
	isSubmitting.value = true
	try {
		const res = await call("pos_next.api.stock.create_stock_transfer", {
			items: JSON.stringify(selectedItems.value),
			source_warehouse: sourceWarehouse.value,
			target_warehouse: targetWarehouse.value,
			company: shiftStore.profileCompany
		})
		
		// Show success state
        successData.value = res
	} catch (e) {
		uiStore.showError(e.message || __("Failed to transfer stock"))
	} finally {
		isSubmitting.value = false
	}
}

function resetForm() {
    successData.value = null
    selectedItems.value = []
    targetWarehouse.value = ""
}

function printEntry(stockEntryName) {
    const params = new URLSearchParams({
        doctype: "Stock Entry",
        name: stockEntryName,
        trigger_print: 1,
        no_letterhead: 0,
        _t: Date.now(),
    })
    const printUrl = `/printview?${params.toString()}`
    const printWindow = window.open(
        printUrl,
        'pos_print_se',
        'width=900,height=700,toolbar=0,scrollbars=1,status=0,resizable=1'
    )
    if (!printWindow) {
        toast.showWarning(__("Popup blocker prevented printing. Please allow popups for this site."))
    } else {
        printWindow.addEventListener('afterprint', () => printWindow.close())
    }
}

const isLoadingAll = ref(false)

async function selectAllAvailable() {
    if (!sourceWarehouse.value) return;
    
    isLoadingAll.value = true;
    try {
        const items = await call("pos_next.api.stock.get_available_items_in_warehouse", {
            warehouse: sourceWarehouse.value
        });
        
        if (items && items.length > 0) {
            // Merge with selected items
            items.forEach(item => {
                const existing = selectedItems.value.find(i => i.item_code === item.item_code);
                if (!existing) {
                        selectedItems.value.push({
                            item_code: item.item_code,
                            item_name: item.item_name,
                            qty: item.available_qty,
                            max_qty: item.available_qty,
                            uom: item.uom
                        });
                }
            });
            toast.showSuccess(__("Added {0} items", [items.length]));
        } else {
            toast.showWarning(__("No available items found in this warehouse"));
        }
    } catch (e) {
        console.error(e);
        toast.showError(e.message || __("Failed to fetch available items"));
    } finally {
        isLoadingAll.value = false;
    }
}
</script>
