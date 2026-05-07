<template>
  <div
    ref="fillout"
    :data-fillout-id="filloutId"
    data-fillout-embed-type="standard"
    data-fillout-inherit-parameters
    data-fillout-dynamic-resize
    :data-formId="filloutId"
    :data-home="windowLocation"
    :data-userId="user?.uuid"
  />
</template>  
<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useStore } from 'effector-vue/composition'
import { $user } from '@/stores/auth'
import api from '@/utils/axios'
import type { User } from '@/types'

const props = defineProps<{
  filloutId: string,
  dataValues: { [key: string]: string }
}>()

const user = useStore<User | null>($user)
const fillout = ref<HTMLDivElement | null>(null)

const windowLocation = ref(window.location.origin)

onMounted(async () => {
  if (fillout.value && props.dataValues) {
    for (const [key, value] of Object.entries(props.dataValues)) {
      const dataKey = "data-" + key
      const attr = document.createAttribute(dataKey)
      attr.value = value
      fillout.value.attributes.setNamedItem(attr)
    }
  }
  try {
    await loadScript()
  } catch (error) {
    console.error('Failed to record fillout start:', error)
  }
})

onUnmounted(() => {
  const script = document.querySelector('script#fillout-script')
  if (script) {
    document.head.removeChild(script)
  }
})

const loadScript = (): Promise<void> => {
  return new Promise((resolve, reject) => {
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
