<template>
  <!-- Show Dashboard for authenticated users -->
  <Dashboard v-if="isAuthenticated" />
  <AuthForm v-else />
</template>

<script setup lang="ts">
import Dashboard from './Dashboard.vue'
import AuthForm from './AuthForm.vue'
import { useStore } from 'effector-vue/composition'
import { $isAuthenticated } from '@/stores/auth'
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/utils/axios'
import { $filloutOnboardingId } from '@/stores/adminSettings'

const filloutOnboardingId = useStore($filloutOnboardingId)
const isAuthenticated = useStore($isAuthenticated)
const route = useRoute()
const router = useRouter()

onMounted(async () => {
  if (isAuthenticated) {
    const filloutId = route.query.formId
  
    if (filloutId && typeof filloutId === 'string') {
      if (filloutId === filloutOnboardingId.value) {
        return
      }
      try {
        // Save fillout submission
        await api.post('/api/fillout/complete', {
          filloutId
        })
      } catch (error) {
        console.error('Failed to save fillout submission:', error)
      }
    }
  }
})
</script>