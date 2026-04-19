<template>
  <Dialog v-model="open" :options="{ title: selectedReport ? selectedReport.label : __('Reports'), size: selectedReport ? 'full' : 'lg' }">
    <template #body-content>
      <div v-if="!selectedReport" class="p-4">
        <p class="text-sm text-gray-500 mb-4">{{ __('Select a report to view') }}</p>
        <div class="flex flex-col gap-2">
          <button
            v-for="report in reports"
            :key="report.label"
            @click="openReport(report)"
            class="flex items-center justify-between p-3 rounded-lg border border-gray-100 hover:bg-gray-50 hover:border-gray-200 transition-all text-sm font-medium text-gray-700 hover:text-blue-600 w-full text-left"
          >
            <div class="flex items-center gap-3">
              <FeatherIcon :name="report.icon" class="w-4 h-4 text-gray-400 group-hover:text-blue-500" />
              <span>{{ report.label }}</span>
            </div>
            <FeatherIcon name="chevron-right" class="w-3.5 h-3.5 text-gray-300" />
          </button>
        </div>
      </div>
      <div v-else class="w-full flex-1 relative" style="min-height: 70vh;">
        <div v-if="reportLoading" class="absolute inset-0 flex flex-col items-center justify-center bg-white z-10">
          <LoadingIndicator class="w-8 h-8 text-blue-600 mb-2" />
          <p class="text-sm text-gray-500 font-medium">{{ __('Generating report...') }}</p>
        </div>
        <iframe :src="selectedReport.route" class="w-full h-full border-0" style="min-height: 70vh;" @load="injectIframeStyles"></iframe>
      </div>
    </template>
    <template #actions>
      <div class="flex gap-2 w-full">
        <Button v-if="selectedReport" variant="subtle" @click="selectedReport = null" class="w-full">
          {{ __('Back to Reports') }}
        </Button>
        <Button v-else variant="subtle" @click="open = false" class="w-full">
          {{ __('Close') }}
        </Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Dialog, Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { usePOSSettingsStore } from '@/stores/posSettings'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits(['update:modelValue'])

const selectedReport = ref(null)
const reportLoading = ref(false)

const open = computed({
  get: () => props.modelValue,
  set: (value) => {
    emit('update:modelValue', value)
  },
})

// Reset selected report when dialog is closed
watch(() => props.modelValue, (newVal) => {
  if (!newVal) {
    // Slight delay to not show the swap while closing animation is playing
    setTimeout(() => {
      selectedReport.value = null
      reportLoading.value = false
    }, 200)
  }
})

function openReport(report) {
  selectedReport.value = report
  reportLoading.value = true
  
  // Keep loader for 3 seconds as requested
  setTimeout(() => {
    reportLoading.value = false
  }, 3000)
}

function injectIframeStyles(event) {
  try {
    const iframeDocument = event.target.contentDocument || event.target.contentWindow.document
    if (!iframeDocument) return

    const styleId = 'pos-iframe-hacks'
    if (!iframeDocument.getElementById(styleId)) {
      const style = iframeDocument.createElement('style')
      style.id = styleId
      style.innerHTML = `
        #windows-style-menu, .title-area { display: none !important; }
        body .container { width: 100% !important; }
      `
      iframeDocument.head.appendChild(style)
    }
  } catch (error) {
    console.error('Failed to inject iframe styles', error)
  }
}

const settingsStore = usePOSSettingsStore()

function buildReportUrl(reportName, passPosProfile = true) {
  const base = `/app/query-report/${encodeURIComponent(reportName)}`
  const posProfile = settingsStore.settings.pos_profile
  if (posProfile && passPosProfile) {
    return `${base}?pos_profile=${encodeURIComponent(posProfile)}&embed=true`
  }
  return `${base}?embed=true`
}

const reports = computed(() => {
  const storeReports = settingsStore.reports
  if (storeReports && storeReports.length > 0) {
    // Map the POS Report child table rows to display format.
    // Each row has: report (Frappe report name) and label (optional display name).
    return storeReports.map((row) => ({
      label: row.label || row.report,
      route: buildReportUrl(row.report, row.pass_pos_profile !== 0),
      icon: 'bar-chart-2',
    }))
  }
  // Fallback to default reports when none are configured in POS Settings
  return [
    {
      label: __('Sales Register'),
      route: buildReportUrl('Sales Register', true),
      icon: 'file-text'
    },
    {
      label: __('Item-wise Sales Register'),
      route: buildReportUrl('Item-wise Sales Register', true),
      icon: 'package'
    },
    {
      label: __('POS Register'),
      route: buildReportUrl('POS Register', true),
      icon: 'list'
    }
  ]
})
</script>
