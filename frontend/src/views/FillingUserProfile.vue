<template>
  <v-card class="mx-auto" max-width="600">
    <v-card-title>Complete Your Profile</v-card-title>
    <UserProfileForm
      submit-text="Save Profile"
      :processing="isLoading"
      :processing-error="error"
      @submit="handleSubmit"
    />
  </v-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import UserProfileForm from '@/components/UserProfileForm.vue'
import { useRouter } from 'vue-router'
import api from '@/utils/axios'
import { updateProfileFx } from '@/stores/user'

const router = useRouter()
const isLoading = ref(false)
const error = ref('')

const handleSubmit = async (formData: any) => {
  try {
    isLoading.value = true
    error.value = ''

    const { data } = await api.post('/api/users/profile', formData)

    if (data.success) {
      await updateProfileFx(data.user)
      router.push('/dashboard')
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'An error occurred'
  } finally {
    isLoading.value = false
  }
}
</script> 