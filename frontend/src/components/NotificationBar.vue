<template>
  <v-snackbar
    v-model="show"
    :color="notification?.type"
    :timeout="notification?.timeout || 3000"
    location="top"
  >
    {{ notification?.message }}
    
    <template v-slot:actions>
      <v-btn
        variant="text"
        @click="hideNotification"
      >
        Close
      </v-btn>
    </template>
  </v-snackbar>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useStore } from 'effector-vue/composition'
import { $notification, hideNotification, Notification } from '@/stores/notification'

const notification = useStore<Notification>($notification)
const show = computed({
  get: () => !!notification.value,
  set: (value: boolean) => {
    if (!value) hideNotification()
  }
})
</script> 