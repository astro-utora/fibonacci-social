<template>
  <v-card class="mx-auto" max-width="400">
    <v-card-title class="text-center">Welcome</v-card-title>
    <v-card-text>
      <div class="text-center">
        <!-- Show loader while script is loading -->
        <div v-if="isScriptLoading" class="d-flex justify-center align-center py-4">
          <v-progress-circular
            indeterminate
            color="primary"
          ></v-progress-circular>
          <span class="ml-2">Loading Google Sign-In...</span>
        </div>
        
        <!-- Show error if script failed to load -->
        <v-alert
          v-else-if="scriptError"
          type="error"
          class="mb-4"
        >
          Failed to load Google Sign-In. Please try again later.
        </v-alert>

        <!-- Container for Google Sign-In button -->
        <div v-show="!isScriptLoading && !scriptError" ref="googleButtonRef"></div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import type { CredentialResponse } from '@/types/google'
import { isProfileComplete } from '@/utils/user'
import { $isAuthenticated, setToken, setUser } from '@/stores/auth'


const route = useRoute()
const router = useRouter()
const isLoading = ref(false)
const isScriptLoading = ref(true)
const scriptError = ref(false)
const googleButtonRef = ref<HTMLElement | null>(null)
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

// Function to load Google script
const loadGoogleScript = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    // Check if script is already loaded
    if (document.querySelector('script#google-signin')) {
      resolve()
      return
    }

    const script = document.createElement('script')
    script.id = 'google-signin'
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    script.onload = () => resolve()
    script.onerror = (e) => reject(e)
    document.head.appendChild(script)
  })
}

// Type is now globally available
const handleCredentialResponse = async (response: CredentialResponse) => {
  try {
    isLoading.value = true
    const { data } = await axios.post('/api/auth/google', {
      token: response.credential,
      invitation_id: route.query.invitation
    })

    if (data.success) {
      setToken(data.token)
      setUser(data.user)

      // Only redirect to profile if needed
      if (!isProfileComplete(data.user)) {
        router.push('/profile')
      }
    }
  } catch (error) {
    console.error('Google login error:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  try {
    isScriptLoading.value = true
    scriptError.value = false

    // Load Google script
    await loadGoogleScript()

    // Initialize Google Identity Services
    window.google.accounts.id.initialize({
      client_id: googleClientId,
      callback: handleCredentialResponse,
      auto_select: false,
      cancel_on_tap_outside: true
    })

    // Render the Google Sign-In button
    if (googleButtonRef.value) {
      window.google.accounts.id.renderButton(googleButtonRef.value, {
        type: 'standard',
        theme: 'outline',
        size: 'large',
        text: 'signin_with',
        shape: 'rectangular',
        logo_alignment: 'left'
      })
    }
  } catch (error) {
    console.error('Failed to load Google Sign-In:', error)
    scriptError.value = true
  } finally {
    isScriptLoading.value = false
  }
})
</script>

<style scoped>
.g_id_signin {
  margin-top: 1rem;
}
</style> 