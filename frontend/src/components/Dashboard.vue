<template>
  <v-container style="width: 100%; height: 100%;">
    <v-row style="height: 100%;">
      <!-- Profile Section -->
      <v-col cols="12" md="3" lg="3">
        <v-card>
          <v-card-text>
            <UserProfile 
              v-if="profileData"
              :profileData="profileData"
              :preview="false"
            />
            <v-skeleton-loader
              v-else
              type="list-item-three-line@4"
            />
          </v-card-text>
        </v-card>
        
        <!-- User Projects Section -->
        <v-card class="mt-4">
          <v-card-title class="d-flex justify-space-between align-center flex-wrap">
            <span>Your Projects</span>
            <!-- Responsive Create Project button -->
            <v-btn
              color="primary"
              prepend-icon="mdi-plus"
              variant="outlined"
              @click="openCreateProjectDialog"
            >
              New Project
            </v-btn>
          </v-card-title>
          <v-card-text>
            <UserProjects 
              :showTitle="false" 
              :showCreateButton="false"
              @select-project="selectProject"
            />
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Role Tree Section -->
      <v-col cols="12" md="9" lg="9" style="height: 100%;">
        <v-card style="height: 100%;">
          <v-card-title class="d-flex align-center">
            <div>
              {{ activeProject ? activeProject.project_name : 'Your Path Tree' }}
            </div>
            <v-spacer></v-spacer>
            <v-btn
              v-if="activeProject"
              size="small"
              icon
              @click="closeProject"
              class="ml-2"
            >
              <v-icon>mdi-close</v-icon>
              <v-tooltip activator="parent" location="bottom">
                Close Project
              </v-tooltip>
            </v-btn>
          </v-card-title>
          <v-card-text style="height: calc(100% - 48px); display: flex; flex-direction: column;">
            <div v-if="isLoading" class="d-flex justify-center">
              <v-progress-circular indeterminate />
            </div>

            <v-alert
              v-else-if="error"
              type="error"
              class="mb-4"
            >
              {{ error }}
            </v-alert>

            <template v-else>
              <role-tree-view
                v-if="roleTree && roleTree.length > 0"
                :tree="roleTree"
                :current-path="[]"
                :expanded-paths="expandedPaths"
                :submissions="filloutSubmissions"
              />
              <v-alert
                v-else
                type="info"
                class="mb-4"
              >
                No role tree available
              </v-alert>
            </template>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Create Project Dialog -->
    <v-dialog v-model="showCreateProjectDialog" max-width="500px">
      <v-card>
        <v-card-title>Create New Project</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="createProject">
            <v-text-field
              v-model="newProject.name"
              label="Project Name"
              required
              :rules="[(v: string) => !!v || 'Project name is required']"
              :validate-on-blur="true"
            ></v-text-field>
            <v-textarea
              v-model="newProject.description"
              label="Description"
              rows="3"
            ></v-textarea>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" text @click="showCreateProjectDialog = false">Cancel</v-btn>
          <v-btn 
            color="primary" 
            :loading="isCreatingProject" 
            @click="createProject"
          >
            Create
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
// @ts-ignore
import { ref, computed, onMounted, type DeepReadonly } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'effector-vue/composition'
import { $user } from '@/stores/auth'
import { updateProfile } from '@/stores/profile'
import { 
  $roleTree, 
  $roleTreeLoading, 
  $roleTreeError, 
  loadRoleTreeFx,
  $selectedRole,
  selectAndCollapseOthers
} from '@/stores/roleTree'
import { $filloutSubmissions, loadSubmissionsFx, FilloutSubmission } from '@/stores/fillout'
import { 
  $activeProject, 
  selectProject as selectProjectEvent, 
  closeProject as closeProjectEvent,
  createProjectFx
} from '@/stores/project'
import { $credits, loadCreditsFx } from '@/stores/credits'
import UserProfile from './UserProfile.vue'
import RoleTreeView from './roles/RoleTreeView.vue'
import UserProjects from './UserProjects.vue'
import type { ProfileData, User, SubRole } from '@/types'
import type { Project } from '@/types/project'

// Type-safe store usage
const user = useStore<User | null>($user)
const roleTree = useStore<SubRole[] | null>($roleTree)
const roleTreeLoading = useStore<boolean>($roleTreeLoading)
const roleTreeError = useStore<string | null>($roleTreeError)
const selectedRole = useStore<SubRole | null>($selectedRole)
const filloutSubmissions = useStore<FilloutSubmission[]>($filloutSubmissions)
const activeProject = useStore<Project | null>($activeProject)
const credits = useStore<number>($credits)

const router = useRouter()
const error = ref<string | null>(null)
const isLoading = ref(false)
const showCreateProjectDialog = ref(false)
const isCreatingProject = ref(false)
const newProject = ref({
  name: '',
  description: ''
})

// Computed properties
const profileData = computed<ProfileData | null>(() => {
  if (!user.value) return null
  return {
    name: user.value.name,
    location: user.value.location,
    workplace: user.value.workplace,
    role: user.value.role,
    birth_date: user.value.birth_date,
    goals: user.value.goals,
    education: user.value.education,
    referral_code: user.value.referral_code,
    avatar_url: user.value.avatar_url,
    credits: user.value.credits
  }
})

// Actions
function handleRoleSelect(data: { role: SubRole; path: string[] }) {
  selectAndCollapseOthers(data)
}

async function selectProject(project: any) {
  if (!project || !project.id) {
    console.error('Invalid project data', project);
    error.value = 'Invalid project data';
    return;
  }

  isLoading.value = true;
  error.value = null;
  
  try {
    console.log(`Selecting project ${project.id} (${project.project_name})`);
    
    // First select the project in the store
    await selectProjectEvent(project);
    
    // Then load the project-specific role tree
    console.log(`Loading role tree for project ${project.id}`);
    const roleTreeResult = await loadRoleTreeFx({ projectId: project.id });
    console.log('Project role tree loaded:', roleTreeResult);
    
    // Also load any project-specific fillout submissions
    await loadSubmissionsFx({ projectId: project.id });
  } catch (e) {
    console.error('Error loading project data:', e);
    error.value = 'Failed to load project data';
  } finally {
    isLoading.value = false;
  }
}

async function closeProject() {
  isLoading.value = true;
  try {
    // First close the project
    await closeProjectEvent();
    
    // Then reload the main role tree
    await loadRoleTreeFx();
    
    // Also reload the main fillout submissions
    await loadSubmissionsFx();
  } catch (e) {
    error.value = 'Failed to load data';
    console.error('Error loading data:', e);
  } finally {
    isLoading.value = false;
  }
}

function navigateToProjectSettings(projectId: string) {
  router.push(`/project-settings/${projectId}`)
}

function openCreateProjectDialog() {
  // Reset form fields
  newProject.value = {
    name: '',
    description: ''
  }
  showCreateProjectDialog.value = true
}

async function createProject() {
  if (!newProject.value.name) return
  
  isCreatingProject.value = true
  try {
    // Use the Effector effect instead of direct API call
    const createdProject = await createProjectFx({
      project_name: newProject.value.name,
      description: newProject.value.description
    })
    
    // Close dialog
    showCreateProjectDialog.value = false
    
    // The project list will be automatically refreshed by the store
    // through the createProjectFx.done sample
    
    // Optionally select the newly created project
    selectProject(createdProject)
  } catch (error) {
    console.error('Failed to create project:', error)
    // Show error notification
  } finally {
    isCreatingProject.value = false
  }
}

// Initialize
onMounted(async () => {
  isLoading.value = true;
  try {
    // Load user credits
    await loadCreditsFx();
  } catch (e) {
    console.error('Error loading credits:', e);
    error.value = 'Failed to load credits';
  }

  try {
    
    // Check if we already have an active project
    if (activeProject.value) {
      // If a project is active, load the project-specific role tree
      await loadRoleTreeFx({ projectId: activeProject.value.id });
      
      // Also load the project-specific fillout submissions
      await loadSubmissionsFx({ projectId: activeProject.value.id });
    } else {
      // Otherwise, load the main role tree
      await loadRoleTreeFx();
      
      // And the main fillout submissions
      await loadSubmissionsFx();
    }
  } catch (e) {
    console.error('Error initializing dashboard:', e);
    error.value = 'Failed to load data';
  } finally {
    isLoading.value = false;
  }
});

// Compute expanded paths based on submissions
const expandedPaths = computed(() => {
  if (!roleTree.value || !filloutSubmissions.value.length) return []
  
  const paths: string[][] = []
  
  function findFilloutPaths(node: DeepReadonly<SubRole>, currentPath: string[]) {
    if (node.filloutId) {
      const submission = filloutSubmissions.value.find(
        s => s.filloutId === node.filloutId
      )
      if (submission) {
        paths.push(currentPath)
      }
    }
    
    node.subroles.forEach((subrole: DeepReadonly<SubRole>) => {
      findFilloutPaths(subrole, [...currentPath, node.role])
    })
  }
  
  for (const role of roleTree.value) {
    findFilloutPaths(role, [])
  }
  return paths
})
</script> 