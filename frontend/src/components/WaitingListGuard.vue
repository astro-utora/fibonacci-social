<template>
  <div>
    <!-- Show waiting list status if user is in waiting list -->
    <WaitingListStatus v-if="showWaitingStatus" />
    
    <!-- Show actual content if user is not in waiting list -->
    <slot v-else></slot>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useStore } from 'effector-vue/composition'
import { $user } from '@/stores/auth'
import WaitingListStatus from '@/components/WaitingListStatus.vue'

const user = useStore($user)

// Show waiting list status if user has a pending waiting list status
const showWaitingStatus = computed(() => {
  return user.value?.waiting_list_status === 'pending'
})
</script> 