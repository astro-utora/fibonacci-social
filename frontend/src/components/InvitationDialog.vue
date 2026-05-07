<template>
  <div>
    <!-- New Invitation Dialog -->
    <v-dialog v-model="showDialog" max-width="600px">
      <v-card>
        <v-card-title>Create New Invitation</v-card-title>
        <UserProfileForm
          submit-text="Generate Invitation"
          cancel-text="Cancel"
          :processing="isGenerating"
          :processing-error="error"
          @submit="handleSubmit"
          @cancel="closeDialog"
        />
      </v-card>
    </v-dialog>

    <!-- Success Dialog -->
    <v-dialog v-model="showSuccessDialog" max-width="500px">
      <v-card>
        <v-card-title>Invitation Created</v-card-title>
        <v-card-text>
          <p>Share this link with the invited user:</p>
          <v-text-field
            v-model="generatedInvitationLink"
            readonly
            append-inner-icon="mdi-content-copy"
            @click:append-inner="copyGeneratedLink"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="closeSuccessDialog">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Copy success snackbar -->
    <v-snackbar v-model="showCopySuccess" timeout="2000">
      Invitation link copied to clipboard!
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import UserProfileForm from '@/components/UserProfileForm.vue'
import { useStore } from 'effector-vue/composition'
import { $user } from '@/stores/user'
import api from '@/utils/axios'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const user = useStore($user)
const isGenerating = ref(false)
const showSuccessDialog = ref(false)
const generatedInvitationLink = ref('')
const showCopySuccess = ref(false)

const showDialog = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value)
})

const error = ref('')

async function closeDialog() {
  showDialog.value = false
}

async function closeSuccessDialog() {
  showSuccessDialog.value = false
}

async function copyGeneratedLink() {
  try {
    await navigator.clipboard.writeText(generatedInvitationLink.value)
    showCopySuccess.value = true
  } catch (err) {
    console.error('Failed to copy generated link:', err)
  }
}

async function handleSubmit(formData: any) {
  isGenerating.value = true
  try {
    const response = await api.post('/api/invitations', formData)

    generatedInvitationLink.value = `${window.location.origin}/?invitation=${response.data.id}`
    showDialog.value = false
    showSuccessDialog.value = true
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to generate invitation. Please try again.'
    console.error('Error generating invitation:', e)
  } finally {
    isGenerating.value = false
  }
}
</script> 