<template>
  <div class="role-tree-editor-panel">
    <p v-if="description" class="text-body-1 mb-4">
      {{ description }}
    </p>
    
    <v-alert
      v-if="error"
      type="error"
      class="mb-4"
    >
      {{ error }}
    </v-alert>
    
    <v-row class="editor-row">
      <v-col cols="12" md="6" class="editor-col">
        <v-card class="editor-card">
          <v-card-title class="d-flex align-center">
            <span>Role Tree Editor</span>
          </v-card-title>
          <v-card-text class="editor-content">
            <!-- Use our updated HJSON editor component -->
            <hjson-editor
              v-if="jsonContent.length > 0"
              v-model="jsonContent"
              :error-messages="validationError"
              label="Role Tree Structure"
              :loading="isLoading"
              @validate="validateJson"
              placeholder="Enter your role tree structure here..."
              class="hjson-editor-wrapper"
            />
            <div class="d-flex justify-end align-center mt-2">
              <v-btn
                :disabled="!!validationError || isSaving"
                :loading="isSaving"
                color="primary"
                @click="handleSave"
              >
                Save Role Tree
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="6" class="preview-col">
        <v-card class="preview-card">
          <v-card-title>Preview</v-card-title>
          <v-card-text class="preview-content">
            <div v-if="isLoading" class="d-flex justify-center align-center h-100">
              <v-progress-circular indeterminate />
            </div>
            <div class="preview-wrapper" v-else>
              <role-tree-view
                v-if="previewRoots && previewRoots.length > 0"
                :tree="previewRoots"
                :preview-mode="true"
                :current-path="[]"
              />
              <v-alert
                v-else-if="validationError"
                type="error"
                class="mb-4"
              >
                {{ validationError }}
              </v-alert>
              <v-alert
                v-else
                type="info"
                class="mb-4"
              >
                No role tree defined yet. Enter valid HJSON to see a preview.
              </v-alert>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
// @ts-ignore
import { ref, computed, onMounted, watch } from 'vue'
import { useStore } from 'effector-vue/composition'
import RoleTreeView from './RoleTreeView.vue'
import HjsonEditor from './HjsonEditor.vue'
import { validateRoleTree } from '@/services/roleTree'
import type { SubRole } from '@/types'
import {
  $roleTree, 
  $roleTreeLoading, 
  $roleTreeError,
  saveRoleTreeFx, 
  loadRoleTreeFx
} from '@/stores/roleTree'
import {
  $projectRoleTree,
  $projectRoleTreeLoading,
  $projectRoleTreeError,
  loadProjectRoleTreeFx,
  saveProjectRoleTreeFx
} from '@/stores/project'

// Props for configuration
const props = defineProps<{
  projectId?: string,     // Optional project ID for project-specific role trees
  description?: string,   // Optional description text
  isAdmin?: boolean       // Is this the admin panel version?
}>();

// State
const jsonContent = ref('')
const jsonToSave = ref('')
const validationError = ref<string | null>(null)

// Use appropriate stores based on context (admin or project)
const roleTree = useStore(props.isAdmin ? $roleTree : $projectRoleTree)
const isLoading = useStore(props.isAdmin ? $roleTreeLoading : $projectRoleTreeLoading)
const isSaving = useStore(props.isAdmin ? $roleTreeLoading : $projectRoleTreeLoading)
const error = useStore(props.isAdmin ? $roleTreeError : $projectRoleTreeError)

// Computed preview tree based on JSON content
const previewRoots = computed<SubRole[]>(() => {
  if (validationError.value) return []
  
  try {
    const data = JSON.parse(jsonToSave.value)
    
    // Handle roots array format
    if (data.roots && Array.isArray(data.roots)) {
      return data.roots
    }
    
    // For backward compatibility - convert single root format
    if (data.root) {
      return [data.root]
    }
    
    return []
  } catch {
    return []
  }
})

// Validate JSON whenever it changes
function validateJson(value: string) {
  try {
    jsonToSave.value = value
    const data = JSON.parse(jsonToSave.value)
    
    // Check for roots array
    if (!data.roots) {
      // For backward compatibility
      if (data.root) {
        // Convert to roots array format
        jsonToSave.value = JSON.stringify({ roots: [data.root] }, null, 2)
        // Re-parse with updated format
        data.roots = [data.root]
      } else {
        validationError.value = 'Missing roots array'
        return
      }
    }
    
    if (!Array.isArray(data.roots)) {
      validationError.value = 'roots must be an array'
      return
    }
    
    if (data.roots.length === 0) {
      validationError.value = 'roots array is empty'
      return
    }
    
    // Validate each root
    for (const root of data.roots) {
      const error = validateRoleTree(root)
      if (error) {
        validationError.value = error
        return
      }
    }
    
    validationError.value = null
  } catch (e) {
    validationError.value = 'Invalid JSON format'
  }
}

// Handle save button click
async function handleSave() {
  if (validationError.value) return
  
  try {
    // Parse the JSON to get the data structure
    const data = JSON.parse(jsonToSave.value);
    const rootsArray = data.roots || [];
    
    if (rootsArray.length === 0) {
      validationError.value = 'No role data to save';
      return;
    }
    
    if (props.isAdmin) {
      // Use the admin role tree effects
      await saveRoleTreeFx({ roots: rootsArray })
    } else if (props.projectId) {
      // Use the project role tree effects
      await saveProjectRoleTreeFx({ 
        projectId: props.projectId,
        roots: rootsArray 
      })
    }
  } catch (e) {
    console.error('Failed to save role tree:', e)
  }
}

// Update JSON when role tree changes
watch(roleTree, (newTree: any) => {
  if (!newTree) return
  
  // Always convert to roots format
  if (Array.isArray(newTree)) {
    jsonContent.value = JSON.stringify({ roots: newTree }, null, 2)
  } else {
    // Handle case where it's a single root object
    jsonContent.value = JSON.stringify({ roots: [newTree] }, null, 2)
  }
  
  validateJson(jsonContent.value)
}, { immediate: true })

// Component initialization
onMounted(async () => {
  // Load appropriate role tree based on context
  if (props.isAdmin) {
    try {
      await loadRoleTreeFx()
    } catch (e) {
      console.error('Failed to load role tree:', e)
    }
  } else if (props.projectId) {
    try {
      await loadProjectRoleTreeFx(props.projectId)
    } catch (e) {
      console.error('Failed to load project role tree:', e)
    }
  }
})
</script>

<style scoped>
.role-tree-editor-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-row {
  flex: 1;
  min-height: 0; /* Important for flex child to respect parent's height */
  display: flex;
  height: 100%;
}

.editor-col, .preview-col {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-card, .preview-card {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-content, .preview-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow: hidden;
}

.hjson-editor-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.preview-wrapper {
  flex: 1;
  overflow: auto;
}

/* Make sure all v-card-text containers allow scrolling when needed */
:deep(.v-card-text) {
  display: flex;
  flex-direction: column;
  overflow: auto;
  flex: 1;
}
</style> 