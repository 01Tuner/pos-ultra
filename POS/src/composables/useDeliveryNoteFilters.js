import { computed } from "vue"
import { useDeliveryNoteFiltersStore } from "@/stores/deliveryNoteFilters"

/**
 * Delivery Note Filters Composable
 *
 * Provides filtering logic for delivery note lists
 * Works with the delivery note filters store for state management
 *
 * @param {Array} deliveryNotes - Array of delivery note objects to filter
 * @returns {Object} Filtered delivery notes and helper functions
 */
export function useDeliveryNoteFilters(deliveryNotes) {
    const store = useDeliveryNoteFiltersStore()

    // Main Filtering Logic
    const filteredNotes = computed(() => {
        if (!Array.isArray(deliveryNotes.value)) return []

        let result = [...deliveryNotes.value]

        // 1. Search Term
        if (store.searchTerm) {
            const term = store.searchTerm.toLowerCase()
            result = result.filter(
                (dn) =>
                    dn.name?.toLowerCase().includes(term) ||
                    (dn.customer_name && dn.customer_name.toLowerCase().includes(term)),
            )
        }

        // 2. Status
        if (store.status) {
            result = result.filter((dn) => dn.status === store.status)
        }

        // 3. Customer
        if (store.customer) {
            result = result.filter(
                (dn) => (dn.customer_name || dn.customer) === store.customer,
            )
        }

        // 4. Product
        if (store.product) {
            const productSearch = store.product.toLowerCase()
            result = result.filter((dn) =>
                dn.items?.some(
                    (item) =>
                        item.item_name?.toLowerCase().includes(productSearch) ||
                        item.item_code?.toLowerCase().includes(productSearch),
                ),
            )
        }

        // 5. Date Range
        if (store.dateFrom) {
            const fromDate = new Date(store.dateFrom)
            fromDate.setHours(0, 0, 0, 0)
            result = result.filter((dn) => {
                const dnDate = new Date(dn.transaction_date)
                dnDate.setHours(0, 0, 0, 0)
                return dnDate >= fromDate
            })
        }

        if (store.dateTo) {
            const toDate = new Date(store.dateTo)
            toDate.setHours(23, 59, 59, 999)
            result = result.filter((dn) => {
                const dnDate = new Date(dn.transaction_date)
                return dnDate <= toDate
            })
        }

        return result
    })

    /**
     * Get unique customers from notes for dropdown
     */
    const uniqueCustomers = computed(() => {
        if (!Array.isArray(deliveryNotes.value)) return []

        const customersMap = new Map()

        deliveryNotes.value.forEach((dn) => {
            if (dn.customer) {
                const customerName = dn.customer_name || dn.customer
                customersMap.set(dn.customer, customerName)
            }
        })

        return Array.from(customersMap.entries())
            .map(([value, label]) => ({ value, label }))
            .sort((a, b) => a.label.localeCompare(b.label))
    })

    /**
     * Get unique statuses from notes
     */
    const uniqueStatuses = computed(() => {
        if (!Array.isArray(deliveryNotes.value)) return []

        const statuses = new Set()
        deliveryNotes.value.forEach((dn) => {
            if (dn.status) {
                statuses.add(dn.status)
            }
        })

        return Array.from(statuses).sort()
    })

    /**
     * Get unique products from notes for dropdown
     */
    const uniqueProducts = computed(() => {
        if (!Array.isArray(deliveryNotes.value)) return []

        const productsMap = new Map()

        deliveryNotes.value.forEach((dn) => {
            if (dn.items && Array.isArray(dn.items)) {
                dn.items.forEach((item) => {
                    if (item.item_code) {
                        const productName = item.item_name || item.item_code
                        productsMap.set(item.item_code, {
                            value: item.item_code,
                            label: productName,
                            subtitle: item.item_code !== productName ? item.item_code : null,
                        })
                    }
                })
            }
        })

        return Array.from(productsMap.values()).sort((a, b) =>
            a.label.localeCompare(b.label),
        )
    })

    /**
     * Get filter statistics
     */
    const filterStats = computed(() => {
        return {
            total: deliveryNotes.value?.length || 0,
            filtered: filteredNotes.value.length,
            percentage: deliveryNotes.value?.length
                ? Math.round(
                    (filteredNotes.value.length / deliveryNotes.value.length) * 100,
                )
                : 0,
        }
    })

    return {
        // Filtered data
        filteredNotes,
        uniqueCustomers,
        uniqueProducts,
        uniqueStatuses,
        filterStats,

        // Store access (for convenience)
        store,
    }
}

/**
 * Quick date filter presets
 */
export const DATE_PRESETS = [
    { label: __("Today"), value: "today", action: "setToday" },
    { label: __("Yesterday"), value: "yesterday", action: "setYesterday" },
    { label: __("This Week"), value: "week", action: "setThisWeek" },
    { label: __("This Month"), value: "month", action: "setThisMonth" },
    { label: __("Last 7 Days"), value: "last7", action: "setLast7Days" },
    { label: __("Last 30 Days"), value: "last30", action: "setLast30Days" },
]

/**
 * Status options
 */
export const STATUS_OPTIONS = [
    { label: __("All Status"), value: "" },
    { label: __("Draft"), value: "Draft" },
    { label: __("To Bill"), value: "To Bill" },
    { label: __("Completed"), value: "Completed" },
    { label: __("Return"), value: "Return" },
    { label: __("Cancelled"), value: "Cancelled" },
]
