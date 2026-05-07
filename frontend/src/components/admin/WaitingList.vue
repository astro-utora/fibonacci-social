<template>
  <div>
    <h2 class="text-h4 mb-4">Waiting List</h2>
    
    <v-card>
      <v-data-table
        :headers="headers"
        :items="waitingList"
        :loading="loading"
        :no-data-text="noDataText"
        class="elevation-1"
        :items-per-page="-1"
        hide-default-footer
      >
        <template v-slot:top>
          <v-toolbar flat>
            <v-toolbar-title>Users Waiting for Approval</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-select
              v-model="statusFilter"
              :items="statusOptions"
              label="Filter by status"
              density="compact"
              style="max-width: 200px"
              class="ml-4 mt-4"
              @update:model-value="handleStatusFilterChange"
            ></v-select>
            <v-btn
              color="primary"
              class="ml-2 mt-4"
              @click="refreshData"
              :loading="loading"
              prepend-icon="mdi-refresh"
            >
              Refresh
            </v-btn>
          </v-toolbar>
        </template>
        
        <template v-slot:item.created_at="{ item }">
          {{ formatDate(item.created_at) }}
        </template>
        
        <template v-slot:item.approved_at="{ item }">
          {{ item.approved_at ? formatDate(item.approved_at) : '-' }}
        </template>
        
        <template v-slot:item.actions="{ item }">
          <div class="d-flex justify-end">
            <v-btn
              v-if="item.status === 'pending'"
              density="compact"
              color="success"
              variant="text"
              @click="approveUser(item)"
              :loading="processingUsers[item.user_id]"
              class="mr-2"
            >
              Approve
            </v-btn>
            <v-btn
              v-if="item.status === 'pending'"
              density="compact"
              color="error"
              variant="text"
              @click="rejectUser(item)"
              :loading="processingUsers[item.user_id]"
            >
              Reject
            </v-btn>
            <v-chip
              v-else
              :color="item.status === 'approved' ? 'success' : 'error'"
              small
            >
              {{ item.status === 'approved' ? 'Approved' : 'Rejected' }}
            </v-chip>
          </div>
        </template>
      </v-data-table>
      
      <!-- Pagination controls -->
      <div class="d-flex align-center px-4 py-2">
        <v-select
          v-model="pageSize"
          :items="pageSizeOptions"
          label="Items per page"
          density="compact"
          hide-details
          variant="outlined"
          style="max-width: 150px"
          class="mr-4"
          @update:model-value="handlePageSizeChange"
        ></v-select>
        
        <v-spacer></v-spacer>
        
        <v-pagination
          v-if="pagination && pagination.total_pages > 0"
          v-model="page"
          :length="pagination.total_pages"
          :total-visible="7"
          rounded
          @update:modelValue="handlePageChange"
        ></v-pagination>
      </div>
    </v-card>
    
    <!-- Confirmation Dialog -->
    <v-dialog v-model="showConfirmDialog" max-width="500px">
      <v-card>
        <v-card-title>Confirm {{ actionType }}</v-card-title>
        <v-card-text>
          Are you sure you want to {{ actionType.toLowerCase() }} user {{ selectedUser?.user_name || selectedUser?.email || 'Unknown' }}?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="showConfirmDialog = false">Cancel</v-btn>
          <v-btn 
            :color="actionType === 'Approve' ? 'success' : 'error'" 
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
import { ref, onMounted, reactive, computed, watch } from 'vue'
import { useStore } from 'effector-vue/composition'
import { 
  $waitingListItems,
  $waitingListPagination,
  $page,
  $pageSize,
  $statusFilter,
  setPage,
  setPageSize,
  setStatusFilter,
  fetchWaitingListFx,
  approveUserFx,
  rejectUserFx,
  WaitingListEntry
} from '@/stores/waitingList'
import { format } from 'date-fns'

// Table headers
const headers = [
  { title: 'Name', key: 'user_name', sortable: true },
  { title: 'Email', key: 'email', sortable: true },
  { title: 'Registration Date', key: 'created_at', sortable: true },
  { title: 'Approval Date', key: 'approved_at', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
]

// Connect to Effector stores
const waitingList = useStore($waitingListItems)
const pagination = useStore($waitingListPagination)
const page = useStore<number>($page)
const pageSize = useStore<number>($pageSize)
const statusFilter = useStore<string>($statusFilter)

// Local state
const loading = ref(false)
const pageSizeOptions = [
  { title: '5 items', value: 5 },
  { title: '10 items', value: 10 },
  { title: '20 items', value: 20 },
  { title: '50 items', value: 50 }
]
const statusOptions = [
  { title: 'All', value: '' },
  { title: 'Pending', value: 'pending' },
  { title: 'Approved', value: 'approved' },
  { title: 'Rejected', value: 'rejected' }
]
const processingUsers = reactive<Record<string, boolean>>({})
const selectedUser = ref<WaitingListEntry | null>(null)
const showConfirmDialog = ref(false)
const actionType = ref('')
const processingConfirm = ref(false)
const showError = ref(false)
const errorMessage = ref('')

// Computed
const noDataText = computed(() => {
  return loading.value 
    ? 'Loading...' 
    : 'No users in waiting list'
})

// Methods
function handlePageChange(newPage: number) {
  setPage(newPage)
}

function handlePageSizeChange(newPageSize: number) {
  setPageSize(newPageSize)
}

function handleStatusFilterChange(newStatus: string) {
  setStatusFilter(newStatus)
}

function refreshData() {
  // The data will be automatically refreshed through the Effector store
  // Just reset the page to 1 to ensure we're seeing the most recent data
  setPage(1)
}

function formatDate(dateString: string) {
  try {
    return format(new Date(dateString), 'MMM dd, yyyy HH:mm')
  } catch {
    return dateString
  }
}

function approveUser(user: WaitingListEntry) {
  selectedUser.value = user
  actionType.value = 'Approve'
  showConfirmDialog.value = true
}

function rejectUser(user: WaitingListEntry) {
  selectedUser.value = user
  actionType.value = 'Reject'
  showConfirmDialog.value = true
}

async function confirmAction() {
  if (!selectedUser.value) return
  
  processingConfirm.value = true
  processingUsers[selectedUser.value.user_id] = true
  
  try {
    if (actionType.value === 'Approve') {
      await approveUserFx(selectedUser.value.user_id)
    } else {
      await rejectUserFx(selectedUser.value.user_id)
    }
    
    // Close dialog
    showConfirmDialog.value = false
  } catch (error: any) {
    showError.value = true
    errorMessage.value = error.message || `Failed to ${actionType.value.toLowerCase()} user`
  } finally {
    processingConfirm.value = false
    processingUsers[selectedUser.value.user_id] = false
  }
}

// Add onMounted hook to fetch data when component loads
onMounted(() => {
  fetchWaitingListFx({ 
    page: page.value,
    page_size: pageSize.value,
    status: statusFilter.value || undefined
  })
})
</script> 