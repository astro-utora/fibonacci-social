<template>
    <v-card
      :class="{
        'role-card': true,
        'selected': isSelected,
        'has-subroles': role.subroles.length > 0,
        'has-fillout': role.filloutId,
        'started': getSubmissionStatus === 'started',
        'completed': getSubmissionStatus === 'completed',
        'validation-is-requested': getSubmissionStatus === 'requested',
        'validated': getSubmissionStatus === 'validated'
      }"
      @click="$emit('select', role)"
    >
      <v-tooltip
        location="top"
        :text="role.role"
      >
        <template v-slot:activator="{ props }">
          <div class="role-content" v-bind="props">
            <v-card-title class="role-title text-truncate">
              {{ role.role }}
            </v-card-title>
            <v-card-text class="role-icons">
              <div class="icons-container">
                <v-icon 
                  v-if="(!role.filloutId || getSubmissionStatus === 'completed') && role.subroles.length > 0" 
                  :icon="isSelected ? 'mdi-folder-open' : 'mdi-folder'" 
                  size="small" 
                  class="status-icon"
                />
                <v-icon 
                  v-if="getSubmissionStatus === 'completed'" 
                  icon="mdi-pencil-circle-outline" 
                  color="grey"
                  size="small"
                  class="status-icon"
                />
                <v-icon 
                  v-if="getSubmissionStatus === 'started'" 
                  icon="mdi-progress-clock" 
                  color="warning"
                  size="small"
                  class="status-icon"
                />
                <v-icon 
                  v-if="getSubmissionStatus === 'requested'" 
                  icon="mdi-progress-check" 
                  color="info"
                  size="small"
                  class="status-icon"
                />
                <v-icon 
                  v-if="getSubmissionStatus === 'validated'" 
                  icon="mdi-check-circle" 
                  color="success"
                  size="small"
                  class="status-icon"
                />
                <v-btn
                  v-if="role.filloutId"
                  variant="outlined"
                  density="compact"
                  :prepend-icon="getSubmissionStatus !== 'requested' ? 'mdi-form-select' : undefined"
                  :color="getSubmissionStatus !== 'validated' ? 'primary' : 'success'"
                  class="form-btn"
                  @click.stop="openFormDialog"
                  :loading="filloutLoading"
                >
                  {{ formButtonName }}
                </v-btn>
              </div>
            </v-card-text>
          </div>
        </template>
      </v-tooltip>
    <!-- Form Dialog -->
    <v-dialog
      v-model="showFormDialog"
      class="fillout-dialog"
      :width="dialogWidth"
      :height="dialogHeight"
    >
      <v-card class="fill-height">
        <v-card-title class="d-flex align-center pa-4">
          {{ role.role }}
          <v-spacer />
          <v-btn icon @click="showFormDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-divider />
        <v-card-text class="pa-0 fill-height">
          <v-alert
            v-if="filloutError"
            type="error"
            density="compact"
            closable
            class="ma-2"
          >
            {{ filloutError }}
          </v-alert>
          <Fillout
            v-if="role.filloutId"
            :fillout-id="role.filloutId"
            :data-values="{}"
            style="height: 100%;"
          />
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Validation Dialog -->
    <v-dialog
      v-model="showValidationDialog"
      class="validation-dialog"
      width="600"
    >
      <v-card>
        <v-card-title class="d-flex align-center pa-4">
          <div>
            {{ role.role }}
            <v-chip
              v-if="getSubmissionStatus === 'requested' || getSubmissionStatus === 'validated'"
              :color="getSubmissionStatus === 'validated' ? 'success' : 'info'"
              size="small"
              class="ml-2"
            >
              {{ getSubmissionStatus === 'validated' ? 'Validated' : 'Validation Requested' }}
            </v-chip>
          </div>
          <v-spacer />
          <v-btn icon @click="showValidationDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-divider />
        <v-card-text>
          <div v-if="getSubmissionStatus === 'validated'" class="pa-2 mb-2">
            <v-alert
              type="success"
              variant="tonal"
              density="compact"
              icon="mdi-check-circle"
            >
              This submission has been validated. No further action is required.
            </v-alert>
          </div>
          
          <div v-else-if="getSubmissionStatus === 'requested'" class="pa-2 mb-2">
            <v-alert
              type="info"
              variant="tonal"
              density="compact"
              icon="mdi-clock-outline"
            >
              Validation has been requested and is awaiting approval.
            </v-alert>
          </div>
          
          <div v-if="filloutData" class="pa-4">
            <h3 class="text-h6 mb-4">Form Responses</h3>
            <v-list>
              <v-list-item v-for="value in filloutData" :key="value.id">
                <v-list-item-title class="font-weight-bold">{{ value.name }}:</v-list-item-title>
                <v-list-item-subtitle>{{ value.value }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </div>
          <div v-else class="pa-4 text-center">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
            <p class="mt-2">Loading submission data...</p>
          </div>
        </v-card-text>
        <v-divider />
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn
            color="primary"
            variant="text"
            @click="handleUpdate"
          >
            Update
          </v-btn>
          <v-btn
            :color="getSubmissionStatus === 'validated' ? 'success' : 'primary'"
            variant="elevated"
            :loading="validationLoading"
            :disabled="getSubmissionStatus === 'requested' || getSubmissionStatus === 'validated'"
            @click="requestValidation"
          >
            {{ getValidateButtonLabel }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    </v-card>
</template>

<script setup lang="ts">
import { ref, computed, type DeepReadonly } from 'vue'
import { useStore } from 'effector-vue/composition'
import { $filloutSubmissions, FilloutSubmission, loadSubmissionsFx, startFilloutFx, $filloutLoading, $filloutError } from '@/stores/fillout'
import { $activeProject } from '@/stores/project'
import Fillout from '@/components/Fillout.vue'
import type { SubRole } from '@/types'
import * as filloutService from '@/services/fillout'
import { Project } from '@/types/project'

const props = defineProps<{
  role: DeepReadonly<SubRole>;
  isSelected: boolean;
}>()

const emit = defineEmits<{
  select: [role: DeepReadonly<SubRole>]
}>()

// Dialogs
const showFormDialog = ref(false)
const showValidationDialog = ref(false)
const filloutData = ref<any>(null)
const validationLoading = ref(false)
const submissions = useStore<FilloutSubmission[]>($filloutSubmissions)
const activeProject = useStore<Project | null>($activeProject)
const filloutLoading = useStore($filloutLoading)
const filloutError = useStore($filloutError)

const formButtonName = computed(() => {
  if (getSubmissionStatus.value == null) return 'Answer needed'
  if (getSubmissionStatus.value === 'started') return 'Answer needed'
  if (getSubmissionStatus.value === 'completed') return 'Request validation'
  if (getSubmissionStatus.value === 'requested') return 'Waiting for validation'
  if (getSubmissionStatus.value === 'validated') return 'Validated'
  return 'Answer needed'
})

// Computed properties for dialogs
const dialogWidth = computed(() => {
  const width = window.innerWidth * 0.8
  return Math.min(Math.max(width, 600), 1200) // min 600px, max 1200px
})

const dialogHeight = computed(() => {
  const height = window.innerHeight * 0.8
  return Math.min(Math.max(height, 400), 900) // min 400px, max 900px
})

// Computed property for submission status
const getSubmissionStatus = computed((): 'started' | 'completed' | 'requested' | 'validated' | null => {
  if (!props.role.filloutId) return null
  const submission = submissions.value.find(s => s.filloutId === props.role.filloutId)
  return submission?.status || null
})

const getValidateButtonLabel = computed(() => {
  if (getSubmissionStatus.value === 'requested') return 'Waiting for validation'
  if (getSubmissionStatus.value === 'validated') return 'Validated'
  return 'Validate'
})

async function openFormDialog() {
  if (getSubmissionStatus.value === 'completed' || getSubmissionStatus.value === 'requested' || getSubmissionStatus.value === 'validated') {
    await openValidationDialog()
  } else {
    await openForm()
  }
}

// Event handlers
async function openForm() {
  showFormDialog.value = true
  if (getSubmissionStatus.value == null) {
    // Record fillout start using Effector effect
    // State management flow:
    // 1. startFilloutFx is called with payload
    // 2. $filloutLoading is set to true while request is in progress
    // 3. API call is made via the effect
    // 4. On success, $filloutStatus is updated with the new status
    // 5. On error, $filloutError is updated with the error message
    // 6. $filloutLoading is set back to false when complete
    try {
      const payload = {
        filloutId: props.role.filloutId,
        project_id: activeProject.value?.id || undefined
      }
      
      await startFilloutFx(payload)
    } catch (error) {
      console.error('Error starting fillout:', error)
    }
  }
}

async function openValidationDialog() {
  showValidationDialog.value = true
  filloutData.value = null

  try {
    // Fetch fillout data
    const response = await filloutService.getFilloutData(props.role.filloutId)
    filloutData.value = response.submission_data
  } catch (error) {
    console.error('Error fetching fillout data:', error)
  }
}

async function handleUpdate() {
  showValidationDialog.value = false
  openForm()
}

async function requestValidation() {
  if (!props.role.filloutId) return
  
  validationLoading.value = true
  
  try {
    await filloutService.requestValidation(
      props.role.filloutId,
      { projectId: props.role.projectId }
    )
    
    // Close dialog
    showValidationDialog.value = false
    
    // Reload submissions to update status
    await loadSubmissionsFx({ projectId: props.role.projectId })
  } catch (error) {
    console.error('Error requesting validation:', error)
  } finally {
    validationLoading.value = false
  }
}
</script>

<style scoped>
.role-card {
  flex: 0 0 auto;
  min-width: 150px;
  max-width: 250px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e0e0e0;
  display: flex;
}

.role-content {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.role-title {
  font-size: 1rem;
  line-height: 1.2;
  padding: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.role-icons {
  display: flex;
  padding: 4px 8px;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.icons-container {
  display: flex;
  gap: 4px;
  align-items: center;
}

.status-icon {
  flex: 0 0 auto;
}

.form-btn {
  font-size: 0.875rem;
  padding: 0 8px;
  flex: 0 0 auto;
  margin-left: auto;
}

.selected {
  border: 2px solid #1976d2;
}

.has-subroles {
  border-bottom: 2px solid #9c27b0;
}

.has-fillout {
  border-right: 2px solid #2196f3;
}

.started {
  border-left: 4px solid #ff9800;
}

.completed {
  border-left: 4px solid #4caf50;
}

.validation-is-requested {
  border-left: 4px solid #2196f3;
}

.validated {
  border-left: 4px solid #4caf50;
}

.fillout-dialog, .validation-dialog {
  margin: 0;
}

:deep(.v-card) {
  display: flex;
  flex-direction: column;
  max-height: 100%;
}

:deep(.v-card-text) {
  flex-grow: 1;
  overflow-y: auto;
}

:deep(.fillout-embed) {
  height: 100%;
}

.text-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style> 