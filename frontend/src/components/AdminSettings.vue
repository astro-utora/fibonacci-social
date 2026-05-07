<template>
  <div>
    <SettingsTable
      title="Admin Settings"
      :settings="settings || []"
      :loading="loading"
      :error="error"
      keyLabel="Setting"
      valueLabel="Value"
      descriptionLabel="Description"
      @refresh="loadSettings"
      @update="updateSetting"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useStore } from 'effector-vue/composition'
import { 
  $adminSettings, 
  fetchAdminSettingsFx, 
  updateAdminSettingFx 
} from '@/stores/adminSettings'
import type { AdminSetting, AdminSettingUpdate } from '@/types/admin'
import SettingsTable from './common/SettingsTable.vue'

const settings = useStore<AdminSetting[]>($adminSettings)
const loading = ref(false)
const error = ref('')

onMounted(() => {
  loadSettings()
})

async function loadSettings() {
  loading.value = true
  error.value = ''
  
  try {
    await fetchAdminSettingsFx()
  } catch (err: any) {
    error.value = err.message || 'Failed to load settings'
  } finally {
    loading.value = false
  }
}

async function updateSetting(key: string, data: AdminSettingUpdate) {
  try {
    await updateAdminSettingFx({ key, data })
  } catch (err: any) {
    error.value = err.message || 'Failed to update setting'
  }
}
</script> 