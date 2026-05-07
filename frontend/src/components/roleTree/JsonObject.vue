<template>
  <div class="json-object">
    <div v-if="fieldName !== null" class="object-header">
      <div class="header-content">
        <v-btn
          size="x-small"
          icon
          variant="text"
          color="grey"
          @click="isCollapsed = !isCollapsed"
          class="toggle-btn"
        >
          <v-icon size="small">{{ isCollapsed ? 'mdi-chevron-right' : 'mdi-chevron-down' }}</v-icon>
        </v-btn>
        <v-text-field
          v-model="displayFieldName"
          variant="plain"
          density="compact"
          hide-details
          class="field-name-input"
          @change="updateFieldName"
        />
        <v-btn
          v-if="canRemove"
          size="small"
          icon
          variant="text"
          @click="$emit('remove')"
          class="remove-btn"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </div>
    </div>
    <div v-if="!isCollapsed" class="object-content">
      <!-- All primitive fields in single hjson editor -->
      <div v-if="hasPrimitiveFields" class="primitive-fields">
        <hjson-editor 
          :value="primitiveFieldsObject" 
          @update:value="updatePrimitiveFields" 
          class="hjson-editor" 
        />
      </div>
      
      <!-- Object and Array fields in a single horizontally scrollable row -->
      <div v-if="hasObjectFields || hasArrayFields" class="complex-fields-container">
        <div class="complex-fields-scroll">
          <!-- Object fields first -->
          <div v-if="hasObjectFields" class="object-fields">
            <json-object 
              v-for="(value, key) in objectFields" 
              :key="key" 
              :data="value" 
              :field-name="key" 
              :can-remove="true"
              @update:data="updateObjectField(key, $event)"
              @update:field-name="renameObjectField(key, $event)"
              @remove="removeObjectField(key)"
              class="nested-object"
            />
          </div>
          
          <!-- Array fields to the right -->
          <div v-if="hasArrayFields" class="array-fields">
            <json-array 
              v-for="(value, key) in arrayFields" 
              :key="key" 
              :data="value" 
              :field-name="key"
              :can-remove="true"
              @update:data="updateArrayField(key, $event)"
              @update:field-name="renameArrayField(key, $event)"
              @remove="removeArrayField(key)"
              class="nested-array"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from '@vue/runtime-core'
import HjsonEditor from './HjsonEditor.vue'
import JsonArray from './JsonArray.vue'

const props = defineProps({
  data: {
    type: Object,
    required: true
  },
  fieldName: {
    type: [String, null],
    default: ''
  },
  canRemove: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:data', 'update:field-name', 'remove'])

// Collapse state
const isCollapsed = ref(false)

// For editable field name
const displayFieldName = ref(props.fieldName || '')

// Watch for field name changes from parent
watch(() => props.fieldName, (newValue) => {
  if (newValue !== null) {
    displayFieldName.value = newValue || ''
  }
})

// Update field name when edited
const updateFieldName = () => {
  if (props.fieldName !== null && displayFieldName.value !== props.fieldName) {
    emit('update:field-name', displayFieldName.value)
  }
}

// Create a local copy of the data
const localData = ref({ ...props.data })

// Watch for changes in props data and update local data
watch(() => props.data, (newValue: any) => {
  localData.value = { ...newValue }
}, { deep: true })

// Categorize fields by type
const primitiveFields = computed(() => {
  const result: Record<string, any> = {}
  for (const key in localData.value) {
    const value = localData.value[key]
    if (value === null || ['string', 'number', 'boolean'].includes(typeof value)) {
      result[key] = value
    }
  }
  return result
})

// Create an object with just the primitive fields
const primitiveFieldsObject = computed(() => {
  return primitiveFields.value
})

const objectFields = computed(() => {
  const result: Record<string, any> = {}
  for (const key in localData.value) {
    const value = localData.value[key]
    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      result[key] = value
    }
  }
  return result
})

const arrayFields = computed(() => {
  const result: Record<string, any> = {}
  for (const key in localData.value) {
    const value = localData.value[key]
    if (Array.isArray(value)) {
      result[key] = value
    }
  }
  return result
})

// Computed properties to check if fields of each type exist
const hasPrimitiveFields = computed(() => Object.keys(primitiveFields.value).length > 0)
const hasObjectFields = computed(() => Object.keys(objectFields.value).length > 0)
const hasArrayFields = computed(() => Object.keys(arrayFields.value).length > 0)

// Update multiple primitive fields at once
const updatePrimitiveFields = (updatedPrimitives: Record<string, any>) => {
  // Update only the primitive fields that were edited
  for (const key in updatedPrimitives) {
    if (key in localData.value) {
      localData.value[key] = updatedPrimitives[key]
    }
  }
  
  emit('update:data', { ...localData.value })
}

// Field update methods
const updateObjectField = (key: string, value: object) => {
  localData.value[key] = value
  emit('update:data', { ...localData.value })
}

const updateArrayField = (key: string, value: any[]) => {
  localData.value[key] = value
  emit('update:data', { ...localData.value })
}

// Rename field methods
const renameObjectField = (oldKey: string, newKey: string) => {
  if (oldKey !== newKey && oldKey in localData.value) {
    const newData = { ...localData.value }
    newData[newKey] = newData[oldKey]
    delete newData[oldKey]
    localData.value = newData
    emit('update:data', newData)
  }
}

const renameArrayField = (oldKey: string, newKey: string) => {
  renameObjectField(oldKey, newKey) // Same implementation
}

// Remove field methods
const removeObjectField = (key: string) => {
  if (key in localData.value) {
    const newData = { ...localData.value }
    delete newData[key]
    localData.value = newData
    emit('update:data', newData)
  }
}

const removeArrayField = (key: string) => {
  removeObjectField(key) // Same implementation
}
</script>

<style scoped>
.json-object {
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  padding-left: 12px;
  padding-right: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.object-header {
  font-weight: bold;
  font-size: 16px;
  padding-bottom: 0;
  color: #333;
}

.header-content {
  display: flex;
  align-items: center;
}

.toggle-btn {
  margin-right: 4px;
}

.field-name-input {
  font-weight: bold;
  max-width: 200px;
  padding: 0;
  margin: 0;
}

.remove-btn {
  margin-left: auto;
}

.primitive-fields {
  margin-bottom: 0;
  margin-top: 0;
  padding-top: 0;
}

.hjson-editor {
  width: 100%;
}

/* Container for both object and array fields */
.complex-fields-container {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
  width: 100%;
  overflow: hidden;
}

.complex-fields-scroll {
  display: flex;
  width: 100%;
  overflow-x: auto;
  padding-bottom: 0px;
}

.object-fields, .array-fields {
  display: flex;
  flex-wrap: nowrap;
  min-width: fit-content;
}

.nested-object, .nested-array {
  min-width: 250px;
  flex-shrink: 0;
}
</style>