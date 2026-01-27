<template>
	<Dialog v-model="show" :options="{ title: isEditMode ? __('Edit Customer') : __('Create New Customer'), size: 'md' }">
		<template #body-content>
			<div class="flex flex-col gap-6">
				<!-- Customer Name (Required) -->
				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="block text-start text-sm font-medium text-gray-700 mb-2">
							{{ __("Customer Name") }} <span class="text-red-500">*</span>
						</label>
						<Input
							v-model="customerData.customer_name"
							type="text"
							:placeholder="__('Enter customer name')"
							required
						/>
					</div>
					<!-- VAT Registration Number -->
					<div>
						<label class="block text-start text-sm font-medium text-gray-700 mb-2">
							{{ __("VAT Registration Number") }}
						</label>
						<Input
							v-model="customerData.custom_vat_registration_number"
							type="text"
							:placeholder="__('Enter VAT number')"
						/>
					</div>
				</div>

				<!-- Mobile Number with Country Code Selector -->
				<div>
					<label class="block text-start text-sm font-medium text-gray-700 mb-2">
						{{ __("Mobile Number") }}
					</label>
					<div class="flex gap-2">
						<!-- Country Code Dropdown -->
						<div class="relative" ref="dropdownRef">
							<button
								type="button"
								@click="showCountryDropdown = !showCountryDropdown"
								class="flex items-center gap-1 w-24 ps-2 pe-1 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white hover:bg-gray-50"
							>
								<img
									:src="`https://flagcdn.com/h24/${currentCountryCode}.png`"
									:alt="currentCountryCode"
									class="w-6 h-auto rounded-sm"
									@error="handleFlagError"
								/>
								<span class="flex-1 text-start">{{ selectedCountryCode || "+20" }}</span>
								<svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
								</svg>
							</button>

							<!-- Country Search Dropdown -->
							<div
								v-if="showCountryDropdown"
								class="absolute start-0 z-50 mt-1 w-80 max-h-80 bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden"
							>
								<div class="sticky top-0 bg-white border-b border-gray-200 p-2">
									<input
										ref="countrySearchRef"
										v-model="countrySearchQuery"
										type="text"
										:placeholder="__('Search country or code...')"
										class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
										@keydown.escape="showCountryDropdown = false"
									/>
								</div>
								<div class="overflow-y-auto max-h-64">
									<button
										v-for="country in filteredCountries"
										:key="country.code"
										type="button"
										@click="selectCountry(country)"
										class="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-gray-50 transition-colors text-start"
										:class="{ 'bg-blue-50': selectedCountryCode === country.isd }"
									>
										<img
											:src="`https://flagcdn.com/h24/${country.code.toLowerCase()}.png`"
											:alt="country.name"
											class="w-6 h-auto rounded-sm shadow-sm"
											@error="(e) => (e.target.style.display = 'none')"
										/>
										<span class="flex-1 text-sm font-medium text-gray-700">{{ country.name }}</span>
										<span class="text-sm text-gray-500">{{ country.isd }}</span>
									</button>
									<div v-if="filteredCountries.length === 0" class="px-4 py-8 text-center text-sm text-gray-500">
										{{ __("No countries found") }}
									</div>
								</div>
							</div>
						</div>

						<!-- Phone Number Input -->
						<input
							v-model="phoneNumber"
							type="tel"
							:placeholder="__('Enter phone number')"
							class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-start"
							@input="updateMobileNumber"
						/>
					</div>
				</div>

				<!-- Email -->
				<div>
					<label class="block text-start text-sm font-medium text-gray-700 mb-2">
						{{ __("Email") }}
					</label>
					<Input v-model="customerData.email_id" type="email" :placeholder="__('Enter email address')" />
				</div>

				<!-- Territory -->
				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="block text-start text-sm font-medium text-gray-700 mb-2">
							{{ __("Customer Group") }}
						</label>
						<select
							v-model="customerData.customer_group"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
						>
							<option value="">{{ __("Select Customer Group") }}</option>
							<option v-for="group in customerGroups" :key="group" :value="group">
								{{ group }}
							</option>
						</select>
					</div>
					<div>
						<label class="block text-start text-sm font-medium text-gray-700 mb-2">
							{{ __("Territory") }}
						</label>
						<select
							v-model="customerData.territory"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
						>
							<option value="">{{ __("Select Territory") }}</option>
							<option v-for="territory in territories" :key="territory" :value="territory">
								{{ territory }}
							</option>
						</select>
					</div>
				</div>

				<!-- Address Section -->
				<div class="border-t border-gray-100 pt-6">
					<h3 class="text-sm font-semibold text-gray-900 mb-4">{{ __("Address Details") }}</h3>
					
					<div class="grid grid-cols-2 gap-4 mb-4">
						<!-- Building Number -->
						<div>
							<label class="block text-start text-sm font-medium text-gray-700 mb-2">
								{{ __("Building Number") }}
							</label>
							<Input
								v-model="addressData.custom_building_number"
								type="text"
								:placeholder="__('Building No')"
							/>
						</div>
						<!-- Street Name -->
						<div>
							<label class="block text-start text-sm font-medium text-gray-700 mb-2">
								{{ __("Street Name") }}
							</label>
							<Input
								v-model="addressData.address_line1"
								type="text"
								:placeholder="__('Street Name')"
							/>
						</div>
					</div>

					<div class="grid grid-cols-2 gap-4 mb-4">
						<!-- Additional No (Address Line 2) -->
						<div>
							<label class="block text-start text-sm font-medium text-gray-700 mb-2">
								{{ __("Additional No") }}
							</label>
							<Input
								v-model="addressData.address_line2"
								type="text"
								:placeholder="__('Additional No')"
							/>
						</div>
						<!-- Area/District -->
						<div>
							<label class="block text-start text-sm font-medium text-gray-700 mb-2">
								{{ __("Area/District") }}
							</label>
							<Input
								v-model="addressData.custom_area"
								type="text"
								:placeholder="__('Area/District')"
							/>
						</div>
					</div>

					<div class="grid grid-cols-2 gap-4">
						<!-- City -->
						<div>
							<label class="block text-start text-sm font-medium text-gray-700 mb-2">
								{{ __("City") }}
							</label>
							<Input
								v-model="addressData.city"
								type="text"
								:placeholder="__('City')"
							/>
						</div>
						<!-- Postal Code -->
						<div>
							<label class="block text-start text-sm font-medium text-gray-700 mb-2">
								{{ __("Postal Code") }}
							</label>
							<Input
								v-model="addressData.pincode"
								type="text"
								:placeholder="__('Postal Code')"
							/>
						</div>
					</div>
				</div>
			</div>
		</template>

		<template #actions>
			<div class="flex flex-col gap-2">
				<!-- Permission Warning -->
				<div v-if="!hasPermission" class="px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg">
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
								{{ __("You don't have permission to create customers. Contact your administrator.") }}
							</p>
						</div>
					</div>
				</div>

				<div class="flex gap-2">
					<Button
						variant="solid"
						@click="handleCreate"
						:loading="createCustomerResource.loading || updateCustomerResource.loading || checkingPermission"
						:disabled="!customerData.customer_name || !hasPermission"
					>
						{{ isEditMode ? __("Save Changes") : __("Create Customer") }}
					</Button>
					<Button variant="subtle" @click="show = false">
						{{ __("Cancel") }}
					</Button>
				</div>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
/**
 * CreateCustomerDialog - Quick customer creation from POS
 *
 * Features:
 * - Country code selector with flag icons and search
 * - Auto-sets territory based on selected country
 * - Permission checking before allowing creation
 * - Lazy loads countries data when dialog opens (not on app startup)
 */

import { usePOSPermissions } from "@/composables/usePermissions"
import { useToast } from "@/composables/useToast"
import { useCountriesStore } from "@/stores/countries"
import { logger } from "@/utils/logger"
import { Button, Dialog, Input, createResource } from "frappe-ui"
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue"

const log = logger.create("CreateCustomerDialog")

// =============================================================================
// Composables & Stores
// =============================================================================

const countriesStore = useCountriesStore()
const { canCreateCustomer } = usePOSPermissions()
const { showSuccess, showError } = useToast()

// =============================================================================
// Props & Emits
// =============================================================================

const props = defineProps({
	modelValue: Boolean,
	posProfile: String,
	initialName: String,
	customer: Object, // Customer object for edit mode
})

const emit = defineEmits(["update:modelValue", "customer-created", "customer-updated"])

// =============================================================================
// State
// =============================================================================

const hasPermission = ref(true)
const checkingPermission = ref(false)
const selectedCountryCode = ref("")
const phoneNumber = ref("")
const showCountryDropdown = ref(false)
const countrySearchQuery = ref("")
const dropdownRef = ref(null)
const countrySearchRef = ref(null)

const customerGroups = ref(["Commercial", "Individual", "Non Profit", "Government"])
const territories = ref(["All Territories"])

const customerData = ref({
	customer_name: "",
	mobile_no: "",
	email_id: "",
	customer_group: "Individual",
	territory: "All Territories",
	custom_vat_registration_number: "",
})

const addressData = ref({
	name: "",
	custom_building_number: "",
	address_line1: "",
	address_line2: "",
	custom_area: "",
	city: "",
	pincode: "",
	country: "",
})

// =============================================================================
// Computed
// =============================================================================

const show = computed({
	get: () => props.modelValue,
	set: (val) => emit("update:modelValue", val),
})

const isEditMode = computed(() => !!props.customer?.name)

const currentCountryCode = computed(() => {
	const country = countriesStore.countries.find((c) => c.isd === selectedCountryCode.value)
	return country?.code.toLowerCase() || "eg"
})

const filteredCountries = computed(() => {
	if (!countrySearchQuery.value) return countriesStore.countries

	const query = countrySearchQuery.value.toLowerCase()
	return countriesStore.countries.filter(
		(c) => c.name.toLowerCase().includes(query) || c.isd.includes(query) || c.code.toLowerCase().includes(query)
	)
})

// =============================================================================
// Country & Territory Methods
// =============================================================================

const handleFlagError = (e) => (e.target.style.display = "none")

const selectCountry = (country) => {
	selectedCountryCode.value = country.isd
	showCountryDropdown.value = false
	countrySearchQuery.value = ""
	updateMobileNumber()
}

const updateMobileNumber = () => {
	customerData.value.mobile_no = phoneNumber.value ? `${selectedCountryCode.value}-${phoneNumber.value}` : ""
}

const handleClickOutside = (event) => {
	if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
		showCountryDropdown.value = false
		countrySearchQuery.value = ""
	}
}

const setCountryFromName = (countryName) => {
	if (!countryName) {
		selectedCountryCode.value = "+20"
		return
	}

	const isd = countriesStore.countryNameToISDMap[countryName]
	if (isd) {
		selectedCountryCode.value = isd
		log.info(`Set country code to ${isd} for ${countryName}`)
	} else {
		log.warn(`Country "${countryName}" not found`)
		selectedCountryCode.value = "+20"
	}
}

/** Auto-set territory based on selected country (exact or fuzzy match) */
const updateTerritoryFromCountry = () => {
	if (!territories.value.length) return

	const country = countriesStore.countries.find((c) => c.isd === selectedCountryCode.value)
	if (!country) return

	// Try exact match first
	if (territories.value.includes(country.name)) {
		customerData.value.territory = country.name
		log.info(`Territory set to: ${country.name}`)
		return
	}

	// Try fuzzy match
	const fuzzyMatch = territories.value.find(
		(t) => t.toLowerCase().includes(country.name.toLowerCase()) || country.name.toLowerCase().includes(t.toLowerCase())
	)

	if (fuzzyMatch) {
		customerData.value.territory = fuzzyMatch
		log.info(`Territory set to fuzzy match: ${fuzzyMatch}`)
	}
}

// =============================================================================
// API Resources
// =============================================================================

const createCustomerResource = createResource({
	url: "frappe.client.insert",
	makeParams: () => ({
		doc: {
			doctype: "Customer",
			customer_name: customerData.value.customer_name,
			customer_type: "Individual",
			customer_group: customerData.value.customer_group || __("Individual"),
			territory: customerData.value.territory || __("All Territories"),
			mobile_no: customerData.value.mobile_no || "",
			email_id: customerData.value.email_id || "",
			custom_vat_registration_number: customerData.value.custom_vat_registration_number || "",
		},
	}),
	onSuccess: async (data) => {
		if (data.name) {
			await saveAddress(data.name)
		}
		showSuccess(__("Customer {0} created successfully", [data.customer_name]))
		emit("customer-created", data)
		show.value = false
	},
	onError: (error) => {
		log.error("Error creating customer", error)
		showError(error.message || __("Failed to create customer"))
	},
})

const updateCustomerResource = createResource({
	url: "frappe.client.set_value",
	makeParams: () => ({
		doctype: "Customer",
		name: props.customer?.name,
		fieldname: {
			customer_name: customerData.value.customer_name,
			customer_group: customerData.value.customer_group || __("Individual"),
			territory: customerData.value.territory || __("All Territories"),
			mobile_no: customerData.value.mobile_no || "",
			email_id: customerData.value.email_id || "",
			custom_vat_registration_number: customerData.value.custom_vat_registration_number || "",
		},
	}),
	onSuccess: async (data) => {
		await saveAddress(props.customer?.name)
		showSuccess(__("Customer {0} updated successfully", [data.customer_name]))
		emit("customer-updated", data)
		show.value = false
	},
	onError: (error) => {
		log.error("Error updating customer", error)
		showError(error.message || __("Failed to update customer"))
	},
})

/** Helper to create list fetch resources */
const createListResource = (doctype, onSuccess) =>
	createResource({
		url: "frappe.client.get_list",
		makeParams: () => ({
			doctype,
			fields: ["name"],
			filters: doctype === "Customer Group" ? { is_group: 0 } : {},
			limit_page_length: 500,
		}),
		auto: false,
		onSuccess: (data) => data?.length && onSuccess(data.map((d) => d.name)),
		onError: (err) => log.error(`Error loading ${doctype}`, err),
	})

const customerGroupsResource = createListResource("Customer Group", (names) => (customerGroups.value = names))
const territoriesResource = createListResource("Territory", (names) => (territories.value = names))

const posProfileResource = createResource({
	url: "frappe.client.get_value",
	makeParams: () => ({
		doctype: "POS Profile",
		filters: { name: props.posProfile },
		fieldname: ["country"],
	}),
	auto: false,
	onSuccess: (data) => {
		const country = data?.country || "Egypt"
		setCountryFromName(country)
		addressData.value.country = country
	},
	onError: (err) => {
		log.error("Error loading POS Profile", err)
		selectedCountryCode.value = "+20"
		addressData.value.country = "Egypt"
	},
})

const saveAddress = async (customerName) => {
	// Check if any address field is filled
	const hasAddress =
		addressData.value.custom_building_number ||
		addressData.value.address_line1 ||
		addressData.value.address_line2 ||
		addressData.value.custom_area ||
		addressData.value.city

	if (!hasAddress) return

	const addressDoc = {
		doctype: "Address",
		address_title: customerData.value.customer_name,
		address_type: "Billing",
		custom_building_number: addressData.value.custom_building_number || "",
		address_line1: addressData.value.address_line1 || "",
		address_line2: addressData.value.address_line2 || "",
		custom_area: addressData.value.custom_area || "",
		city: addressData.value.city || "",
		pincode: addressData.value.pincode || "",
		country: addressData.value.country || "Egypt",
		links: [
			{
				link_doctype: "Customer",
				link_name: customerName,
			},
		],
	}

	try {
		if (addressData.value.name) {
			// Update existing address
			await createResource({
				url: "frappe.client.set_value",
				params: {
					doctype: "Address",
					name: addressData.value.name,
					fieldname: addressDoc,
				},
			}).submit()
		} else {
			// Create new address
			await createResource({
				url: "frappe.client.insert",
				params: {
					doc: addressDoc,
				},
			}).submit()
		}
	} catch (err) {
		log.error("Error saving address", err)
	}
}

const fetchCustomerAddress = async (customerName) => {
	try {
		const addresses = await createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Address",
				filters: {
					link_doctype: "Customer",
					link_name: customerName,
				},
				fields: ["*"],
				limit_page_length: 1,
			},
		}).submit()

		if (addresses && addresses.length > 0) {
			const addr = addresses[0]
			addressData.value = {
				name: addr.name,
				custom_building_number: addr.custom_building_number || "",
				address_line1: addr.address_line1 || "",
				address_line2: addr.address_line2 || "",
				custom_area: addr.custom_area || "",
				city: addr.city || "",
				pincode: addr.pincode || "",
				country: addr.country || "",
			}
		}
	} catch (err) {
		log.error("Error fetching address", err)
	}
}

// =============================================================================
// Dialog Lifecycle
// =============================================================================

const loadDialogData = async () => {
	// Lazy load countries (non-blocking)
	countriesStore.loadCountries()

	// Load form options
	await territoriesResource.reload()
	customerGroupsResource.reload()
	checkPermissions()

	// Set country from POS Profile
	if (props.posProfile) {
		await posProfileResource.reload()
	} else {
		selectedCountryCode.value = "+20"
		addressData.value.country = "Egypt"
	}

	if (isEditMode.value) {
		await fetchCustomerAddress(props.customer.name)
	}
}

const checkPermissions = async () => {
	checkingPermission.value = true
	try {
		hasPermission.value = await canCreateCustomer()
	} catch (err) {
		log.error("Permission check failed", err)
		hasPermission.value = false
	} finally {
		checkingPermission.value = false
	}
}

const handleCreate = async () => {
	if (!customerData.value.customer_name) {
		return showError(__("Customer Name is required"))
	}
	if (isEditMode.value) {
		await updateCustomerResource.submit()
	} else {
		await createCustomerResource.submit()
	}
}

const resetForm = () => {
	Object.assign(customerData.value, {
		customer_name: "",
		mobile_no: "",
		email_id: "",
		customer_group: "Individual",
		territory: "All Territories",
		custom_vat_registration_number: "",
	})
	Object.assign(addressData.value, {
		name: "",
		custom_building_number: "",
		address_line1: "",
		address_line2: "",
		custom_area: "",
		city: "",
		pincode: "",
		country: addressData.value.country || "Egypt",
	})
	selectedCountryCode.value = ""
	phoneNumber.value = ""
}

// =============================================================================
// Watchers
// =============================================================================

watch(
	() => props.initialName,
	(name) => name && (customerData.value.customer_name = name)
)

// Pre-fill form when customer prop changes (edit mode)
watch(
	() => props.customer,
	(customer) => {
		if (customer?.name) {
			customerData.value.customer_name = customer.customer_name || ""
			customerData.value.email_id = customer.email_id || ""
			customerData.value.customer_group = customer.customer_group || "Individual"
			customerData.value.territory = customer.territory || "All Territories"
			customerData.value.custom_vat_registration_number = customer.custom_vat_registration_number || ""
			// Handle mobile_no with country code
			if (customer.mobile_no) {
				customerData.value.mobile_no = customer.mobile_no
				if (customer.mobile_no.includes("-")) {
					const [code, ...rest] = customer.mobile_no.split("-")
					selectedCountryCode.value = code
					phoneNumber.value = rest.join("-")
				} else {
					phoneNumber.value = customer.mobile_no
				}
			}
		}
	},
	{ immediate: true }
)

watch(
	() => customerData.value.mobile_no,
	(value) => {
		if (value?.includes("-")) {
			const [code, ...rest] = value.split("-")
			selectedCountryCode.value = code
			phoneNumber.value = rest.join("-")
		}
	}
)

watch(selectedCountryCode, async () => {
	await nextTick()
	updateTerritoryFromCountry()
})

watch(showCountryDropdown, async (isOpen) => {
	if (isOpen) {
		await nextTick()
		countrySearchRef.value?.focus()
	}
})

watch(
	() => props.modelValue,
	async (isOpen) => {
		show.value = isOpen
		isOpen ? await loadDialogData() : resetForm()
	}
)

watch(show, (val) => emit("update:modelValue", val))

// =============================================================================
// Lifecycle Hooks
// =============================================================================

onMounted(() => {
	loadDialogData()
	document.addEventListener("click", handleClickOutside)
})

onBeforeUnmount(() => {
	document.removeEventListener("click", handleClickOutside)
})
</script>

<style scoped>
.sr-only {
	position: absolute;
	width: 1px;
	height: 1px;
	padding: 0;
	margin: -1px;
	overflow: hidden;
	clip: rect(0, 0, 0, 0);
	white-space: nowrap;
	border-width: 0;
}
</style>
