<template>
  <v-container class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card>
          <v-card-title class="text-center">Login</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="handleSubmit">
              <v-text-field
                v-model="email"
                label="Email"
                type="email"
                required
              />
              <v-text-field
                v-model="password"
                label="Password"
                type="password"
                required
              />
              <v-btn
                block
                color="primary"
                type="submit"
                :loading="isLoading"
              >
                Login
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { loginFx } from '@/stores/auth'
import { showNotification } from '@/stores/notification'

const router = useRouter()
const email = ref('')
const password = ref('')
const isLoading = ref(false)

async function handleSubmit() {
  if (!email.value || !password.value) return
  
  isLoading.value = true
  try {
    await loginFx({ email: email.value, password: password.value })
    router.push('/')
  } catch (error) {
    showNotification({
      type: 'error',
      message: 'Login failed. Please check your credentials.'
    })
  } finally {
    isLoading.value = false
  }
}
</script> 