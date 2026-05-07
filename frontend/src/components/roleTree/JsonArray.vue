<template>
  <div class="json-array">
    <div v-if="fieldName" class="array-header">
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
        <span class="item-count">({{ localData.length }} items)</span>
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
    <div v-if="!isCollapsed" class="array-content">
      <div class="array-items">
        <template v-for="(item, index) in localData" :key="index">
          <!-- For object items -->
          <div class="array-item-wrapper">
            <json-object 
              v-if="isObject(item)" 
              :data="item" 
              :field-name="null"
              @update:data="updateItem(index, $event)"
              class="array-item-object"
            />
            <!-- For primitive items -->
            <div v-else class="array-item-primitive">
              <hjson-editor 
                :value="item" 
                @update:value="updateItem(index, $event)" 
                class="hjson-editor"
              />
            </div>
            <!-- Remove item button -->
            <v-btn
              size="x-small"
              icon
              variant="text"
              @click="removeItem(index)"
              class="remove-item-btn"
            >
              <v-icon size="small">mdi-close</v-icon>
            </v-btn>
          </div>
        </template>
        
        <!-- Add item button inline with array items -->
        <button class="add-item-btn" @click="addItem">+</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from '@vue/runtime-core'
import HjsonEditor from './HjsonEditor.vue'
import JsonObject from './JsonObject.vue'

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  fieldName: {
    type: String,
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
  displayFieldName.value = newValue || ''
})

// Update field name when edited
const updateFieldName = () => {
  if (displayFieldName.value !== props.fieldName) {
    emit('update:field-name', displayFieldName.value)
  }
}

// Create a local copy of the data
const localData = ref([...props.data])

// Watch for changes in props data and update local data
watch(() => props.data, (newValue: any[]) => {
  localData.value = [...newValue]
}, { deep: true })

// Helper to check if an item is an object
const isObject = (item: any): boolean => {
  return typeof item === 'object' && item !== null && !Array.isArray(item)
}

// Update item at specific index
const updateItem = (index: number, value: any) => {
  localData.value[index] = value
  emit('update:data', [...localData.value])
}

// Remove item at specific index
const removeItem = (index: number) => {
  const newData = [...localData.value]
  newData.splice(index, 1)
  localData.value = newData
  emit('update:data', newData)
}

// Add a new item to the array
const addItem = () => {
  // Determine the type of the new item based on existing items
  let newItem: any = null
  
  if (localData.value.length > 0) {
    const lastItem = localData.value[localData.value.length - 1]
    if (isObject(lastItem)) {
      // Create an empty object with the same structure
      newItem = {}
      for (const key in lastItem as Record<string, any>) {
        if (isObject(lastItem[key])) {
          newItem[key] = {}
        } else if (Array.isArray(lastItem[key])) {
          newItem[key] = []
        } else {
          newItem[key] = null
        }
      }
    } else if (typeof lastItem === 'string') {
      newItem = ''
    } else if (typeof lastItem === 'number') {
      newItem = 0
    } else if (typeof lastItem === 'boolean') {
      newItem = false
    }
  } else {
    // Default to empty object if array is empty
    newItem = {}
  }
  
  localData.value.push(newItem)
  emit('update:data', [...localData.value])
}
</script>

<style scoped>
.json-array {
  border: 1px solid #d0e8ff;
  border-radius: 4px;
  margin: 8px;
  /* background-color: #f5f9ff; */
  padding: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.array-header {
  font-weight: bold;
  font-size: 16px;
  padding-bottom: 0;
  color: #0066cc;
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
  color: #0066cc;
  padding: 0;
  margin: 0;
}

.item-count {
  margin-left: 8px;
  font-size: 12px;
  color: #666;
  font-weight: normal;
}

.remove-btn {
  margin-left: auto;
}

.array-content {
  margin-top: 0;
  padding-top: 0;
}

.array-items {
  display: flex;
  flex-wrap: nowrap;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 8px;
  margin-top: 4px;
}

.array-item-wrapper {
  position: relative;
  flex-shrink: 0;
}

.array-item-primitive {
  display: flex;
  align-items: center;
  background-color: white;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 8px;
  margin-bottom: 6px;
  min-width: 160px;
  flex-shrink: 0;
}

.hjson-editor {
  width: 100%;
}

.array-item-object {
  min-width: 250px;
  flex-shrink: 0;
  padding-left: 0px !important;
  padding-right: 0px !important;
}

.remove-item-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  opacity: 0.8;
  z-index: 1;
}


.add-item-btn {
  background-color: white;
  color: #4d9fff;
  border: 1px solid #d0e8ff;
  border-radius: 4px;
  width: 30px;
  height: 30px;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.add-item-btn:hover {
  background-color: #f5f9ff;
  border-color: #4d9fff;
}
</style>