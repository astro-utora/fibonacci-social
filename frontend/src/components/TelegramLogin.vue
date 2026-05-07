<template>
  <v-container>
    <!-- Show Welcome/Login screen for non-authenticated users -->
    <v-row justify="center">
      <v-col cols="12" md="8">
        <!-- Loading State -->
        <v-card v-if="isLoading" class="mt-4">
          <v-card-text class="text-center">
            <v-progress-circular indeterminate color="primary" class="ma-4"></v-progress-circular>
            <div>Loading invitation data...</div>
          </v-card-text>
        </v-card>

        <!-- Invitation Preview -->
        <template v-else-if="invitationData">
          <UserProfile 
            :profile-data="invitationData"
            title="Complete Registration"
            :editable="false"
          />
          
          <v-card class="mt-4">
            <v-card-text class="text-center">
              <p class="mb-4">All information has been pre-filled from your invitation.</p>
              <v-btn
                color="primary"
                size="large"
                @click="loginWithTelegram(invitationId)"
              >
                Register with Telegram
              </v-btn>
            </v-card-text>
          </v-card>
        </template>

        <!-- Regular Login -->
        <template v-else>
          <!-- Error Alert -->
          <v-alert
            v-if="errorMessage"
            :type="errorType"
            variant="tonal"
            closable
            class="mb-4"
            @click:close="clearError"
          >
            <template v-if="route.query.error === 'not_registered'">
              {{ errorMessage }}
              <div class="mt-2">
                <v-btn
                  color="primary"
                  :href="botStartLink"
                  target="_blank"
                  prepend-icon="mdi-telegram"
                  class="mt-2"
                >
                  Register Now
                </v-btn>
              </div>
            </template>
            <template v-else>
              {{ errorMessage }}
            </template>
          </v-alert>

          <v-card class="mt-4">
            <v-card-title class="text-h4 text-center">
              Welcome to Fibonacci Social
            </v-card-title>
            
            <v-card-text class="text-center">
              <v-row justify="center">
                <v-col cols="12">
                  <p class="text-h6 mb-4">
                    New to Fibonacci Social?
                  </p>
                  <v-btn
                    color="primary"
                    size="large"
                    block
                    :href="botStartLink"
                    target="_blank"
                    prepend-icon="mdi-telegram"
                    class="mb-8"
                  >
                    Register with Bot
                  </v-btn>
                  
                  <p class="text-h6 mb-4">
                    Already have an account?
                  </p>
                  <v-btn
                    color="secondary"
                    size="large"
                    block
                    @click="loginWithTelegram()"
                    prepend-icon="mdi-login"
                  >
                    Login with Telegram
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </template>
      </v-col>
    </v-row>
  </v-container>
</template>
<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import UserProfile from './UserProfile.vue'
import { loginWithTelegram } from '@/utils/auth'
import { useRouter, useRoute } from 'vue-router'
import api from '@/utils/axios'

const router = useRouter()
const route = useRoute()
const errorMessage = ref('')
const isLoading = ref(false)
const invitationData = ref(null)

const invitationId = computed(() => route.query.invitation as string)
const referralId = computed(() => route.query.ref as string)

const botStartLink = computed(() => {
  if (referralId.value) {
    return `https://t.me/fibonacci_welcome_bot?start=ref_${referralId.value}`
    // return `https://t.me/stask_local_dev_bot?start=ref_${referralId.value}`
  }
  return `https://t.me/fibonacci_welcome_bot`
})

const errorType = computed(() => {
  return route.query.error === 'not_registered' ? 'info' : 'error'
})

const errorMessages = {
  'no_auth_data': 'Authentication data not received from Telegram',
  'invalid_data': 'Invalid authentication data received',
  'auth_failed': 'Authentication failed. Please try again',
  'decode_error': 'Error processing authentication data',
  'process_error': 'Error during authentication process',
  'network_error': 'Network error occurred during authentication',
  'not_registered': 'Please register first before logging in',
  'invitation_used': 'This invitation has already been used or is invalid',
  'invitation_error': 'Error processing invitation. Please try again'
}

const clearError = () => {
  errorMessage.value = ''
  // Remove error from URL without triggering a navigation
  const newQuery = { ...route.query }
  delete newQuery.error
  router.replace({ query: newQuery })
}

onMounted(async () => {
  // Check for error parameter in URL
  const error = route.query.error as keyof typeof errorMessages
  if (error && errorMessages[error]) {
    errorMessage.value = errorMessages[error]
  }

  const invitationId = route.query.invitation
  if (invitationId) {
    isLoading.value = true
    try {
      const response = await api.get(`/api/invitations/${invitationId}`)
      invitationData.value = response.data
    } catch (error) {
      console.error('Error loading invitation:', error)
    } finally {
      isLoading.value = false
    }
  }
})

</script>