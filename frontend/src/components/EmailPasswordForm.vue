<template>
  <v-form
    ref="form"
    v-model="isValid"
    @submit.prevent="handleSubmit"
  >
    <v-text-field
      v-model="formData.email"
      label="Email"
      type="email"
      :rules="[rules.required, rules.email]"
      validate-on-blur
      required
    ></v-text-field>

    <v-text-field
      v-model="formData.password"
      label="Password"
      :type="showPassword ? 'text' : 'password'"
      :rules="[rules.required, rules.password]"
      :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
      @click:append="showPassword = !showPassword"
      validate-on-blur
      required
    ></v-text-field>

    <v-text-field
      v-if="showPasswordConfirmation"
      v-model="formData.confirmPassword"
      label="Confirm Password"
      :type="showPassword ? 'text' : 'password'"
      :rules="[rules.required, rules.confirmPassword]"
      validate-on-blur
      required
    ></v-text-field>

    <v-alert
      v-if="error"
      type="error"
      class="mb-4"
    >
      {{ error }}
    </v-alert>

    <v-btn
      block
      color="primary"
      type="submit"
      :loading="loading"
      :disabled="!isValid"
    >
      {{ submitText }}
    </v-btn>
  </v-form>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const props = defineProps<{
  loading: boolean,
  showPasswordConfirmation: boolean,
  submitText: string,
  error?: string,
}>()

const emit = defineEmits(['submit'])

const form = ref<any>(null)

const showPassword = ref(false)
const isValid = ref(false)

const formData = ref({
  email: '',
  password: '',
  confirmPassword: ''
})

const rules = {
  required: (v: string) => !!v || 'Field is required',
  email: (v: string) => /.+@.+\..+/.test(v) || 'Invalid email',
  password: (v: string) => v.length >= 8 || 'Password must be at least 8 characters',
  confirmPassword: (v: string) => v === formData.value.password || 'Passwords must match'
}

const handleSubmit = () => {
  form.value.validate().then(() => {
    emit('submit', formData.value)
  })
}


</script>