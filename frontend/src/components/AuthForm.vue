<template>
  <!-- Loading State -->
  <v-card v-if="isLoadingInvitation" class="mt-4">
    <v-card-text class="text-center">
      <v-progress-circular indeterminate color="primary" class="ma-4"></v-progress-circular>
      <div>Loading invitation data...</div>
    </v-card-text>
  </v-card>

  <!-- Invitation Preview -->
  <template v-else-if="invitationData">
    <div class="d-flex justify-center">
      <UserProfile 
        :profile-data="invitationData"
        title="Complete Registration"
        :preview="true"
      />
    </div>
    
    <v-card class="mx-auto mt-4" max-width="400">
      <v-card-text class="text-center">
        <p class="mb-4">All information has been pre-filled from your invitation.</p>
        <EmailPasswordForm
          :show-password-confirmation="true"
          submit-text="Register with email"
          :loading="isLoading"
          :error="error"
          @submit="handleInvitation"
        />
      </v-card-text>
    </v-card>
  </template>  
  <v-card v-else class="mx-auto" max-width="400">
    <v-tabs v-model="activeTab">
      <v-tab value="login">Login</v-tab>
      <v-tab value="register">Register</v-tab>
    </v-tabs>

    <v-card-text>
      <EmailPasswordForm
        :show-password-confirmation="activeTab === 'register'"
        :submit-text="activeTab === 'login' ? 'Login' : 'Register'"
        :loading="isLoading"
        :error="error"
        @submit="handleSubmit"
      />
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
// @ts-ignore - Suppressing TS errors for Vue composition API imports
import { ref, computed, onMounted } from 'vue'
import EmailPasswordForm from '@/components/EmailPasswordForm.vue'
import UserProfile from '@/components/UserProfile.vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { useStore } from 'effector-vue/composition'
import { $isAuthenticated, setToken, setUser } from '@/stores/auth'
import { setLoginEmail } from '@/stores/loginEmail'
import { isProfileComplete } from '@/utils/user'
import api from '@/utils/axios'

const router = useRouter()
const route = useRoute()
const form = ref<any>(null)
const activeTab = ref('login')
const isLoading = ref(false)
const error = ref('')
const isLoadingInvitation = ref(false)
const invitationData = ref(null)

const invitationId = computed(() => route.query.invitation as string)
const referralId = computed(() => route.query.ref as string)
const paymentParam = computed(() => route.query.payment as string)

const formData = ref({
  email: '',
  password: '',
  confirmPassword: ''
})

const rules = {
  required: (v: string) => !!v || 'Field is required',
  email: (v: string) => /.+@.+\..+/.test(v) || 'Invalid email',
  password: (v: string) => v.length >= 8 || 'Password must be at least 8 characters',
  confirmPassword: (v: string) => v === formData.value.password || 'Passwords must match'
}

const isAuthenticated = useStore($isAuthenticated)

onMounted(async () => {
  if (invitationId.value) {
    isLoadingInvitation.value = true
    try {
      const response = await api.get(`/api/invitations/${invitationId.value}`)
      invitationData.value = response.data
    } catch (error) {
      console.error('Error loading invitation:', error)
    } finally {
      isLoadingInvitation.value = false
    }
  }
})

async function handleInvitation(formData: any) {
  try {
    isLoading.value = true
    error.value = ''
    
    const { data } = await axios.post('/api/auth/register', {
      email: formData.email,
      password: formData.password,
      invitation_id: invitationId.value,
    })

    if (data.success) {
      // Save the email to the store after successful registration
      setLoginEmail(formData.email)
      
      setToken(data.token)
      setUser(data.user)
      
      // Redirect based on profile completion
      if (!isProfileComplete(data.user)) {
        router.push({
          path: '/onboarding',
          query: paymentParam.value ? { payment: paymentParam.value } : {}
        })
      }
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'An error occurred'
  } finally {
    isLoading.value = false
  }
}

async function handleSubmit(formData: any) {
  try {
    isLoading.value = true
    error.value = ''

    const endpoint = activeTab.value === 'login' ? '/api/auth/login' : '/api/auth/register'
    const { data } = await axios.post(endpoint, {
      email: formData.email,
      password: formData.password,
      invitation_id: route.query.invitation,
      referral: activeTab.value === 'register' ? referralId.value : null
    })

    if (data.success) {
      // Save the email to the store after successful login/registration
      setLoginEmail(formData.email)
      
      setToken(data.token)
      setUser(data.user)

      // Only redirect to profile if needed
      if (!isProfileComplete(data.user)) {
        router.push({
          path: '/onboarding',
          query: paymentParam.value ? { payment: paymentParam.value } : {}
        })
      }
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'An error occurred'
  } finally {
    isLoading.value = false
  }
}
</script> 