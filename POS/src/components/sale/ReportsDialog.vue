<template>
  <Dialog v-model="open" :options="{ title: __('Reports'), size: 'sm' }">
    <template #body-content>
      <div class="div p-4">
        <p class="text-sm text-gray-500 mb-4">{{ __('Select a report to open in ERPNext') }}</p>
        <div class="flex flex-col gap-2">
          <a
            v-for="report in reports"
            :key="report.label"
            :href="report.route"
            target="_blank"
            class="flex items-center justify-between p-3 rounded-lg border border-gray-100 hover:bg-gray-50 hover:border-gray-200 transition-all text-sm font-medium text-gray-700 hover:text-blue-600"
          >
            <div class="flex items-center gap-3">
              <FeatherIcon :name="report.icon" class="w-4 h-4 text-gray-400 group-hover:text-blue-500" />
              <span>{{ report.label }}</span>
            </div>
            <FeatherIcon name="external-link" class="w-3.5 h-3.5 text-gray-300" />
          </a>
        </div>
      </div>
    </template>
    <template #actions>
      <Button variant="subtle" @click="open = false" class="w-full">
        {{ __('Close') }}
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { computed } from 'vue'
import { Dialog, Button, FeatherIcon } from 'frappe-ui'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits(['update:modelValue'])

const open = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const reports = [
  {
    label: __('Sales Register'),
    route: '/app/query-report/Sales%20Register',
    icon: 'file-text'
  },
  {
    label: __('Item-wise Sales Register'),
    route: '/app/query-report/Item-wise%20Sales%20Register',
    icon: 'package'
  }
]
</script>
