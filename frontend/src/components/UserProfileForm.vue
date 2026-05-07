<template>
  <v-card-text>
    <v-form
      ref="form"
      v-model="isValid"
      @submit.prevent="handleSubmit"
      validate-on="blur"
    >
      <v-text-field
        v-model="formData.name"
        label="Full Name"
        :rules="[rules.required]"
        validate-on-blur
        required
      ></v-text-field>

      <v-text-field
        v-model="formData.location"
        label="Location"
        :rules="[rules.required]"
        validate-on-blur
        required
      ></v-text-field>

      <v-text-field
        v-model="formData.role"
        label="Role"
        :rules="[rules.required]"
        validate-on-blur
        required
      ></v-text-field>

      <v-text-field
        v-model="formData.workplace"
        label="Workplace"
        :rules="[rules.required]"
        validate-on-blur
        required
      ></v-text-field>

      <v-text-field
        v-model="formData.birth_date"
        label="Birth Date"
        type="date"
        :rules="[rules.required]"
        validate-on-blur
        required
      ></v-text-field>

      <v-textarea
        v-model="formData.goals"
        label="Goals"
        :rules="[rules.required]"
        validate-on-blur
        required
      ></v-textarea>

      <v-text-field
        v-model="formData.education"
        label="Education"
        :rules="[rules.required]"
        validate-on-blur
        required
      ></v-text-field>

      <v-text-field
        v-model="formData.phone_number"
        label="Phone Number"
        :rules="[rules.required]"
        validate-on-blur
        required
      ></v-text-field>

      <v-alert
        v-if="processingError"
        type="error"
        class="mb-4"
      >
        {{ processingError }}
      </v-alert>
    </v-form>
  </v-card-text>
  <v-card-actions>
    <v-spacer></v-spacer>
    <v-btn v-if="cancelText" color="error" @click="handleCancel">{{ cancelText }}</v-btn>
    <v-btn 
      color="primary" 
      :loading="processing"
      :disabled="!isValid"
      @click="handleSubmit"
    >
      {{ submitText }}
    </v-btn>
  </v-card-actions>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  submitText: string,
  cancelText?: string,
  processing: boolean,
  processingError?: string
}>()

const emit = defineEmits(['submit', 'cancel'])

const form = ref<any>(null)
const isValid = ref(false)

const formData = ref({
  name: '',
  location: '',
  workplace: '',
  role: '',
  birth_date: '',
  goals: '',
  education: '',
  phone_number: ''
})

const rules = {
  required: (v: string) => !!v || 'Field is required',
  date: (v: string) => /^\d{4}-\d{2}-\d{2}$/.test(v) || 'Invalid date format (YYYY-MM-DD)'
}

function handleSubmit() {
  if (!form.value?.validate()) return

  emit('submit', formData.value)
}

function handleCancel() {
  emit('cancel')
}
</script>