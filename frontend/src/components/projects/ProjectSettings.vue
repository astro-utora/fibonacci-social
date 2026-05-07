<template>
  <v-container fluid class="fill-height pa-0">
    <v-row class="fill-height ma-0">
      <v-col cols="12" class="fill-height pa-0">
        <NavigationPanel
          :title="projectTitle"
          :items="navigationItems"
          :mode="navigationMode"
          class="fill-height"
        >
          <template #actions>
            <v-btn
              variant="text"
              prepend-icon="mdi-arrow-left"
              @click="router.back()"
            >
              Back
            </v-btn>
          </template>

          <!-- General Tab -->
          <template #general>
            <v-form class="mt-4">
              <v-text-field
                v-model="projectName"
                label="Project Name"
                required
                :rules="[(v: string) => !!v || 'Project name is required']"
              ></v-text-field>
              
              <v-switch
                v-model="allowGuests"
                label="Allow guest access"
                hint="When enabled, non-members can view this project"
                persistent-hint
                class="mt-4"
              ></v-switch>
              
              <v-btn
                color="primary"
                class="mt-4"
                :loading="isSaving"
                :disabled="!isProjectNameModified && !isAllowGuestsModified"
                @click="saveGeneralSettings"
              >
                Save Changes
              </v-btn>
            </v-form>
          </template>
          
          <!-- Role Tree Tab -->
          <template #roles>
            <role-tree-editor-panel
              :project-id="projectId"
              description="Define the role tree for this project. Users will see this tree when they access your project."
              :is-admin="false"
              class="fill-height"
            />
          </template>
          
          <!-- Users Tab -->
          <template #users>
            <project-members 
              :projectId="projectId" 
              ref="membersComponent"
              @refresh="handleMembersRefresh"
              class="fill-height"
            />
          </template>
          
          <!-- Settings Tab -->
          <template #settings>
            <div class="fill-height">
              <SettingsTable
                title="Project Settings"
                :settings="projectSettings"
                :loading="settingsLoading"
                :error="settingsError"
                keyLabel="Setting"
                valueLabel="Value"
                descriptionLabel="Description"
                @refresh="loadProjectSettings"
                @update="updateProjectSetting"
              />
            </div>
          </template>
        </NavigationPanel>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'effector-vue/composition'
import { 
  $activeProject,
  $projectRoleTree,
  $projectRoleTreeLoading,
  $projectRoleTreeError,
  loadProjectRoleTreeFx,
  loadProjectFx,
  updateProjectFx
} from '@/stores/project'
import * as projectService from '@/services/project'
import type { Project } from '@/types/project'
import type { SubRole } from '@/types'
import type { NavigationItem } from '@/types/navigation'
import NavigationPanel from '@/components/common/NavigationPanel.vue'
import SettingsTable from '../common/SettingsTable.vue'
import RoleTreeView from '@/components/roles/RoleTreeView.vue'
import { validateRoleTree } from '@/services/roleTree'
import RoleTreeEditorPanel from '@/components/roles/RoleTreeEditorPanel.vue'
import ProjectMembers from '@/components/projects/ProjectMembers.vue'

const route = useRoute()
const router = useRouter()
const activeProject = useStore<Project | null>($activeProject)

// Navigation settings
const navigationMode = ref<'vertical' | 'tabs'>('vertical')
const navigationItems: NavigationItem[] = [
  { label: 'General', value: 'general', icon: 'mdi-tune' },
  { label: 'Role Tree', value: 'roles', icon: 'mdi-file-tree' },
  { label: 'Members', value: 'users', icon: 'mdi-account-group' },
  { label: 'Settings', value: 'settings', icon: 'mdi-cog' }
]

const projectId = computed(() => route.params.id as string)
const projectName = ref('')
const allowGuests = ref(false)
const projectRoleTree = ref<SubRole | null>(null)
const isSaving = ref(false)

// Project settings
const projectSettings = ref<any[]>([])
const settingsLoading = ref(false)
const settingsError = ref('')

// Initialize
onMounted(async () => {
  // Load project details if not already in store
  if (!activeProject.value || activeProject.value.id !== projectId.value) {
    try {
      await loadProjectFx(projectId.value)
    } catch (e) {
      console.error('Failed to load project details', e)
    }
  }
  
  // Update project name and settings from active project
  if (activeProject.value) {
    projectName.value = activeProject.value.project_name
    allowGuests.value = activeProject.value.allow_guests
  }
  
  // Load project role tree if not done automatically
  try {
    await loadProjectRoleTreeFx(projectId.value)
  } catch (e) {
    console.error('Failed to load project role tree', e)
  }
  
  // Load other project data
  try {
    await Promise.all([
      loadProjectSettings()
    ])
    
    // Load members after component is mounted
    setTimeout(() => {
      if (membersComponent.value) {
        // @ts-ignore - TS doesn't know about the loadMembers method
        membersComponent.value.loadMembers();
      }
    }, 100);
  } catch (e) {
    console.error('Failed to load project data', e)
  }
})

// Update the computed property to use the local input field value
const projectTitle = computed(() => {
  return projectName.value 
    ? `Project Settings: ${projectName.value}` 
    : activeProject.value?.project_name 
      ? `Project Settings: ${activeProject.value.project_name}` 
      : 'Project Settings';
});

// Track if the project name has been modified from the original
const isProjectNameModified = computed(() => {
  return activeProject.value && projectName.value !== activeProject.value.project_name;
});

// Track if the allow_guests setting has been modified
const isAllowGuestsModified = computed(() => {
  return activeProject.value && allowGuests.value !== activeProject.value.allow_guests;
});

// Actions
async function loadProjectRoleTree() {
  try {
    const treeData = await projectService.fetchProjectRoleTree(projectId.value)
    projectRoleTree.value = treeData.root
  } catch (e) {
    console.error('Failed to load project role tree', e)
  }
}

async function loadProjectSettings() {
  settingsLoading.value = true
  settingsError.value = ''
  
  try {
    // Call the API to get project settings
    const settings = await projectService.getProjectSettings(projectId.value)
    projectSettings.value = settings
  } catch (e: any) {
    settingsError.value = e.message || 'Failed to load project settings'
    console.error('Failed to load project settings:', e)
  } finally {
    settingsLoading.value = false
  }
}

async function saveGeneralSettings() {
  isSaving.value = true;
  try {
    // Use the store effect to update the project and automatically update the store
    await updateProjectFx({
      id: projectId.value,
      data: { 
        project_name: projectName.value,
        allow_guests: allowGuests.value
      }
    });
    
    // Show a success notification (if you have a notification system)
    console.log('Project settings saved successfully');
  } catch (e) {
    console.error('Failed to save settings', e);
    // Optionally show an error notification
  } finally {
    isSaving.value = false;
  }
}

async function handleRoleTreeSave(data: any) {
  try {
    await projectService.saveProjectRoleTree(projectId.value, data.root)
    projectRoleTree.value = data.root
  } catch (e) {
    console.error('Failed to save role tree', e)
    throw new Error('Failed to save project role tree')
  }
}

function handleRoleTreeError(errorMessage: string) {
  console.error(errorMessage)
  // You can handle the error here, e.g., show a notification
}

async function updateProjectSetting(key: string, data: any) {
  settingsLoading.value = true
  
  try {
    // Call the API to update the setting
    const updatedSetting = await projectService.updateProjectSetting(
      projectId.value,
      key,
      data.value.toString()
    )
    
    // Update local data
    const index = projectSettings.value.findIndex((s: any) => s.key === key)
    if (index >= 0) {
      projectSettings.value[index] = updatedSetting
    }
    
    // Success notification would go here
    console.log(`Updated project setting: ${key}`, updatedSetting)
  } catch (e: any) {
    settingsError.value = e.message || 'Failed to update setting'
    console.error(`Failed to update setting ${key}:`, e)
  } finally {
    settingsLoading.value = false
  }
}

const membersComponent = ref(null)

function handleMembersRefresh() {
  if (membersComponent.value) {
    // @ts-ignore - TS doesn't know about the loadMembers method
    membersComponent.value.loadMembers();
  }
}
</script>

<style scoped>
.fill-height {
  height: 100%;
}
</style>
