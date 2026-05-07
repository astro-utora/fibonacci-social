<template>
  <v-container fluid>
    <v-card>
      <v-card-title class="d-flex align-center">
        <h1 class="text-h5">User Forms Monitoring</h1>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          prepend-icon="mdi-refresh"
          :loading="isLoading"
          @click="refreshData"
        >
          Refresh
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-alert
          v-if="error"
          type="error"
          closable
          @click:close="resetError"
        >
          {{ error }}
        </v-alert>

        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
          class="mb-4"
        ></v-text-field>

        <v-data-table
          :headers="headers"
          :items="userForms"
          :search="search"
          :loading="isLoading"
          :items-per-page="-1"
          hide-default-footer
          class="elevation-1"
        >
          <!-- User Name Column -->
          <template v-slot:item.userName="{ item }">
            <div class="font-weight-medium">{{ item.userName }}</div>
            <div class="text-caption text-grey">{{ item.userId }}</div>
          </template>

          <!-- Start Date Column -->
          <template v-slot:item.startDate="{ item }">
            {{ formatDate(item.startDate) }}
          </template>

          <!-- Complete Date Column -->
          <template v-slot:item.completeDate="{ item }">
            <span v-if="item.completeDate">{{ formatDate(item.completeDate) }}</span>
            <span v-else>-</span>
          </template>

          <!-- Request Date Column -->
          <template v-slot:item.requestedDate="{ item }">
            <span v-if="item.requestedDate">{{ formatDate(item.requestedDate) }}</span>
            <span v-else>-</span>
          </template>

          <!-- Validated Date Column -->
          <template v-slot:item.validatedDate="{ item }">
            <span v-if="item.validatedDate">{{ formatDate(item.validatedDate) }}</span>
            <span v-else>-</span>
          </template>

          <!-- Status Column -->
          <template v-slot:item.status="{ item }">
            <v-chip
              :color="getStatusColor(item)"
              size="small"
            >
              {{ getStatusText(item) }}
            </v-chip>
          </template>

          <!-- Actions Column -->
          <template v-slot:item.actions="{ item }">
            <div v-if="item.requestedDate && !item.validatedDate">
              <v-btn
                color="primary"
                size="small"
                variant="elevated"
                prepend-icon="mdi-eye"
                @click="openReviewDialog(item)"
              >
                Review
              </v-btn>
            </div>
          </template>
        </v-data-table>

        <!-- Pagination Controls -->
        <div class="d-flex align-center mt-4">
          <v-select
            :model-value="currentPageSize"
            @update:model-value="handlePageSizeChange"
            :items="pageSizeOptions"
            label="Items per page"
            variant="outlined"
            density="compact"
            hide-details
            class="pagination-select mr-4"
            style="max-width: 150px;"
          ></v-select>
          
          <v-spacer></v-spacer>
          
          <v-pagination
            v-if="pagination && pagination.total_pages > 0"
            :model-value="currentPage"
            @update:model-value="handlePageChange"
            :length="pagination.total_pages"
            :total-visible="7"
            rounded
          ></v-pagination>
        </div>
      </v-card-text>
    </v-card>

    <!-- Review Dialog -->
    <v-dialog
      v-model="showReviewDialog"
      max-width="700px"
    >
      <v-card>
        <v-card-title class="d-flex align-center">
          <span>Review Form Submission</span>
          <v-spacer></v-spacer>
          <v-btn icon @click="showReviewDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        
        <v-card-text>
          <div v-if="selectedItem">
            <div class="d-flex align-center mb-4">
              <h3 class="text-h6">{{ selectedItem.role }} - {{ selectedItem.userName }}</h3>
              <v-chip class="ml-2" :color="getStatusColor(selectedItem)" size="small">
                {{ getStatusText(selectedItem) }}
              </v-chip>
            </div>

            <v-divider class="mb-4"></v-divider>

            <div v-if="isFormDataLoading" class="d-flex flex-column align-center my-4">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
              <span class="mt-2">Loading form data...</span>
            </div>

            <div v-else-if="formDataError" class="text-center my-4">
              <v-alert type="error" density="compact">
                {{ formDataError }}
              </v-alert>
              <v-btn class="mt-4" @click="fetchFormData(selectedItem)">
                Try Again
              </v-btn>
            </div>

            <div v-else-if="formData && formData.length > 0">
              <h4 class="text-subtitle-1 mb-3">Form Responses</h4>
              <v-list>
                <v-list-item v-for="(field, index) in formData" :key="index" density="compact">
                  <template v-slot:prepend>
                    <v-icon color="primary" size="small" class="mr-2">mdi-form-textbox</v-icon>
                  </template>
                  <v-list-item-title class="font-weight-medium text-subtitle-2">
                    {{ field.name }}:
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    {{ formatFieldValue(field.value) }}
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </div>

            <div v-else class="text-center my-4">
              <v-alert type="info" density="compact">
                No form data available for this submission.
              </v-alert>
            </div>
          </div>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn
            color="error"
            variant="outlined"
            prepend-icon="mdi-close-circle"
            @click="handleReject"
            :loading="actionLoading && actionType === 'reject'"
          >
            Reject
          </v-btn>
          <v-btn
            color="success"
            variant="elevated"
            prepend-icon="mdi-check-circle"
            @click="handleValidate"
            :loading="actionLoading && actionType === 'validate'"
            class="ml-2"
          >
            Validate
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useStore } from 'effector-vue/composition'
import { 
  $userForms, 
  $isLoading, 
  $error, 
  fetchUserFormsFx, 
  validateFormFx,
  rejectValidationFx,
  resetError,
  UserFormEntry,
  $page,
  $pageSize,
  $userFormsPagination,
  setPage,
  setPageSize
} from '@/stores/userForms'
import * as filloutService from '@/services/fillout'

// Store data
const userForms = useStore($userForms)
const isLoading = useStore($isLoading)
const error = useStore($error)
const pagination = useStore($userFormsPagination)
const currentPage = useStore($page)
const currentPageSize = useStore($pageSize)

// Pagination controls
const pageSizeOptions = [
  { title: '5 items', value: 5 },
  { title: '10 items', value: 10 },
  { title: '20 items', value: 20 },
  { title: '50 items', value: 50 }
]

// Local state
const search = ref('')
const actionLoading = ref(false)
const actionType = ref(null)
const showReviewDialog = ref(false)
const selectedItem = ref(null)
const formData = ref(null)
const isFormDataLoading = ref(false)
const formDataError = ref(null)

// Table headers
const headers = [
  { title: 'User', key: 'userName', sortable: true },
  { title: 'Role', key: 'role', sortable: true },
  { title: 'Fillout ID', key: 'filloutId', sortable: true },
  { title: 'Start Date', key: 'startDate', sortable: true },
  { title: 'Complete Date', key: 'completeDate', sortable: true },
  { title: 'Request Date', key: 'requestedDate', sortable: true },
  { title: 'Validated Date', key: 'validatedDate', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false },
]

// Format date for display
function formatDate(dateString: string) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

// Format field value for display
function formatFieldValue(value) {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

// Get status text based on entry state
function getStatusText(item: UserFormEntry): string {
  if (item.validatedDate) return 'Validated'
  if (item.requestedDate) return 'Requested'
  if (item.completeDate) return 'Completed'
  return 'In Progress'
}

// Get status color based on entry state
function getStatusColor(item: UserFormEntry): string {
  if (item.validatedDate) return 'success'
  if (item.requestedDate) return 'info'
  if (item.completeDate) return 'primary'
  return 'warning'
}

// Open review dialog
async function openReviewDialog(item: UserFormEntry) {
  selectedItem.value = item
  showReviewDialog.value = true
  formData.value = null
  formDataError.value = null
  
  await fetchFormData(item)
}

// Fetch form data for the selected item
async function fetchFormData(item: UserFormEntry) {
  isFormDataLoading.value = true
  formDataError.value = null
  
  try {
    const response = await filloutService.getFilloutData(item.filloutId)
    formData.value = response.submission_data || []
  } catch (err) {
    console.error('Error fetching form data:', err)
    formDataError.value = 'Failed to load form data. Please try again.'
  } finally {
    isFormDataLoading.value = false
  }
}

// Handle validate action from dialog
async function handleValidate() {
  if (!selectedItem.value) return
  
  actionLoading.value = true
  actionType.value = 'validate'
  
  try {
    await validateFormFx({
      filloutId: selectedItem.value.filloutId,
      userId: selectedItem.value.userId
    })
    showReviewDialog.value = false
  } finally {
    actionLoading.value = false
    actionType.value = null
  }
}

// Handle reject action from dialog
async function handleReject() {
  if (!selectedItem.value) return
  
  actionLoading.value = true
  actionType.value = 'reject'
  
  try {
    await rejectValidationFx({
      filloutId: selectedItem.value.filloutId,
      userId: selectedItem.value.userId
    })
    showReviewDialog.value = false
  } finally {
    actionLoading.value = false
    actionType.value = null
  }
}

// Handle pagination changes
function handlePageChange(newPage: number) {
  setPage(newPage)
}

function handlePageSizeChange(newSize: number) {
  setPageSize(newSize)
}

// Watch for page or pageSize changes
watch([$page, $pageSize], () => {
  fetchUserFormsFx({
    page: Number(currentPage),
    page_size: Number(currentPageSize)
  })
})

// Refresh data
function refreshData() {
  // Reset to page 1 when refreshing
  setPage(1)
  fetchUserFormsFx({
    page: 1,
    page_size: Number(currentPageSize)
  })
}

// Load data on component mount
onMounted(() => {
  fetchUserFormsFx({
    page: Number(currentPage),
    page_size: Number(currentPageSize)
  })
})
</script>

<style scoped>
.fillout-form-data {
  max-height: 400px;
  overflow-y: auto;
}
</style> 