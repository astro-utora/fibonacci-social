<template lang="pug">
    Fillout(
        v-if="isLoaded"
        :fillout-id="filloutId"
        :data-values="dataValues"
    )
</template>

<script setup lang="ts">
// @ts-ignore - Suppressing TS errors for Vue composition API imports
import { ref, onMounted } from 'vue'
import Fillout from '@/components/Fillout.vue'
import { $user } from '@/stores/user'
import { useStore } from 'effector-vue/composition'
import { $filloutOnboardingId } from '@/stores/adminSettings'
import { $loginEmail } from '@/stores/loginEmail'
import { useRoute } from 'vue-router'

// Use the filloutOnboardingId from the adminSettings store
const filloutId = useStore($filloutOnboardingId)
const dataValues = ref<{[key: string]: string }>({})
const route = useRoute()

const user = $user.getState()
const loginEmail = useStore($loginEmail)
const isLoaded = ref(false)

onMounted(() => {
    if (loginEmail.value) {
        dataValues.value.email = loginEmail.value
    }
    
    // Get payment param from route query
    const paymentParam = route.query.payment
    if (paymentParam && typeof paymentParam === 'string') {
        dataValues.value.payment = paymentParam
    }

    isLoaded.value = true
})
</script>
