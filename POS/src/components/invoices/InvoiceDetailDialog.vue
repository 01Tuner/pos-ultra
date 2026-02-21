<template>
	<Dialog
		v-model="show"
		:options="{ title: __('Invoice Details'), size: '5xl' }"
	>
		<template #body-content>
			<div v-if="loading" class="text-center py-12">
				<div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500 mx-auto"></div>
				<p class="mt-3 text-sm text-gray-500">{{ __('Loading invoice details...') }}</p>
			</div>

			<div v-else-if="invoiceData" class="flex flex-col gap-6">
				<!-- Invoice Header -->
				<div class="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg p-4 md:p-5 border border-indigo-100">
					<div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
						<div class="flex-1">
							<div class="flex items-center gap-3 mb-2 flex-wrap">
								<h3 class="text-lg md:text-xl font-bold text-gray-900">{{ invoiceData.name }}</h3>
								<span
									v-if="invoiceData.is_return"
									class="px-3 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800"
								>
									{{ __('Return Invoice') }}
								</span>
								<span
									v-else
									:class="[
										'px-3 py-1 text-xs font-semibold rounded-full',
										getInvoiceStatusColor(invoiceData)
									]"
								>
									{{ __(invoiceData.status) }}
								</span>
							</div>
							<div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
								<div class="text-start">
									<span class="text-gray-600">{{ __('Customer:') }}</span>
									<span class="ms-2 font-semibold text-gray-900">{{ invoiceData.customer_name || invoiceData.customer }}</span>
								</div>
								<div class="text-start">
									<span class="text-gray-600">{{ __('Date:') }}</span>
									<span class="ms-2 font-medium text-gray-900">{{ formatDate(invoiceData.posting_date) }} {{ formatTime(invoiceData.posting_time) }}</span>
								</div>
								<div v-if="invoiceData.return_against" class="text-start">
									<span class="text-gray-600">{{ __('Return Against:') }}</span>
									<span class="ms-2 font-medium text-gray-900">{{ invoiceData.return_against }}</span>
								</div>
							</div>
						</div>
					</div>
						<div class="flex flex-col sm:items-end gap-3">
							<div class="text-start sm:text-end">
								<div class="text-xs text-gray-500 mb-1">{{ __('Grand Total') }}</div>
								<div class="text-xl md:text-2xl font-bold text-indigo-600">
									{{ formatCurrency(invoiceData.grand_total) }}
								</div>
							</div>
                            <!-- Action Buttons -->
                            <div class="flex gap-2">
                                <Dropdown
                                    v-if="!invoiceData.is_return && invoiceData.status !== 'Cancelled' && invoiceData.docstatus === 1 && !invoiceData.update_stock && allowDeliveryNote"
                                    :options="[
                                        {
                                            label: __('Delivery Note'),
                                            icon: 'truck',
                                            onClick: handleCreateDeliveryNote
                                        }
                                    ]"
                                >
                                    <template #default="{ open }">
                                        <Button
                                            variant="subtle"
                                            theme="gray"
                                            size="sm"
                                            class="shadow-sm border border-gray-200"
                                        >
                                            <template #prefix>
                                                <FeatherIcon name="plus" class="w-4 h-4" />
                                            </template>
                                            {{ __('Create') }}
                                            <template #suffix>
                                                <FeatherIcon name="chevron-down" class="w-4 h-4 ml-1 transition-transform" :class="{ 'rotate-180': open }" />
                                            </template>
                                        </Button>
                                    </template>
                                </Dropdown>
                                <Button
                                    v-if="!invoiceData.is_return && invoiceData.status !== 'Cancelled' && allowReturn"
                                    variant="subtle"
                                    theme="gray"
                                    size="sm"
                                    @click="handleReturn"
                                    class="shadow-sm border border-gray-200"
                                >
                                    <template #prefix>
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
                                        </svg>
                                    </template>
                                    {{ __('Return') }}
                                </Button>
                                <Button
                                    v-if="!invoiceData.is_return && invoiceData.outstanding_amount > 0 && invoiceData.status !== 'Cancelled'"
                                    variant="solid"
                                    theme="blue"
                                    size="sm"
                                    @click="handlePayment"
                                    class="shadow-md hover:shadow-lg transition-all"
                                >
                                    <template #prefix>
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                                        </svg>
                                    </template>
                                    {{ __('Payment') }}
                                </Button>
								<Button size="sm" @click="handlePrint">
									<template #prefix>
										<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/>
										</svg>
									</template>
									{{ __('Print') }}
								</Button>
                            </div>
						</div>
					</div>

				<!-- Credit Sale Return Notice -->
				<div v-if="invoiceData.is_return && isCreditSaleReturn" class="bg-gradient-to-r rtl:bg-gradient-to-l from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
					<div class="flex flex-row-reverse items-start gap-3">
						<div class="w-8 h-8 rounded-full bg-blue-200 flex items-center justify-center flex-shrink-0">
							<svg class="w-4 h-4 text-blue-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
							</svg>
						</div>
						<div class="text-end flex-1">
							<h4 class="text-sm font-semibold text-blue-900">{{ __('Credit Sale Return') }}</h4>
							<p class="text-xs text-blue-700 mt-1">
								{{ __('This return was against a Pay on Account invoice. The accounts receivable balance has been reversed. No cash refund was processed.') }}
							</p>
						</div>
					</div>
				</div>

				<!-- Pay on Account Notice (for original credit sales) -->
				<div v-else-if="!invoiceData.is_return && isCreditSale" class="bg-gradient-to-r rtl:bg-gradient-to-l from-amber-50 to-orange-50 rounded-lg p-4 border border-amber-200">
					<div class="flex flex-row-reverse items-start gap-3">
						<div class="w-8 h-8 rounded-full bg-amber-200 flex items-center justify-center flex-shrink-0">
							<svg class="w-4 h-4 text-amber-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
							</svg>
						</div>
						<div class="text-end flex-1">
							<h4 class="text-sm font-semibold text-amber-900">{{ __('Pay on Account') }}</h4>
							<p class="text-xs text-amber-700 mt-1">
								{{ __('This invoice was sold on credit. The customer owes the full amount.') }}
							</p>
						</div>
					</div>
				</div>

				<!-- Items Section -->
				<div>
					<h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
						<svg class="w-4 h-4 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
						</svg>
						{{ __('Items') }}
					</h4>
					<!-- Mobile Cards View -->
					<div class="md:hidden flex flex-col gap-3">
						<div
							v-for="(item, idx) in invoiceData.items"
							:key="idx"
							class="bg-white border border-gray-200 rounded-lg p-3"
						>
							<!-- Item Name & Amount Row -->
							<div class="flex items-center justify-between gap-3 mb-2">
								<div class="flex-1 min-w-0 text-center">
									<div class="text-sm font-semibold text-gray-900">{{ item.item_name }}</div>
									<div class="text-xs text-gray-500">{{ item.item_code }}</div>
								</div>
							</div>
							<!-- Details Grid -->
							<div class="grid grid-cols-3 gap-2 text-center border-t border-gray-100 pt-2">
								<div>
									<div class="text-xs text-gray-500">{{ __('Qty') }}</div>
									<div class="text-sm font-medium text-gray-900">{{ item.quantity }}</div>
								</div>
								<div>
									<div class="text-xs text-gray-500">{{ __('Rate') }}</div>
									<div class="text-sm font-medium text-gray-900">{{ formatCurrency(item.rate) }}</div>
								</div>
								<div>
									<div class="text-xs text-gray-500">{{ __('Amount') }}</div>
									<div class="text-sm font-semibold text-gray-900">{{ formatCurrency(item.amount) }}</div>
								</div>
							</div>
							<!-- Discount Row (if applicable) -->
							<div v-if="item.discount_percentage" class="text-center text-xs text-orange-600 mt-2 pt-2 border-t border-gray-100">
								{{ __('Discount:') }} {{ item.discount_percentage }}%
							</div>
						</div>
					</div>
					<!-- Desktop Table View -->
					<div class="hidden md:block border border-gray-200 rounded-lg overflow-hidden">
						<table class="min-w-full divide-y divide-gray-200">
							<thead class="bg-gray-50">
								<tr>
									<th class="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">{{ __('Item') }}</th>
									<th class="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">{{ __('Qty') }}</th>
									<th class="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">{{ __('Rate') }}</th>
									<th class="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">{{ __('Discount') }}</th>
									<th class="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">{{ __('Amount') }}</th>
								</tr>
							</thead>
							<tbody class="bg-white divide-y divide-gray-200">
								<tr v-for="(item, idx) in invoiceData.items" :key="idx" class="hover:bg-gray-50">
									<td class="px-4 py-3 text-center">
										<div class="text-sm font-medium text-gray-900">{{ item.item_name }}</div>
										<div class="text-xs text-gray-500">{{ item.item_code }}</div>
									</td>
									<td class="px-4 py-3 text-center text-sm text-gray-900">{{ item.quantity }}</td>
									<td class="px-4 py-3 text-center text-sm text-gray-900">{{ formatCurrency(item.rate) }}</td>
									<td class="px-4 py-3 text-center text-sm text-gray-600">
										{{ item.discount_percentage ? `${item.discount_percentage}%` : '-' }}
									</td>
									<td class="px-4 py-3 text-center text-sm font-semibold text-gray-900">{{ formatCurrency(item.amount) }}</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>

				<!-- Totals Section -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
					<!-- Payment Info -->
					<div v-if="invoiceData.payments && invoiceData.payments.length > 0" class="flex flex-col gap-6">
						<!-- Payments Section (Sales Invoice Vouchers) -->
						<div v-if="paymentsList.length > 0">
							<h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
								<svg class="w-4 h-4 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
								</svg>
								{{ __('Payments') }}
							</h4>
							<div class="flex flex-col gap-2">
								<div
									v-for="(payment, idx) in paymentsList"
									:key="idx"
									class="flex justify-between items-center p-3 bg-green-50 border border-green-200 rounded-lg"
								>
									<div class="text-start flex-1">
										<div class="text-sm font-medium text-gray-900">{{ payment.mode_of_payment }}</div>
										<div v-if="payment.voucher_no" class="text-[10px] text-gray-400 mt-0.5 flex items-center gap-2">
											<button
												class="font-medium transition-colors"
											>
												{{ payment.voucher_no }}
											</button>
											<span v-if="payment.creation" class="inline-flex items-center">
												<span class="w-1 h-1 rounded-full bg-gray-400 mx-1"></span>
												{{ formatDate(payment.creation) }} {{ formatTime(payment.creation) }}
											</span>
										</div>
									</div>
									<div class="flex items-center gap-3">
										<div class="text-sm font-semibold text-green-700">{{ formatCurrency(payment.amount) }}</div>
										<button
											@click="handlePrintReceipt(payment)"
											class="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
											:title="__('Print Receipt')"
										>
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/>
											</svg>
										</button>
									</div>
								</div>
							</div>
						</div>

						<!-- Returns Section (Payment Entry Vouchers) -->
						<div v-if="returnsList.length > 0">
							<h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
								<svg class="w-4 h-4 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
								</svg>
								{{ __('Returns') }}
							</h4>
							<div class="flex flex-col gap-2">
								<div
									v-for="(payment, idx) in returnsList"
									:key="idx"
									class="flex justify-between items-center p-3 bg-red-50 border border-red-200 rounded-lg"
								>
									<div class="text-start flex-1">
										<div class="text-sm font-medium text-gray-900">{{ payment.mode_of_payment }}</div>
										<div v-if="payment.voucher_no" class="text-[10px] text-gray-400 mt-0.5 flex items-center gap-2">
											<button
												@click="openDocument(payment)"
												class="hover:text-blue-600 hover:underline cursor-pointer font-medium transition-colors"
												:title="__('Open Document')"
											>
												{{ payment.voucher_no }}
											</button>
											<span v-if="payment.creation" class="inline-flex items-center">
												<span class="w-1 h-1 rounded-full bg-gray-400 mx-1"></span>
												{{ formatDate(payment.creation) }} {{ formatTime(payment.creation) }}
											</span>
										</div>
									</div>
									<div class="flex items-center gap-3">
										<div class="text-sm font-semibold text-red-700">{{ formatCurrency(payment.amount) }}</div>
										<button
											@click="handlePrintReceipt(payment)"
											class="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
											:title="__('Print Receipt')"
										>
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/>
											</svg>
										</button>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- Summary -->
					<div>
						<h4 class="text-sm font-semibold text-gray-700 mb-3 text-start">{{ __('Summary') }}</h4>
						<div class="flex flex-col gap-2 bg-gray-50 p-4 rounded-lg border border-gray-200">
							<div class="flex justify-between text-sm">
								<span class="text-gray-600">{{ __('Net Total:') }}</span>
								<span class="font-medium text-gray-900">{{ formatCurrency(invoiceData.net_total || invoiceData.total) }}</span>
							</div>
							<div v-if="invoiceData.total_taxes_and_charges" class="flex justify-between text-sm">
								<span class="text-gray-600">{{ __('Taxes:') }}</span>
								<span class="font-medium text-gray-900">{{ formatCurrency(invoiceData.total_taxes_and_charges) }}</span>
							</div>
							<div v-if="invoiceData.discount_amount" class="flex justify-between text-sm">
								<span class="text-gray-600">{{ __('Discount:') }}</span>
								<span class="font-medium text-red-600">-{{ formatCurrency(invoiceData.discount_amount) }}</span>
							</div>
							<div class="pt-2 border-t border-gray-300 flex justify-between">
								<span class="font-semibold text-gray-900">{{ __('Grand Total:') }}</span>
								<span class="font-bold text-lg text-indigo-600">{{ formatCurrency(invoiceData.grand_total) }}</span>
							</div>
							<div v-if="invoiceData.paid_amount" class="flex justify-between text-sm">
								<span class="text-gray-600">{{ __('Paid Amount:') }}</span>
								<span class="font-semibold text-green-600">{{ formatCurrency(invoiceData.paid_amount) }}</span>
							</div>
							<!-- For return invoices with negative outstanding (credit to customer) -->
							<div v-if="invoiceData.is_return && invoiceData.outstanding_amount < 0" class="flex justify-between text-sm">
								<span class="text-gray-600">{{ __('Customer Credit:') }}</span>
								<span class="font-semibold text-blue-600">{{ formatCurrency(Math.abs(invoiceData.outstanding_amount)) }}</span>
							</div>
							<!-- For regular invoices with outstanding (customer owes) -->
							<div v-else-if="invoiceData.outstanding_amount && invoiceData.outstanding_amount > 0" class="flex justify-between text-sm">
								<span class="text-gray-600">{{ __('Outstanding:') }}</span>
								<span class="font-semibold text-orange-600">{{ formatCurrency(invoiceData.outstanding_amount) }}</span>
							</div>
						</div>
					</div>
				</div>

				<!-- Related Documents -->
                 <div v-if="(invoiceData.related_sales_orders && invoiceData.related_sales_orders.length) || (invoiceData.related_delivery_notes && invoiceData.related_delivery_notes.length)" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Related Sales Orders -->
                    <div v-if="invoiceData.related_sales_orders && invoiceData.related_sales_orders.length">
                        <h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                            <svg class="w-4 h-4 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            {{ __('Related Sales Orders') }}
                        </h4>
                        <div class="flex flex-col gap-2">
                            <div
                                v-for="so in invoiceData.related_sales_orders"
                                :key="so"
                                class="flex justify-between items-center p-3 bg-white border border-gray-200 rounded-lg shadow-sm"
                            >
                                <span class="text-sm font-medium text-gray-900">{{ so }}</span>
                                <Button
                                    size="sm"
                                    variant="subtle"
                                    @click="openDocument({ voucher_type: 'Sales Order', voucher_no: so })"
                                >
                                    {{ __('View') }}
                                </Button>
                            </div>
                        </div>
                    </div>

                    <!-- Related Delivery Notes -->
                    <div v-if="invoiceData.related_delivery_notes && invoiceData.related_delivery_notes.length">
                        <h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                            <svg class="w-4 h-4 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0"/>
                            </svg>
                            {{ __('Related Delivery Notes') }}
                        </h4>
                        <div class="flex flex-col gap-2">
                            <div
                                v-for="dn in invoiceData.related_delivery_notes"
                                :key="dn"
                                class="flex justify-between items-center p-3 bg-white border border-gray-200 rounded-lg shadow-sm"
                            >
                                <span class="text-sm font-medium text-gray-900">{{ dn }}</span>
                                <Button
                                    size="sm"
                                    variant="subtle"
                                    @click="openDocument({ voucher_type: 'Delivery Note', voucher_no: dn })"
                                >
                                    {{ __('View') }}
                                </Button>
                            </div>
                        </div>
                    </div>
                 </div>

				<!-- Additional Info -->
				<div v-if="invoiceData.remarks" class="bg-gray-50 p-4 rounded-lg border border-gray-200">
					<h4 class="text-sm font-semibold text-gray-700 mb-2 text-start">{{ __('Remarks') }}</h4>
					<p class="text-sm text-gray-600 text-start">{{ invoiceData.remarks }}</p>
				</div>
			</div>

			<div v-else class="text-center py-12">
				<svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
				</svg>
				<p class="mt-2 text-sm text-gray-500">{{ __('Failed to load invoice details') }}</p>
			</div>
		</template>
		<template #actions>
			<div class="flex justify-end w-full">
				<Button variant="subtle" @click="show = false">
					{{ __('Close') }}
				</Button>
			</div>
		</template>

	</Dialog>
</template>

<script setup>
import { useFormatters } from "@/composables/useFormatters"
import { formatCurrency as formatCurrencyUtil } from "@/utils/currency"
import { printPaymentReceipt } from "@/utils/printInvoice"
import { getInvoiceStatusColor } from "@/utils/invoice"
import { logger } from "@/utils/logger"
import { Button, Dialog, call, FeatherIcon, Dropdown } from "frappe-ui"
import { ref, watch, nextTick, computed } from "vue"
import { usePOSSettingsStore } from "@/stores/posSettings"
import { usePOSCartStore } from "@/stores/posCart"
import { useToast } from "@/composables/useToast"

const settingsStore = usePOSSettingsStore()
const cartStore = usePOSCartStore()
const allowReturn = computed(() => settingsStore.allowReturn)
const allowDeliveryNote = computed(() => settingsStore.enableDeliveryNote)

const { showSuccess, showError } = useToast()
const log = logger.create('InvoiceDetailDialog')
const { formatDate, formatTime } = useFormatters()

const props = defineProps({
	modelValue: Boolean,
	invoiceName: String,
	posProfile: String,
	currency: {
		type: String,
		default: "USD",
	},
})

function formatCurrency(amount) {
	return formatCurrencyUtil(Number.parseFloat(amount || 0), props.currency)
}

const emit = defineEmits(["update:modelValue", "print-invoice", "make-payment", "return-invoice", "open-invoice", "open-sales-order", "open-delivery-note"])

function handlePayment() {
    if (!invoiceData.value) return
    emit("make-payment", invoiceData.value)
    show.value = false
}

function handleReturn() {
    if (!invoiceData.value) return
    emit("return-invoice", invoiceData.value)
    show.value = false
}

const show = ref(props.modelValue)
const loading = ref(false)
const invoiceData = ref(null)



// Computed: Check if this is a credit sale (Pay on Account - no payments, full outstanding)
const isCreditSale = computed(() => {
	if (!invoiceData.value) return false
	// Credit sale if no payments array or empty array
	const hasNoPayments = !invoiceData.value.payments || invoiceData.value.payments.length === 0
	if (hasNoPayments) return true

	// Also check if total paid is zero compared to grand total
	const totalPaid = invoiceData.value.payments?.reduce((sum, p) => sum + Math.abs(p.amount || 0), 0) || 0
	const grandTotal = Math.abs(invoiceData.value.grand_total || 0)
	const outstanding = Math.abs(invoiceData.value.outstanding_amount || 0)

	// Credit sale if total paid is near zero and outstanding is near grand total
	return totalPaid < 0.01 && Math.abs(outstanding - grandTotal) < 0.01
})

// Computed: Check if this is a credit sale return (return with no payments)
const isCreditSaleReturn = computed(() => {
	if (!invoiceData.value || !invoiceData.value.is_return) return false
	const hasNoPayments = !invoiceData.value.payments || invoiceData.value.payments.length === 0
	const totalPaid = invoiceData.value.payments?.reduce((sum, p) => sum + Math.abs(p.amount || 0), 0) || 0
	return hasNoPayments || totalPaid < 0.01
})

const paymentsList = computed(() => {
	if (!invoiceData.value || !invoiceData.value.payments) return []
	return invoiceData.value.payments.filter(p => !p.voucher_type || p.voucher_type === 'Payment Entry')
})

const returnsList = computed(() => {
	if (!invoiceData.value || !invoiceData.value.payments) return []
	return invoiceData.value.payments.filter(p => p.voucher_type === 'Sales Invoice')
})

watch(
	() => props.modelValue,
	(val) => {
		show.value = val
		if (val && props.invoiceName) {
			loadInvoiceDetails()
		}
	},
)

watch(
	() => props.invoiceName,
	(val) => {
		if (val && show.value) {
			loadInvoiceDetails()
		}
	}
)

watch(show, async (val) => {
	emit("update:modelValue", val)
	if (!val) {
		// Clear data when closing
		invoiceData.value = null
	} else {
		// Ensure dialog appears above other dialogs
		await nextTick()
		const dialogs = document.querySelectorAll('.modal-container, .modal-backdrop')
		dialogs.forEach(dialog => {
			const title = dialog.querySelector('[class*="title"]')
			if (title && title.textContent?.includes('Invoice Details')) {
				dialog.style.zIndex = '400'
			}
		})
	}
})

async function loadInvoiceDetails() {
	if (!props.invoiceName) return

	loading.value = true
	try {
		const result = await call("pos_next.api.invoices.get_invoice", {
			invoice_name: props.invoiceName,
		})

		// Map server 'qty' to 'quantity' for internal consistency
		if (result && result.items) {
			result.items = result.items.map((item) => ({
				...item,
				quantity: item.qty,
			}))
		}
		invoiceData.value = result
	} catch (error) {
		log.error("Error loading invoice details:", error)
		invoiceData.value = null
	} finally {
		loading.value = false
	}
}

function handlePrint() {
	if (!invoiceData.value) return
	emit("print-invoice", invoiceData.value)
}

async function handlePrintReceipt(payment) {
	try {
		await printPaymentReceipt(payment)
	} catch (error) {
		log.error("Error calling printPaymentReceipt:", error)
	}
}

async function handleCreateDeliveryNote() {
    if (!invoiceData.value) return
    try {
        const mappedDoc = await call("pos_next.api.delivery_notes.make_delivery_note_from_invoice", {
            source_name: invoiceData.value.name
        })

        // Clear existing cart
        cartStore.clearCart()
        
        // Set target doctype to Delivery Note
        cartStore.setTargetDoctype('Delivery Note')

        // Set customer
        if (mappedDoc.customer) {
            cartStore.setCustomer({
                name: mappedDoc.customer,
                customer_name: mappedDoc.customer_name || mappedDoc.customer
            })
        }

        // Add items to cart
        if (mappedDoc.items && mappedDoc.items.length) {
            mappedDoc.items.forEach(item => {
                cartStore.addItem({
                    item_code: item.item_code,
                    item_name: item.item_name,
                    description: item.description,
                    uom: item.uom,
                    rate: item.rate,
                    price_list_rate: item.price_list_rate || item.rate,
                    is_stock_item: item.is_stock_item,
                    stock_uom: item.stock_uom,
                    conversion_factor: item.conversion_factor,
                    item_group: item.item_group,
                    description: item.description,
                    discount_percentage: item.discount_percentage,
                    discount_amount: item.discount_amount,
                    // Reference fields
                    sales_order: item.sales_order,
                    against_sales_order: item.against_sales_order,
                    so_detail: item.so_detail,
                    against_sales_invoice: item.against_sales_invoice,
                    si_detail: item.si_detail,
                    dn_detail: item.dn_detail,
                }, item.qty)
            })
        }

        showSuccess(__("Delivery Note prepared in Cart"))
        show.value = false
    } catch (error) {
        console.error(error)
        showError(error.message || __("Failed to prepare delivery note"))
    }
}

function openDocument(payment) {
    if (!payment.voucher_type || !payment.voucher_no) return

    if (payment.voucher_type === 'Sales Invoice') {
        emit('open-invoice', payment.voucher_no)
    } else if (payment.voucher_type === 'Sales Order') {
        emit('open-sales-order', payment.voucher_no)
    } else if (payment.voucher_type === 'Delivery Note') {
        emit('open-delivery-note', payment.voucher_no)
    } else {
        // Convert DocType to slug (e.g., "Payment Entry" -> "payment-entry")
        const slug = payment.voucher_type.toLowerCase().trim().replace(/\s+/g, '-')
        const url = `/app/${slug}/${payment.voucher_no}`
        window.open(url, '_blank')
    }
}
</script>

