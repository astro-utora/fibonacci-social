<template>
  <div style="width: 100%; height: 100%; display: flex; flex-direction: column;">
    <h1>Fibonacci + fillout test</h1>
    <div
        style="width:100%; flex: 1;"
        data-fillout-id="i8uLkjbaAUus"
        data-fillout-embed-type="standard"
        data-fillout-inherit-parameters
        data-fillout-dynamic-resize
        :data-userId="userId"
        >
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { User } from '@/types'
import { useStore } from 'effector-vue/composition'
import { $user } from '@/stores/auth'

const user = useStore<User>($user)

const userId = computed(() => user.value?.id)

onMounted(async () => {
  await loadScript()
})

const loadScript = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    // Check if script is already loaded
    if (document.querySelector('script#google-signin')) {
      resolve()
      return
    }

    const script = document.createElement('script')
    script.id = 'fillout-script'
    script.src = 'https://server.fillout.com/embed/v1/'
    script.async = true
    script.defer = true
    script.onload = () => resolve()
    script.onerror = (e) => reject(e)
    document.head.appendChild(script)
  })
}
</script>

