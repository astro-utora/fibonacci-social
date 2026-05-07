<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="6">
        <v-card class="mt-4">
          <v-card-text class="text-center">
            <v-progress-circular
              indeterminate
              color="primary"
            ></v-progress-circular>
            <p class="mt-4">Processing authentication...</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { loginWithTelegramFx } from '@/stores/user'
import { TelegramAuthData } from '@/types/telegram'

const router = useRouter()

function base64UrlDecode(str: string): string {
  // Convert Base64URL to Base64 by replacing URL-safe chars
  let base64 = str.replace(/-/g, '+').replace(/_/g, '/')
  // Add padding if needed
  const pad = base64.length % 4
  if (pad) {
    base64 += '='.repeat(4 - pad)
  }
  // Decode Base64 to string
  return atob(base64)
}

onMounted(async () => {
  console.group('Telegram Callback Processing')
  try {
    // Get data from URL hash and invitation parameter
    const hash = window.location.hash
    const urlParams = new URLSearchParams(window.location.search)
    const invitationId = urlParams.get('invitation')
    
    console.log('Raw hash:', hash)
    console.log('Invitation ID:', invitationId)

    if (!hash || !hash.startsWith('#tgAuthResult=')) {
      console.error('No Telegram auth data in URL')
      router.push('/?error=no_auth_data')
      return
    }

    // Extract and decode the data
    const encodedData = hash.replace('#tgAuthResult=', '')
    console.log('Encoded data:', encodedData)
    
    try {
      const decodedString = base64UrlDecode(encodedData)
      console.log('Decoded string:', decodedString)
      const telegramData = JSON.parse(decodedString) as TelegramAuthData
      console.log('Parsed Telegram data:', telegramData)
      
      // Add invitation data if present
      if (invitationId) {
        telegramData.invitation_id = invitationId
      }

      // Validate required fields
      if (!telegramData.hash || !telegramData.id || !telegramData.auth_date) {
        console.error('Missing required fields in auth data')
        router.push('/?error=invalid_data')
        return
      }

      const result = await loginWithTelegramFx(telegramData)
      console.log('Login result:', result)

      if (result.success) {
        console.log('Authentication successful, redirecting to dashboard')
        router.push('/')
      } else {
        console.error('Authentication failed:', result.error)
        if (result.error?.status === 404) {
          // Check if it's an invitation error or registration error
          if (invitationId && result.error?.detail?.includes('Invitation')) {
            router.push('/?error=invitation_used')
          } else {
            router.push('/?error=not_registered')
          }
        } else if (result.error?.status === 500 && result.error?.detail?.includes('invitation')) {
          router.push('/?error=invitation_error')
        } else {
          router.push('/?error=auth_failed')
        }
      }
    } catch (decodeError) {
      console.error('Error decoding/parsing data:', decodeError)
      router.push('/?error=decode_error')
    }
  } catch (error) {
    console.error('Error processing callback:', error)
    router.push('/?error=process_error')
  }
  console.groupEnd()
})
</script> 