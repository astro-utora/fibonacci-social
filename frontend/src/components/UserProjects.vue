<template>
  <div class="user-projects">
    <div v-if="showTitle" class="d-flex justify-space-between align-center mb-4">
      <h3 class="text-h6 mb-0">Your Projects</h3>
      <v-btn
        v-if="showCreateButton"
        color="primary"
        prepend-icon="mdi-plus"
        variant="outlined"
        @click="openCreateDialog"
      >
        Create Project
      </v-btn>
    </div>
    <div v-else-if="showCreateButton" class="d-flex justify-end mb-4">
      <v-btn
        color="primary"
        prepend-icon="mdi-plus"
        variant="outlined"
        @click="openCreateDialog"
      >
        Create Project
      </v-btn>
    </div>

    <div v-if="isLoading" class="d-flex justify-center my-4">
      <v-progress-circular indeterminate />
    </div>

    <v-alert
      v-else-if="error"
      type="error"
      class="mb-4"
    >
      {{ error }}
    </v-alert>

    <v-list v-else-if="projects.length > 0">
      <v-list-item
        v-for="project in projects"
        :key="project.id"
        :title="project.project_name"
        :subtitle="`Created: ${formatDate(project.created_at)}`"
        @click="handleProjectSelect(project)"
      >
        <template v-slot:prepend>
          <v-icon icon="mdi-image-outline" />
        </template>
      </v-list-item>
    </v-list>

    <v-alert
      v-else
      type="info"
      class="my-4"
    >
      You don't have any projects yet. Create your first project to get started!
    </v-alert>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'effector-vue/composition'
import { $projects, $projectsLoading, $projectsError, loadProjectsFx, refreshProjects } from '@/stores/project'

const props = defineProps({
  showTitle: {
    type: Boolean,
    default: true
  },
  showCreateButton: {
    type: Boolean,
    default: true
  },
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select-project', 'update:modelValue'])

// Use effector stores
const projects = useStore($projects)
const isLoading = useStore($projectsLoading)
const error = useStore($projectsError)
const showCreateDialog = ref(false)

// Handle v-model for the dialog
const showCreateDialogComputed = computed({
  get: () => props.modelValue || showCreateDialog.value,
  set: (value) => {
    showCreateDialog.value = value
    emit('update:modelValue', value)
  }
})

// Lifecycle hooks
onMounted(async () => {
  // Load projects on component mount
  loadProjectsFx()
})

// Actions
function openCreateDialog() {
  showCreateDialogComputed.value = true
}

function closeCreateDialog() {
  showCreateDialogComputed.value = false
}

function handleProjectSelect(project) {
  // Emit event to parent component
  emit('select-project', project)
}

// Refresh projects - now just triggers the refreshProjects event
async function refreshProjectsList() {
  refreshProjects()
}

// Helpers
function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

// Expose methods to parent components
defineExpose({
  refreshProjects: refreshProjectsList
})
</script>

<style scoped>
.user-projects {
  margin-top: 20px;
}
</style> 