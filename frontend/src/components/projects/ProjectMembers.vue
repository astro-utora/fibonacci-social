<template>
  <div class="project-members">
    <div class="d-flex justify-space-between align-center mb-4">
      <p class="text-body-1 mb-0">
        Manage users who have access to this project.
      </p>
      <v-btn 
        color="primary" 
        prepend-icon="mdi-account-plus"
        @click="showAddMemberDialog = true"
      >
        Add Member
      </v-btn>
    </div>
    
    <!-- Project Members Table -->
    <v-data-table
      v-if="projectMembers.length > 0"
      :headers="memberHeaders"
      :items="projectMembers"
      item-value="id"
      class="mt-4"
      :loading="projectMembersLoading"
    >
      <template v-slot:item.user_name="{ item }">
        {{ item.user_name || 'Unknown User' }}
      </template>
      
      <template v-slot:item.email="{ item }">
        {{ item.email || 'No email available' }}
      </template>
      
      <template v-slot:item.role="{ item }">
        <v-chip :color="getRoleColor(item.role)">{{ item.role }}</v-chip>
      </template>
      
      <template v-slot:item.actions="{ item }">
        <v-btn
          icon
          color="error"
          size="small"
          :disabled="isRemovingMember || item.role === 'owner'"
          :loading="removingMemberId === item.id"
          @click="confirmRemoveMember(item)"
        >
          <v-icon>mdi-delete</v-icon>
          <v-tooltip activator="parent" location="bottom">
            {{ item.role === 'owner' ? 'Cannot remove owner' : 'Remove member' }}
          </v-tooltip>
        </v-btn>
      </template>
    </v-data-table>
    
    <v-alert
      v-else-if="projectMembersLoading"
      type="info"
      class="mt-4"
    >
      Loading project members...
    </v-alert>
    
    <v-alert
      v-else-if="memberError"
      type="error"
      class="mt-4"
    >
      {{ memberError }}
    </v-alert>
    
    <v-alert
      v-else
      type="info"
      class="mt-4"
    >
      No members have been added to this project yet.
    </v-alert>
    
    <!-- Add Member Dialog -->
    <v-dialog v-model="showAddMemberDialog" max-width="500px">
      <v-card>
        <v-card-title>Add Project Member</v-card-title>
        <v-card-text>
          <v-alert v-if="memberError" type="error" class="mb-4">
            {{ memberError }}
          </v-alert>
          
          <v-form @submit.prevent="searchUsers">
            <v-text-field
              v-model="searchEmail"
              label="Search User by Email"
              type="email"
              required
              :rules="[(v: string) => !!v || 'Email is required']"
            ></v-text-field>
            
            <v-btn 
              color="primary" 
              :loading="isSearchingUsers"
              :disabled="!searchEmail"
              @click="searchUsers"
              class="mb-4"
            >
              Search
            </v-btn>
          </v-form>
          
          <v-divider class="my-4"></v-divider>
          
          <div v-if="searchResults.length > 0">
            <p class="text-subtitle-1 mb-2">Search Results:</p>
            <v-list>
              <v-list-item
                v-for="user in searchResults"
                :key="user.uuid"
                @click="selectUser(user)"
              >
                <v-list-item-title>{{ user.name || user.email }}</v-list-item-title>
                <v-list-item-subtitle>{{ user.email }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </div>
          
          <div v-else-if="hasSearched && !isSearchingUsers">
            <v-alert type="info">No users found with that email.</v-alert>
          </div>
          
          <v-divider class="my-4" v-if="selectedUser"></v-divider>
          
          <div v-if="selectedUser" class="mt-4">
            <p class="text-subtitle-1 mb-2">Selected User:</p>
            <v-card variant="outlined" class="mb-4">
              <v-card-text>
                <p><strong>Name:</strong> {{ selectedUser.name || 'N/A' }}</p>
                <p><strong>Email:</strong> {{ selectedUser.email }}</p>
              </v-card-text>
            </v-card>
            
            <v-select
              v-model="newMember.role"
              label="Role"
              :items="availableRoles"
              required
            ></v-select>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeAddMemberDialog">Cancel</v-btn>
          <v-btn 
            color="primary" 
            :loading="isAddingMember"
            :disabled="!selectedUser || !newMember.role"
            @click="addMember"
          >
            Add Member
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Confirm Remove Dialog -->
    <v-dialog v-model="showRemoveDialog" max-width="400px">
      <v-card>
        <v-card-title class="text-h5">Remove Member</v-card-title>
        <v-card-text>
          Are you sure you want to remove 
          <strong>
            {{ 
              selectedMember?.email || 
              selectedMember?.user_name || 
              'this member' 
            }}
          </strong> 
          from this project?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeRemoveMemberDialog">Cancel</v-btn>
          <v-btn 
            color="error" 
            :loading="isRemovingMember"
            @click="removeMember"
          >
            Remove
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useStore } from 'effector-vue/composition'
import { 
  $projectMembers,
  $projectMembersLoading,
  $selectedMember,
  $addingMember,
  $removingMember,
  $projectMembersError,
  fetchProjectMembersFx,
  addProjectMemberFx,
  removeProjectMemberFx,
  setSelectedMember
} from '@/stores/projectMembers'
import * as userService from '@/services/user'
import type { User } from '@/types'
import type { ProjectMember } from '@/types/project'

// Props
const props = defineProps<{
  projectId: string;
}>();

// Emit events
const emit = defineEmits(['refresh']);

// Member management state
const showAddMemberDialog = ref(false);
const showRemoveDialog = ref(false);
const newMember = ref({
  email: '',
  role: 'member',
});
const removingMemberId = ref<string | null>(null);
const availableRoles = ['admin', 'member', 'viewer'];

// Search state
const searchEmail = ref('');
const searchResults = ref<User[]>([]);
const selectedUser = ref<User | null>(null);
const isSearchingUsers = ref(false);
const hasSearched = ref(false);

// Effector stores for project members
const projectMembers = useStore($projectMembers);
const projectMembersLoading = useStore($projectMembersLoading);
const isAddingMember = useStore($addingMember);
const isRemovingMember = useStore($removingMember);
const selectedMember = useStore($selectedMember);
const memberError = useStore($projectMembersError);

// Table headers
const memberHeaders = [
  { title: 'Name', key: 'user_name' },
  { title: 'Email', key: 'email' },
  { title: 'Role', key: 'role' },
  { title: 'Actions', key: 'actions' }
];

// Expose method to load members
const loadMembers = async () => {
  try {
    await fetchProjectMembersFx(props.projectId);
  } catch (e) {
    console.error('Failed to load project members', e);
  }
};

// Method to be called by parent component
defineExpose({
  loadMembers
});

// Functions for member management
function confirmRemoveMember(member: ProjectMember) {
  setSelectedMember(member);
  removingMemberId.value = member.id;
  showRemoveDialog.value = true;
}

function closeRemoveMemberDialog() {
  showRemoveDialog.value = false;
  removingMemberId.value = null;
}

async function removeMember() {
  if (!selectedMember.value) return;
  
  // Retrieve the ID safely
  const memberId = selectedMember.value.user_id;
  if (!memberId) {
    console.error('Selected member has no ID', selectedMember.value);
    return;
  }
  
  try {
    await removeProjectMemberFx({
      projectId: props.projectId,
      memberId
    });
    
    showRemoveDialog.value = false;
    emit('refresh');
  } catch (e) {
    console.error('Failed to remove member', e);
  } finally {
    removingMemberId.value = null;
  }
}

function closeAddMemberDialog() {
  showAddMemberDialog.value = false;
  searchEmail.value = '';
  searchResults.value = [];
  selectedUser.value = null;
  hasSearched.value = false;
  newMember.value = {
    email: '',
    role: 'member'
  };
}

async function addMember() {
  if (!selectedUser.value || !newMember.value.role) {
    return;
  }
  
  try {
    await addProjectMemberFx({
      projectId: props.projectId,
      user_id: selectedUser.value.uuid,
      role: newMember.value.role
    });
    
    // Close dialog
    closeAddMemberDialog();
    emit('refresh');
  } catch (error: any) {
    console.error('Failed to add member:', error);
  }
}

async function searchUsers() {
  if (!searchEmail.value) return;
  
  isSearchingUsers.value = true;
  hasSearched.value = true;
  searchResults.value = [];
  
  try {
    console.log(`Searching for users with email: ${searchEmail.value}`);
    
    const users = await userService.searchUsersByEmail(searchEmail.value);
    
    if (users && users.length > 0) {
      searchResults.value = users;
      console.log(`Found ${users.length} users:`, users);
    } else {
      console.log('No users found matching the search criteria');
    }
  } catch (error) {
    console.error('Failed to search users:', error);
  } finally {
    isSearchingUsers.value = false;
  }
}

function selectUser(user: User) {
  selectedUser.value = user;
}

function getRoleColor(role: string) {
  switch (role.toLowerCase()) {
    case 'owner':
      return 'purple';
    case 'editor':
      return 'primary';
    case 'member':
      return 'green';
    case 'viewer':
      return 'grey';
    default:
      return 'blue';
  }
}
</script>

<style scoped>
.project-members {
  width: 100%;
}
</style> 