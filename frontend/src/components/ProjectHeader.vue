<template>
  <div v-if="activeProject" class="project-header">
    <v-alert
      color="primary"
      variant="tonal"
      class="mb-4"
    >
      <div class="d-flex align-center">
        <v-icon icon="mdi-folder-open" class="mr-2" />
        <div class="text-subtitle-1 font-weight-medium">
          Project: {{ activeProject.project_name }}
        </div>
        <v-spacer />
        <v-btn
          variant="text"
          color="primary"
          prepend-icon="mdi-cog"
          @click="openProjectSettings"
        >
          Project Settings
        </v-btn>
        <v-btn
          variant="outlined"
          color="primary"
          prepend-icon="mdi-close"
          @click="handleCloseProject"
        >
          Close Project
        </v-btn>
      </div>
    </v-alert>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// In a real implementation, this would use a store
// Using props for now
const props = defineProps({
  activeProject: Object
})

const emit = defineEmits(['close', 'settings'])

// Actions
function handleCloseProject() {
  emit('close')
}

function openProjectSettings() {
  emit('settings', props.activeProject?.id)
}
</script> 