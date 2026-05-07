<template>
  <div class="waiting-list-container">
    <v-card class="mx-auto my-4 pa-4 text-center" max-width="600">
      <v-card-title class="text-h5 mb-2">
        <v-icon large color="warning" class="mr-2">mdi-clock-outline</v-icon>
        Your Account is Pending Approval
      </v-card-title>
      
      <v-card-text>
        <p class="text-body-1 mb-4">
          Thank you for registering! Your account is currently in our waiting list and pending approval by an administrator.
        </p>
        
        <p class="text-body-1 mb-4">
          Once your account is approved, you'll have full access to all features of the application.
        </p>
        
        <p class="text-body-2 text-grey">
          Registration date: {{ formatDate(waitingStatus?.created_at) }}
        </p>
      </v-card-text>
      
      <v-card-actions class="justify-center">
        <v-btn
          color="primary"
          @click="refreshStatus"
          :loading="loading"
        >
          Check Status
        </v-btn>
        <v-btn
          color="secondary"
          @click="handleLogout"
        >
          Logout
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { format } from 'date-fns'
import { getCurrentUserStatusFx, WaitingListEntry } from '@/stores/waitingList'
import { logout } from '@/stores/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const waitingStatus = ref<WaitingListEntry | null>(null)
const loading = ref(false)

function formatDate(dateString?: string) {
  if (!dateString) return 'Unknown'
  
  try {
    return format(new Date(dateString), 'MMMM dd, yyyy')
  } catch {
    return dateString
  }
}

async function refreshStatus() {
  loading.value = true
  try {
    const status = await getCurrentUserStatusFx()
    waitingStatus.value = status
    
    // If status is approved, refresh the page to update the UI
    if (status?.status === 'approved') {
      window.location.reload()
    }
  } catch (error) {
    console.error('Error checking status:', error)
  } finally {
    loading.value = false
  }
}

async function handleLogout() {
  await logout()
  router.push('/login')
}

onMounted(async () => {
  await refreshStatus()
})
</script>

<style scoped>
.waiting-list-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
}
</style> 