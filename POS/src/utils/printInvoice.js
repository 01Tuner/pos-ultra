import { usePOSSettingsStore } from "@/stores/posSettings"
import { call } from "@/utils/apiWrapper"
import { logger } from "@/utils/logger"
import { isAndroid } from "@/utils/device"

const log = logger.create('PrintInvoice')

/**
 * Opens an HTML string as a Blob URL in a new tab.
 * Used on mobile (iOS/Android) where window.print() is unreliable.
 */
function openHtmlBlob(html) {
	const blob = new Blob([html], { type: 'text/html' })
	const blobUrl = URL.createObjectURL(blob)
	const win = window.open(blobUrl, '_blank')
	if (win) {
		win.onload = () => URL.revokeObjectURL(blobUrl)
	} else {
		// Popup blocked — fall back to download
		const a = document.createElement('a')
		a.href = blobUrl
		a.download = 'receipt.html'
		document.body.appendChild(a)
		a.click()
		document.body.removeChild(a)
		setTimeout(() => URL.revokeObjectURL(blobUrl), 1000)
	}
}

/**
 * Fetches Frappe's PDF download endpoint and opens the result as a Blob URL.
 * Falls back to fetching the /printview HTML and opening as an HTML blob when
 * the PDF generation fails (e.g. wkhtmltopdf broken image links error).
 * Used on mobile (iOS/Android) where window.print() is unreliable.
 */
async function openFrappePdfBlob(urlParams) {
	try {
		const pdfUrl = `/api/method/frappe.utils.print_format.download_pdf?${urlParams}`
		const response = await fetch(pdfUrl, { credentials: 'same-origin' })
		if (!response.ok) throw new Error(`PDF fetch failed: ${response.status}`)

		const blob = await response.blob()
		const blobUrl = URL.createObjectURL(blob)
		const win = window.open(blobUrl, '_blank')
		if (win) {
			win.addEventListener('load', () => setTimeout(() => URL.revokeObjectURL(blobUrl), 30000))
		} else {
			// Popup blocked — trigger download instead
			const a = document.createElement('a')
			a.href = blobUrl
			a.download = 'document.pdf'
			document.body.appendChild(a)
			a.click()
			document.body.removeChild(a)
			setTimeout(() => URL.revokeObjectURL(blobUrl), 1000)
		}
	} catch (err) {
		// PDF generation failed (e.g. broken image links in wkhtmltopdf).
		// Fall back to fetching the printview HTML and opening as an HTML blob.
		log.warn('PDF blob failed, falling back to printview HTML:', err)
		await openFrappeHtmlBlob(urlParams)
	}
}

/**
 * Fetches Frappe's /printview HTML and opens it as an HTML blob with a print button.
 * Used as fallback when server-side PDF generation fails.
 */
async function openFrappeHtmlBlob(urlParams) {
	const htmlUrl = `/printview?${urlParams}`
	const response = await fetch(htmlUrl, { credentials: 'same-origin' })
	if (!response.ok) throw new Error(`Printview fetch failed: ${response.status}`)
	let html = await response.text()

	// Fix relative URLs so stylesheets/images resolve correctly from a blob origin
	html = html.replace('<head>', `<head><base href="${window.location.origin}">`)

	openHtmlBlob(html)
}

/**
 * Fetches Frappe's /printview HTML and returns the HTML string.
 * Adds a <base href> tag so relative URLs resolve correctly.
 * Used as a building block for client-side PDF generation on mobile.
 */
async function fetchFrappeHtml(urlParams) {
	const htmlUrl = `/printview?${urlParams}`
	const response = await fetch(htmlUrl, { credentials: 'same-origin' })
	if (!response.ok) throw new Error(`Printview fetch failed: ${response.status}`)
	let html = await response.text()
	html = html.replace('<head>', `<head><base href="${window.location.origin}">`)
	return html
}

/**
 * Renders an HTML string to a PDF using jsPDF + html2canvas and opens it in a new tab.
 * The HTML is loaded into a hidden off-screen iframe so the full document (styles,
 * fonts, images) renders correctly before the canvas screenshot is taken.
 * Falls back to openHtmlBlob if rendering fails.
 *
 * @param {string} htmlString - Full HTML document string to render
 * @param {string} filename   - PDF filename for the download fallback (default: 'document.pdf')
 * @param {number} iframeWidth - Iframe render width in px: 794 for A4, 302 for 80mm thermal
 */
export async function openAsPdf(htmlString, filename = 'document.pdf', iframeWidth = 794) {
	try {
		const { jsPDF } = await import('jspdf')
		const html2canvas = (await import('html2canvas')).default

		// Render the full HTML document in a hidden off-screen iframe
		const iframe = document.createElement('iframe')
		iframe.style.cssText = `position:fixed;top:-9999px;left:-9999px;width:${iframeWidth}px;height:1123px;border:none;visibility:hidden;`
		document.body.appendChild(iframe)

		// Inject style to hide UI-only elements before rendering
		const printHtml = htmlString.replace('</head>', `<style>.action-banner{display:none!important}</style></head>`)

		await new Promise((resolve, reject) => {
			iframe.onload = resolve
			iframe.onerror = reject
			iframe.contentDocument.open()
			iframe.contentDocument.write(printHtml)
			iframe.contentDocument.close()
		})

		// Strip print-format-gutter class so its padding/margin doesn't affect the PDF
		iframe.contentDocument.querySelectorAll('.print-format-gutter')
			.forEach(el => el.classList.remove('print-format-gutter'))

		// Allow fonts/images to settle
		await new Promise(r => setTimeout(r, 500))

		const element = iframe.contentDocument.body
		const canvas = await html2canvas(element, {
			scale: 2,
			useCORS: true,
			allowTaint: true,
			logging: false,
			windowWidth: iframeWidth,
		})

		document.body.removeChild(iframe)

		const imgData = canvas.toDataURL('image/png')
		const pdf = new jsPDF({
			orientation: 'portrait',
			unit: 'px',
			format: [canvas.width, canvas.height],
		})
		pdf.addImage(imgData, 'PNG', 0, 0, canvas.width, canvas.height)

		// Explicitly set application/pdf MIME type so Android Chrome opens in PDF viewer
		const blob = new Blob([pdf.output('arraybuffer')], { type: 'application/pdf' })
		const blobUrl = URL.createObjectURL(blob)

		if (isAndroid()) {
			// On Android, window.open() is blocked in async context (not a direct user gesture).
			// Using <a> without a `download` attribute lets Chrome handle the MIME type and
			// open the PDF in the built-in viewer instead of forcing a file save.
			const a = document.createElement('a')
			a.href = blobUrl
			a.target = '_blank'
			a.rel = 'noopener'
			document.body.appendChild(a)
			a.click()
			document.body.removeChild(a)
			setTimeout(() => URL.revokeObjectURL(blobUrl), 30000)
		} else {
			const win = window.open(blobUrl, '_blank')
			if (win) {
				win.addEventListener('load', () => setTimeout(() => URL.revokeObjectURL(blobUrl), 30000))
			} else {
				// Popup blocked — fall back to download
				const a = document.createElement('a')
				a.href = blobUrl
				a.download = filename
				document.body.appendChild(a)
				a.click()
				document.body.removeChild(a)
				setTimeout(() => URL.revokeObjectURL(blobUrl), 1000)
			}
		}
	} catch (err) {
		log.warn('jsPDF/html2canvas failed, falling back to HTML blob:', err)
		openHtmlBlob(htmlString)
	}
}

/**
* Print invoice using Frappe's print format system
* @param {Object} invoiceData - The invoice document data
* @param {string} printFormat - The print format name (optional)
* @param {string} letterhead - The letterhead name (optional)
* @note Use "POS Next Receipt" format for thermal printer (80mm) or configure via POS Profile
*/
export async function printInvoice(
	invoiceData,
	printFormat = null,
	letterhead = null,
) {
	try {
		if (!invoiceData || !invoiceData.name) {
			throw new Error("Invalid invoice data")
		}

		const doctype = invoiceData.doctype || "Sales Invoice"

		const params = new URLSearchParams({
			doctype: doctype,
			name: invoiceData.name,
			no_letterhead: letterhead ? 0 : 1,
			_lang: "en",
			_t: Date.now(),
		})

		if (printFormat) {
			params.append("format", printFormat)
		}

		if (letterhead) {
			params.append("letterhead", letterhead)
		}

		if (isAndroid()) {
			// Mobile (iOS/Android): generate PDF client-side — window.print() is unreliable
			const html = await fetchFrappeHtml(params.toString())
			await openAsPdf(html, `${invoiceData.name}.pdf`)
		} else {
			// Desktop: use Frappe's printview with trigger_print
			params.append("trigger_print", 1)
			const printUrl = `/printview?${params.toString()}`
			const printWindow = window.open(printUrl, "_blank", "width=800,height=600")
			if (!printWindow) throw new Error("Failed to open print window. Please check your popup blocker settings.")
			printWindow.addEventListener('afterprint', () => printWindow.close())
		}

		return true
	} catch (error) {
		log.error("Error printing with Frappe print format:", error)
		return printInvoiceCustom(invoiceData)
	}
}

/**
* Generates and prints a custom POS receipt using a thermal printer layout.
*
* This fallback printer is used when Frappe's standard print format is unavailable.
* The receipt is optimized for 80mm thermal printers with clean, readable formatting.
*
* Receipt Structure:
* - Header: Company name and invoice type
* - Info: Invoice number, date, customer, payment status
* - Items: Each item shows quantity × original price = subtotal
* - Discounts: Displayed as separate line items with negative amounts
* - Totals: Subtotal, tax, and grand total
* - Payments: Payment methods and amounts, change, outstanding balance
* - Footer: Thank you message and branding
*
* @param {Object} invoiceData - The invoice document data from ERPNext
* @param {string} invoiceData.name - Invoice number
* @param {string} invoiceData.company - Company name
* @param {Array} invoiceData.items - Invoice line items
* @param {Array} invoiceData.payments - Payment records
* @param {number} invoiceData.grand_total - Invoice total amount
*/
export async function printInvoiceCustom(invoiceData) {
	const printContent = `
<!DOCTYPE html>
<html>
		<head>
			<meta charset="UTF-8">
			<title>${__('Invoice - {0}', [invoiceData.name])}</title>
			<style>
				* {
					margin: 0;
					padding: 0;
					box-sizing: border-box;
				}

				body {
					font-family: 'Courier New', monospace;
					padding: 10px;
					width: 80mm;
					margin: 0;
					max-width: 80mm;
					font-weight: bold;
					color: black;
				}

				.receipt {
					width: 100%;
				}

				.header {
					text-align: center;
					margin-bottom: 20px;
					border-bottom: 2px dashed #000;
					padding-bottom: 10px;
				}

				.company-name {
					font-size: 18px;
					font-weight: bold;
					margin-bottom: 5px;
				}

				.invoice-info {
					margin-bottom: 15px;
					font-size: 12px;
				}

				.invoice-info div {
					display: flex;
					justify-content: space-between;
					margin-bottom: 3px;
				}

				.partial-status {
					color: #000;
					font-weight: bold;
					margin-bottom: 5px;
				}

				.items-table {
					width: 100%;
					margin-bottom: 15px;
					border-top: 1px dashed #000;
					border-bottom: 1px dashed #000;
					padding: 10px 0;
				}

				.item-row {
					margin-bottom: 10px;
					font-size: 12px;
				}

				.item-name {
					font-weight: bold;
					margin-bottom: 3px;
				}

				.item-details {
					display: flex;
					justify-content: space-between;
					font-size: 11px;
					color: #000;
				}

				.item-discount {
					display: flex;
					justify-content: space-between;
					font-size: 10px;
					color: #000;
					margin-top: 2px;
				}

				.item-serials {
					font-size: 9px;
					color: #000;
					margin-top: 3px;
					padding: 3px 5px;
					background-color: #fff;
					border: 1px dashed #000;
					border-radius: 2px;
				}

				.item-serials-label {
					font-weight: bold;
					margin-bottom: 2px;
				}

				.item-serials-list {
					word-break: break-all;
				}

				.totals {
					margin-top: 15px;
					border-top: 1px dashed #000;
					padding-top: 10px;
				}

				.total-row {
					display: flex;
					justify-content: space-between;
					margin-bottom: 5px;
					font-size: 12px;
				}

				.grand-total {
					font-size: 16px;
					font-weight: bold;
					border-top: 2px solid #000;
					padding-top: 10px;
					margin-top: 10px;
				}

				.payments {
					margin-top: 15px;
					border-top: 1px dashed #000;
					padding-top: 10px;
				}

				.payment-row {
					display: flex;
					justify-content: space-between;
					margin-bottom: 3px;
					font-size: 11px;
				}

				.total-paid {
					font-weight: bold;
					border-top: 1px solid #000;
					padding-top: 5px;
					margin-top: 5px;
				}

				.outstanding-row {
					display: flex;
					justify-content: space-between;
					font-size: 13px;
					font-weight: bold;
					color: #000;
					background-color: #fff;
					border: 1px solid #000;
					padding: 8px;
					margin-top: 8px;
					border-radius: 4px;
				}

				.footer {
					text-align: center;
					margin-top: 20px;
					padding-top: 10px;
					border-top: 2px dashed #000;
					font-size: 11px;
				}

				@media print {
					@page {
						size: 80mm auto;
						margin: 0;
					}

					body {
						width: 80mm;
						padding: 5mm;
						margin: 0;
					}

					.no-print {
						display: none;
					}
				}
			</style>
		</head>
		<body>
			<div class="receipt">
				<!-- Header -->
				<div class="header">
					<div class="company-name">${invoiceData.company || "POS Next"}</div>
					<div style="font-size: 12px;">${__('TAX INVOICE')}</div>
				</div>

				<!-- Invoice Info -->
				<div class="invoice-info">
					<div>
						<span>${__('Invoice #:')}</span>
						<span><strong>${invoiceData.name}</strong></span>
					</div>
					<div>
						<span>${__('Date:')}</span>
						<span>${new Date(invoiceData.posting_date || Date.now()).toLocaleString()}</span>
					</div>
					${invoiceData.customer_name
			? `
					<div>
						<span>${__('Customer:')}</span>
						<span>${invoiceData.customer_name}</span>
					</div>
					`
			: ""
		}
					${(invoiceData.status === "Partly Paid" || (invoiceData.outstanding_amount && invoiceData.outstanding_amount > 0 && invoiceData.outstanding_amount < invoiceData.grand_total))
			? `
					<div class="partial-status">
						<span>${__('Status:')}</span>
						<span>${__('PARTIAL PAYMENT')}</span>
					</div>
					`
			: ""
		}
				</div>

				<!-- Items -->
				<div class="items-table">
					${invoiceData.items
			.map((item) => {
				// Determine if item has promotional pricing
				const hasItemDiscount =
					(item.discount_percentage &&
						Number.parseFloat(item.discount_percentage) > 0) ||
					(item.discount_amount &&
						Number.parseFloat(item.discount_amount) > 0)
				const isFree = item.is_free_item
				const qty = item.quantity || item.qty

				// Display original list price for transparency
				const displayRate = item.price_list_rate || item.rate
				// Calculate subtotal before any price reductions
				const subtotal = qty * displayRate

				return `
						<div class="item-row">
							<div class="item-name">
								${item.item_name || item.item_code} ${isFree ? __('(FREE)') : ""}
							</div>
							<div class="item-details">
								<span>${qty} × ${formatCurrency(displayRate)}</span>
								<span><strong>${formatCurrency(subtotal)}</strong></span>
							</div>
							${hasItemDiscount
						? `
							<div class="item-discount">
								<span>Discount ${item.discount_percentage ? `(${Number(item.discount_percentage).toFixed(2)}%)` : ""}</span>
								<span>-${formatCurrency(item.discount_amount || 0)}</span>
							</div>
							`
						: ""
					}
							${item.serial_no
						? `
							<div class="item-serials">
								<div class="item-serials-label">${__('Serial No:')}</div>
								<div class="item-serials-list">${item.serial_no.replace(/\n/g, ', ')}</div>
							</div>
							`
						: ""
					}
						</div>
						`
			})
			.join("")}
				</div>

				<!-- Totals -->
				<div class="totals">
					${invoiceData.total_taxes_and_charges &&
			invoiceData.total_taxes_and_charges > 0
			? `
					<div class="total-row">
						<span>${__('Subtotal:')}</span>
						<span>${formatCurrency((invoiceData.grand_total || 0) - (invoiceData.total_taxes_and_charges || 0))}</span>
					</div>
					<div class="total-row">
						<span>${__('Tax:')}</span>
						<span>${formatCurrency(invoiceData.total_taxes_and_charges)}</span>
					</div>
					`
			: ""
		}
					${invoiceData.discount_amount
			? `
					<div class="total-row" style="color: #28a745;">
						<span>Additional Discount${invoiceData.additional_discount_percentage ? ` (${Number(invoiceData.additional_discount_percentage).toFixed(1)}%)` : ""}:</span>
						<span>-${formatCurrency(Math.abs(invoiceData.discount_amount))}</span>
					</div>
					`
			: ""
		}
					<div class="total-row grand-total">
						<span>${__('TOTAL:')}</span>
						<span>${formatCurrency(invoiceData.grand_total)}</span>
					</div>
				</div>

				<!-- Payments -->
				${invoiceData.payments && invoiceData.payments.length > 0
			? `
				<div class="payments">
					<div style="font-weight: bold; margin-bottom: 5px; font-size: 12px;">Payments:</div>
					${invoiceData.payments
				.map(
					(payment) => `
						<div class="payment-row">
							<span>${payment.mode_of_payment}:</span>
							<span>${formatCurrency(payment.amount)}</span>
						</div>
					`,
				)
				.join("")}
					<div class="payment-row total-paid">
						<span>${__('Total Paid:')}</span>
						<span>${formatCurrency(invoiceData.paid_amount || 0)}</span>
					</div>
					${invoiceData.change_amount && invoiceData.change_amount > 0
				? `
					<div class="payment-row" style="font-weight: bold; margin-top: 5px;">
						<span>${__('Change:')}</span>
						<span>${formatCurrency(invoiceData.change_amount)}</span>
					</div>
					`
				: ""
			}
					${invoiceData.outstanding_amount && invoiceData.outstanding_amount > 0
				? `
					<div class="outstanding-row">
						<span>${__('BALANCE DUE:')}</span>
						<span>${formatCurrency(invoiceData.outstanding_amount)}</span>
					</div>
					`
				: ""
			}
				</div>
				`
			: ""
		}

				<!-- Footer -->
				<div class="footer">
					<div style="margin-bottom: 5px;">${__('Thank you for your business!')}</div>
					<div style="font-size: 10px;">Powered by <a href="https://nexus.brainwise.me" target="_blank" style="color: #3b82f6; text-decoration: none; font-weight: 600;">BrainWise</a></div>
				</div>
			</div>

		</body>
	</html>
`

	if (isAndroid()) {
		// Mobile (iOS/Android): generate PDF client-side using 80mm thermal format
		await openAsPdf(printContent, `${invoiceData.name}.pdf`, 302)
	} else {
		// Desktop: open a popup and auto-trigger window.print()
		const printWindow = window.open("", "_blank", "width=350,height=600")
		printWindow.document.write(printContent)
		printWindow.document.close()
		printWindow.onload = () => {
			setTimeout(() => printWindow.print(), 250)
		}
		printWindow.addEventListener('afterprint', () => printWindow.close())
	}
}

function formatCurrency(amount) {
	return Number.parseFloat(amount || 0).toFixed(2)
}

/**
* Print invoice by name, fetching print format from POS Profile
* @param {string} invoiceName - The name of the invoice to print
* @param {string} printFormat - Optional print format override
* @param {string} letterhead - Optional letterhead override
*/
export async function printInvoiceByName(
	invoiceName,
	printFormat = null,
	letterhead = null,
) {
	try {
		// Fetch the invoice document using proper POS API endpoint
		const invoiceDoc = await call("pos_next.api.invoices.get_invoice", {
			invoice_name: invoiceName,
		})

		if (!invoiceDoc) {
			throw new Error("Invoice not found")
		}

		// If no print format specified and invoice has a POS Profile, fetch its print settings
		if (!printFormat && invoiceDoc.pos_profile) {
			try {
				const posProfileDoc = await call("frappe.client.get", {
					doctype: "POS Profile",
					name: invoiceDoc.pos_profile,
				})

				if (posProfileDoc) {
					printFormat = posProfileDoc.print_format
					letterhead = letterhead || posProfileDoc.letter_head
				}
			} catch (error) {
				log.warn("Could not fetch POS Profile print settings:", error)
				// Continue with default print format
			}
		}

		// Fallback to POS Settings if POS Profile doesn't have a print format
		if (!printFormat) {
			try {
				const posSettings = usePOSSettingsStore()
				if (posSettings.customPrintFormat) {
					printFormat = posSettings.customPrintFormat
				}
			} catch (error) {
				log.warn("Could not fetch POS Settings print format:", error)
			}
		}

		// Print the invoice
		return await printInvoice(invoiceDoc, printFormat, letterhead)
	} catch (error) {
		log.error("Error fetching invoice for print:", error)
		throw error
	}
}

/**
* Print a payment receipt
* @param {Object} paymentData - The payment record with voucher_type and voucher_no
*/
export async function printPaymentReceipt(paymentData) {
	try {
		if (!paymentData || !paymentData.voucher_no) {
			throw new Error("Invalid payment data")
		}

		if (paymentData.voucher_type === "Payment Entry") {
			const params = new URLSearchParams({
				doctype: "Payment Entry",
				name: paymentData.voucher_no,
				format: "Standard",
				no_letterhead: 1,
				_lang: "en",
			})
			if (isAndroid()) {
				const html = await fetchFrappeHtml(params.toString())
				await openAsPdf(html, `${paymentData.voucher_no}.pdf`)
			} else {
				params.append("trigger_print", 1)
				const printUrl = `/printview?${params.toString()}`
				const printWindow = window.open(printUrl, "_blank", "width=800,height=600")
				if (!printWindow) throw new Error("Popup blocked")
				printWindow.addEventListener('afterprint', () => printWindow.close())
			}
		} else if (paymentData.voucher_type === "Sales Invoice") {
			await printInvoiceByName(paymentData.voucher_no)
		} else {
			throw new Error(`Unsupported voucher type: ${paymentData.voucher_type}`)
		}

		return true
	} catch (error) {
		log.error("Error printing payment receipt:", error)
		throw error
	}
}
/**
* Print Sales Order by name
* @param {string} orderName - The name of the sales order
*/
export async function printSalesOrderByName(orderName) {
	try {
		if (!orderName) {
			throw new Error("Sales Order name is required")
		}

		const params = new URLSearchParams({
			doctype: "Sales Order",
			name: orderName,
			no_letterhead: 0,
			_t: Date.now(),
		})

		if (isAndroid()) {
			const html = await fetchFrappeHtml(params.toString())
			await openAsPdf(html, `${orderName}.pdf`)
		} else {
			params.append("trigger_print", 1)
			const printUrl = `/printview?${params.toString()}`
			const printWindow = window.open(printUrl, 'pos_print_so', 'width=900,height=700,toolbar=0,scrollbars=1,status=0,resizable=1')
			if (!printWindow) throw new Error("Failed to open print window. Please check your popup blocker settings.")
			printWindow.addEventListener('afterprint', () => printWindow.close())
		}

		return true
	} catch (error) {
		log.error("Error printing Sales Order:", error)
		throw error
	}
}

/**
* Print Delivery Note by name
* @param {string} dnName - The name of the delivery note
*/
export async function printDeliveryNoteByName(dnName) {
	try {
		if (!dnName) {
			throw new Error("Delivery Note name is required")
		}

		const params = new URLSearchParams({
			doctype: "Delivery Note",
			name: dnName,
			no_letterhead: 0,
			_t: Date.now(),
		})

		if (isAndroid()) {
			const html = await fetchFrappeHtml(params.toString())
			await openAsPdf(html, `${dnName}.pdf`)
		} else {
			params.append("trigger_print", 1)
			const printUrl = `/printview?${params.toString()}`
			const printWindow = window.open(printUrl, 'pos_print_dn', 'width=900,height=700,toolbar=0,scrollbars=1,status=0,resizable=1')
			if (!printWindow) throw new Error("Failed to open print window. Please check your popup blocker settings.")
			printWindow.addEventListener('afterprint', () => printWindow.close())
		}

		return true
	} catch (error) {
		log.error("Error printing Delivery Note:", error)
		throw error
	}
}

/**
 * Print Payment Entry linked to a Sales Invoice.
 * Looks up the Payment Entry created for the POS invoice and opens its print view.
 * Falls back to printing the Sales Invoice if no Payment Entry is found.
 * @param {string} invoiceName - The Sales Invoice name
 */
export async function printPaymentEntryByInvoiceName(invoiceName) {
	try {
		if (!invoiceName) {
			throw new Error("Invoice name is required")
		}

		// Look up Payment Entry linked to this Sales Invoice
		const results = await call("frappe.client.get_list", {
			doctype: "Payment Entry",
			filters: [
				["Payment Entry Reference", "reference_name", "=", invoiceName],
				["Payment Entry Reference", "reference_doctype", "=", "Sales Invoice"],
			],
			fields: ["name"],
			limit: 1,
		})

		if (results && results.length > 0) {
			const paymentEntryName = results[0].name
			const params = new URLSearchParams({
				doctype: "Payment Entry",
				name: paymentEntryName,
				no_letterhead: 0,
				_t: Date.now(),
			})
			if (isAndroid()) {
				const html = await fetchFrappeHtml(params.toString())
				await openAsPdf(html, `${paymentEntryName}.pdf`)
			} else {
				params.append("trigger_print", 1)
				const printUrl = `/printview?${params.toString()}`
				const printWindow = window.open(printUrl, "_blank", "width=800,height=600")
				if (!printWindow) throw new Error("Popup blocked")
				printWindow.addEventListener('afterprint', () => printWindow.close())
			}
			return true
		}

		// No Payment Entry found — fall back to Sales Invoice print
		log.warn(`No Payment Entry found for ${invoiceName}, falling back to invoice print`)
		return await printInvoiceByName(invoiceName)
	} catch (error) {
		log.error("Error printing Payment Entry:", error)
		throw error
	}
}
