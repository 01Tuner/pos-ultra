import { useSalesOrderFiltersStore } from "@/stores/salesOrderFilters"
import { computed } from "vue"

/**
 * Sales Order Filters Composable
 *
 * Provides filtering logic for sales order lists
 * Works with the sales order filters store for state management
 *
 * @param {Array} orders - Array of sales order objects to filter
 * @returns {Object} Filtered orders and helper functions
 */
export function useSalesOrderFilters(orders) {
    const filtersStore = useSalesOrderFiltersStore()

    /**
     * Apply all active filters to the order list
     */
    const filteredOrders = computed(() => {
        if (!Array.isArray(orders.value)) return []

        let result = [...orders.value]

        // Apply search term filter
        if (filtersStore.searchTerm) {
            const search = filtersStore.searchTerm.toLowerCase()
            result = result.filter(
                (order) =>
                    order.name?.toLowerCase().includes(search) ||
                    order.customer_name?.toLowerCase().includes(search) ||
                    order.customer?.toLowerCase().includes(search),
            )
        }

        // Apply date range filter
        if (filtersStore.dateFrom) {
            const fromDate = new Date(filtersStore.dateFrom)
            fromDate.setHours(0, 0, 0, 0)
            result = result.filter((order) => {
                // Use transaction_date for Sales Orders
                const orderDate = new Date(order.transaction_date || order.posting_date)
                orderDate.setHours(0, 0, 0, 0)
                return orderDate >= fromDate
            })
        }

        if (filtersStore.dateTo) {
            const toDate = new Date(filtersStore.dateTo)
            toDate.setHours(23, 59, 59, 999)
            result = result.filter((order) => {
                const orderDate = new Date(order.transaction_date || order.posting_date)
                return orderDate <= toDate
            })
        }

        // Apply customer filter
        if (filtersStore.customer) {
            result = result.filter(
                (order) =>
                    order.customer === filtersStore.customer ||
                    order.customer_name === filtersStore.customer,
            )
        }

        // Apply status filter
        if (filtersStore.status) {
            result = result.filter((order) => order.status === filtersStore.status)
        }

        // Apply product filter
        if (filtersStore.product) {
            const productSearch = filtersStore.product.toLowerCase()
            result = result.filter((order) => {
                if (!order.items || !Array.isArray(order.items)) return false
                return order.items.some(
                    (item) =>
                        item.item_name?.toLowerCase().includes(productSearch) ||
                        item.item_code?.toLowerCase().includes(productSearch),
                )
            })
        }

        return result
    })

    /**
     * Get unique customers from orders for dropdown
     */
    const uniqueCustomers = computed(() => {
        if (!Array.isArray(orders.value)) return []

        const customersMap = new Map()

        orders.value.forEach((order) => {
            if (order.customer) {
                const customerName = order.customer_name || order.customer
                customersMap.set(order.customer, customerName)
            }
        })

        return Array.from(customersMap.entries())
            .map(([value, label]) => ({ value, label }))
            .sort((a, b) => a.label.localeCompare(b.label))
    })

    /**
     * Get unique statuses from orders
     */
    const uniqueStatuses = computed(() => {
        if (!Array.isArray(orders.value)) return []

        const statuses = new Set()
        orders.value.forEach((order) => {
            if (order.status) {
                statuses.add(order.status)
            }
        })

        return Array.from(statuses).sort()
    })

    /**
     * Get unique products from orders for dropdown
     */
    const uniqueProducts = computed(() => {
        if (!Array.isArray(orders.value)) return []

        const productsMap = new Map()

        orders.value.forEach((order) => {
            if (order.items && Array.isArray(order.items)) {
                order.items.forEach((item) => {
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
     * Get customer name from value
     */
    function getCustomerName(customerValue) {
        const customer = uniqueCustomers.value.find(
            (c) => c.value === customerValue,
        )
        return customer ? customer.label : customerValue
    }

    /**
     * Get filter statistics
     */
    const filterStats = computed(() => {
        return {
            total: orders.value?.length || 0,
            filtered: filteredOrders.value.length,
            percentage: orders.value?.length
                ? Math.round(
                    (filteredOrders.value.length / orders.value.length) * 100,
                )
                : 0,
        }
    })

    return {
        // Filtered data
        filteredOrders,
        uniqueCustomers,
        uniqueProducts,
        uniqueStatuses,
        filterStats,

        // Helper functions
        getCustomerName,

        // Store access (for convenience)
        store: filtersStore,
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
    { label: __("To Deliver"), value: "To Deliver" },
    { label: __("To Bill"), value: "To Bill" },
    { label: __("To Deliver and Bill"), value: "To Deliver and Bill" },
    { label: __("Completed"), value: "Completed" },
    { label: __("Cancelled"), value: "Cancelled" },
]
