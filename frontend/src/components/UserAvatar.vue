<template>
  <div class="user-avatar">
    <v-avatar
      :size="size"
      :color="!fullImageUrl ? 'primary' : undefined"
    >
      <v-img
        v-if="fullImageUrl"
        :src="fullImageUrl"
        :key="fullImageUrl"
        :alt="name || 'User avatar'"
      />
      <span v-else class="text-h6 text-white">
        {{ initials }}
      </span>
    </v-avatar>
    
    <div v-if="editable" class="avatar-edit-container" :style="{ width: `${size}px`, height: `${size}px` }">
      <v-file-input
        ref="fileInput"
        v-model="file"
        accept="image/*"
        hide-input
        class="avatar-input"
        @change="handleFileChange"
      />
      <div class="avatar-edit-overlay" @click="triggerFileInput">
        <v-icon color="white" size="small">mdi-pencil</v-icon>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { uploadAvatar } from '@/stores/user'
import { showNotification } from '@/stores/notification'
import { defaultApiUrl } from '@/utils/constants'

const props = defineProps<{
  imageUrl?: string | null
  name?: string | null
  size?: number
  editable?: boolean
}>()

// Default size if not provided
const size = computed(() => props.size || 40)

const emit = defineEmits<{
  (e: 'update:imageUrl', url: string): void
}>()

const file = ref<File | null>(null)
const fileInput = ref<HTMLElement | null>(null)

// Convert relative URL to absolute URL if needed and add cache-busting parameter
const fullImageUrl = computed(() => {
  if (!props.imageUrl) return null
  
  // Start with the base URL
  let url = props.imageUrl
  
  // If the URL already starts with http:// or https://, it's already a complete URL
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    // Otherwise, combine with the API base URL
    // Remove leading slash if it exists to avoid double slashes
    const avatarPath = url.startsWith('/') ? url.substring(1) : url
    const apiUrl = import.meta.env.VITE_API_URL || defaultApiUrl
    url = `${apiUrl}/${avatarPath}`
  }
  
  // Add a cache-busting timestamp parameter
  return `${url}?t=${new Date().getTime()}`
})

const initials = computed(() => {
  if (!props.name) return '?'
  return props.name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

async function handleFileChange(event: Event) {
  // The file is already bound to file.value through v-model
  if (!file.value) return
  
  try {
    console.log('Uploading file:', file.value)
    const response = await uploadAvatar(file.value)
    // If the returned avatar_url is relative, construct the full URL for emitting
    const avatarUrl = response.avatar_url;
    emit('update:imageUrl', avatarUrl)
    showNotification({
      message: 'Avatar updated successfully',
      type: 'success'
    })
  } catch (error) {
    console.error('Error uploading avatar:', error)
    showNotification({
      message: 'Failed to update avatar',
      type: 'error'
    })
  } finally {
    file.value = null
  }
}

function triggerFileInput() {
  console.log('Triggering file input')
  const input = fileInput.value as HTMLInputElement
  if (input) {
    input.click()
  } else {
    console.error('File input element not found')
  }
}
</script>

<style scoped>
.user-avatar {
  position: relative;
  display: inline-block;
}

.avatar-edit-container {
  position: absolute;
  top: 0;
  left: 0;
  border-radius: 50%;
  overflow: visible;
}

.avatar-input {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

.avatar-edit-button {
  position: absolute;
  bottom: -8px;
  right: -8px;
  z-index: 3;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.avatar-edit-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  cursor: pointer;
  transition: opacity 0.2s ease;
  z-index: 2;
}

.user-avatar:hover .avatar-edit-overlay {
  opacity: 1;
}
</style> 