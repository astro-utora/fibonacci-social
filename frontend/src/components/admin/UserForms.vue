<template>
  <div>
    <h2 class="text-h4 mb-4">User Forms</h2>
    
    <v-card class="elevation-1">
      <v-data-table
        :headers="headers"
        :items="userForms"
        :loading="isLoading"
        :no-data-text="noDataText"
        :items-per-page="-1"
        hide-default-footer
      >
        <template v-slot:top>
          <v-toolbar flat>
            <v-toolbar-title>User Form Submissions</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              class="mt-4"
              @click="refreshData"
              :loading="isLoading"
              prepend-icon="mdi-refresh"
            >
              Refresh
            </v-btn>
          </v-toolbar>
        </template>
        
        <template v-slot:item.startDate="{ item }">
          {{ formatDate(item.startDate) }}
        </template>
        
        <template v-slot:item.completeDate="{ item }">
          {{ item.completeDate ? formatDate(item.completeDate) : '-' }}
        </template>
        
        <template v-slot:item.requestedDate="{ item }">
          {{ item.requestedDate ? formatDate(item.requestedDate) : '-' }}
        </template>
        
        <template v-slot:item.validatedDate="{ item }">
          {{ item.validatedDate ? formatDate(item.validatedDate) : '-' }}
        </template>
        
        <template v-slot:item.actions="{ item }">
          <div class="d-flex justify-end">
            <v-btn
              v-if="item.requestedDate && !item.validatedDate"
              density="compact"
              color="success"
              variant="text"
              @click="validateForm(item)"
              :loading="processingForms[item.id]"
              class="mr-2"
            >
              Validate
            </v-btn>
            <v-btn
              v-if="item.requestedDate && !item.validatedDate"
              density="compact"
              color="error"
              variant="text"
              @click="rejectValidation(item)"
              :loading="processingForms[item.id]"
            >
              Reject
            </v-btn>
            <v-chip
              v-else-if="item.validatedDate"
              color="success"
              small
            >
              Validated
            </v-chip>
            <span v-else>-</span>
          </div>
        </template>
      </v-data-table>
      
      <!-- Pagination controls -->
      <div class="d-flex px-4 py-2 justify-center">
        <v-pagination
          v-model="page"
          :length="pagination.total_pages"
          :total-visible="7"
          @update:modelValue="handlePageChange"
        ></v-pagination>
        
        <v-select
          v-model="pageSize"
          :items="pageSizeOptions"
          label="Items per page"
          density="compact"
          style="max-width: 150px"
          class="ml-4"
          @update:model-value="handlePageSizeChange"
        ></v-select>
      </div>
    </v-card>
    
    <!-- Confirmation Dialog -->
    <v-dialog v-model="showConfirmDialog" max-width="500px">
      <v-card>
        <v-card-title>Confirm {{ actionType }}</v-card-title>
        <v-card-text>
          Are you sure you want to {{ actionType.toLowerCase() }} the form submission for user {{ selectedForm?.userName || 'Unknown' }}?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="showConfirmDialog = false">Cancel</v-btn>
          <v-btn 
            :color="actionType === 'Validate' ? 'success' : 'error'" 
            variant="text" 
            @click="confirmAction"
            :loading="processingConfirm"
          >
            Confirm
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Error Snackbar -->
    <v-snackbar
      v-model="showError"
      color="error"
      timeout="3000"
    >
      {{ errorMessage }}
      <template v-slot:actions>
        <v-btn
          variant="text"
          @click="showError = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'effector-vue/composition'
import { 
  $userFormItems,
  $userFormsPagination, 
  $page,
  $pageSize,
  setPage,
  setPageSize,
  validateFormFx, 
  rejectValidationFx,
  UserFormEntry 
} from '@/stores/userForms'
import { format } from 'date-fns'

// Table headers
const headers = [
  { title: 'User', key: 'userName', sortable: true },
  { title: 'Role', key: 'role', sortable: true },
  { title: 'Started', key: 'startDate', sortable: true },
  { title: 'Completed', key: 'completeDate', sortable: true },
  { title: 'Requested', key: 'requestedDate', sortable: true },
  { title: 'Validated', key: 'validatedDate', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
]

// Connect to Effector stores
const userForms = useStore($userFormItems)
const pagination = useStore($userFormsPagination)
const page = useStore($page)
const pageSize = useStore($pageSize)

// Local state
const isLoading = ref(false)
const pageSizeOptions = [
  { title: '5 items', value: 5 },
  { title: '10 items', value: 10 },
  { title: '20 items', value: 20 },
  { title: '50 items', value: 50 }
]
const processingForms = reactive<Record<string, boolean>>({})
const selectedForm = ref<UserFormEntry | null>(null)
const showConfirmDialog = ref(false)
const actionType = ref('')
const processingConfirm = ref(false)
const showError = ref(false)
const errorMessage = ref('')

// Computed
const noDataText = computed(() => {
  return isLoading.value 
    ? 'Loading...' 
    : 'No form submissions found'
})

// Methods
function handlePageChange(newPage: number) {
  setPage(newPage)
}

function handlePageSizeChange(newPageSize: number) {
  setPageSize(newPageSize)
}

function refreshData() {
  // Reset to page 1 to ensure we're seeing the most recent data
  setPage(1)
}

function formatDate(dateString: string) {
  try {
    return format(new Date(dateString), 'MMM dd, yyyy HH:mm')
  } catch {
    return dateString
  }
}

function validateForm(form: UserFormEntry) {
  selectedForm.value = form
  actionType.value = 'Validate'
  showConfirmDialog.value = true
}

function rejectValidation(form: UserFormEntry) {
  selectedForm.value = form
  actionType.value = 'Reject'
  showConfirmDialog.value = true
}

async function confirmAction() {
  if (!selectedForm.value) return
  
  processingConfirm.value = true
  processingForms[selectedForm.value.id] = true
  
  try {
    const params = {
      userId: selectedForm.value.userId,
      filloutId: selectedForm.value.filloutId
    }
    
    if (actionType.value === 'Validate') {
      await validateFormFx(params)
    } else {
      await rejectValidationFx(params)
    }
    
    // Close dialog
    showConfirmDialog.value = false
  } catch (error: any) {
    showError.value = true
    errorMessage.value = error.message || `Failed to ${actionType.value.toLowerCase()} form`
  } finally {
    processingConfirm.value = false
    processingForms[selectedForm.value.id] = false
  }
}
</script> 