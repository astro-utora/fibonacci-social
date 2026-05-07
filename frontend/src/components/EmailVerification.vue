<template>
  <v-card class="mx-auto" max-width="400">
    <v-card-title class="text-center">Email Verification</v-card-title>
    <v-card-text>
      <div v-if="isLoading" class="text-center">
        <v-progress-circular
          indeterminate
          color="primary"
        ></v-progress-circular>
        <p class="mt-2">Verifying your email...</p>
      </div>
      
      <v-alert
        v-else-if="error"
        type="error"
        class="mb-4"
      >
        {{ error }}
      </v-alert>
      
      <v-alert
        v-else
        type="success"
        class="mb-4"
      >
        Email verified successfully! You can now close this window.
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const isLoading = ref(true)
const error = ref('')

onMounted(async () => {
  const token = route.query.token as string
  
  if (!token) {
    error.value = 'Invalid verification link'
    isLoading.value = false
    return
  }

  try {
    await axios.get(`/api/auth/verify-email/${token}`)
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Verification failed'
  } finally {
    isLoading.value = false
  }
})
</script> 