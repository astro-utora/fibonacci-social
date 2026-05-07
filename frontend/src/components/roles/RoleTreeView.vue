<template>
  <div class="role-tree-container">
    <div class="role-tree">
      <!-- First row shows all root elements -->
      <RolesRow
        v-if="rootRoles.length > 0"
        :roles="rootRoles"
        :selected-role="selectedRolesPath[0] || ''"
        @selectRole="selectRole(0, $event)"
        :force-expand="true"
        :hide-expand-button="true"
        class="role-row"
      />
      
      <!-- Subsequent rows show subroles based on selection -->
      <template v-for="(roles, index) in subroleRows" :key="index">
        <RolesRow
          v-if="roles.length"
          :roles="roles"
          :selected-role="selectedRolesPath[index + 1] || ''"
          :force-expand="index + 1 === selectedRolesPath.length"
          @selectRole="selectRole(index + 1, $event)"
          class="role-row subroles-row"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, DeepReadonly, onMounted } from 'vue'
import RolesRow from './RolesRow.vue'
import type { SubRole } from '@/types'
import { useStore } from 'effector-vue/composition'
import { $filloutSubmissions, FilloutSubmission } from '@/stores/fillout'

const props = defineProps<{
  tree: DeepReadonly<SubRole[]>
  previewMode?: boolean
}>()

const submissions = useStore<FilloutSubmission[]>($filloutSubmissions)

// Initialize with empty selection path
const selectedRolesPath = ref<string[]>([])

// The root roles are just the top level roles from the tree
const rootRoles = computed(() => props.tree || [])

// The subrole rows are the nested levels based on selection
const subroleRows = computed(() => {
  return generateSubroleRows()
})

// Determine if subroles should be shown for a given role
function showSubroles(role: DeepReadonly<SubRole>) {
  return props.previewMode || !(role.filloutId && getSubmissionStatus(role) !== 'validated')
}

// When component mounts, select the first root if no selection exists
function initializeSelection() {
  if (props.tree.length > 0 && selectedRolesPath.value.length === 0) {
    // Only auto-select if there's exactly one root
    if (props.tree.length === 1) {
      selectedRolesPath.value = [props.tree[0].role]
    }
  }
}

onMounted(() => {
  initializeSelection()
})

// Generate all rows of subroles based on current selection
function generateSubroleRows() {
  const rows: DeepReadonly<SubRole[]>[] = []
  
  // If no selection, return empty array
  if (selectedRolesPath.value.length === 0) return rows
  
  // Find the selected root role
  const selectedRoot = props.tree.find(role => role.role === selectedRolesPath.value[0])
  if (!selectedRoot) return rows
  
  // Navigate through the tree based on selection
  let currentNode: DeepReadonly<SubRole> = selectedRoot

  // Start from the root (index 0) and traverse down
  for (let i = 0; i < selectedRolesPath.value.length; i++) {
    // For the first level (root), we've already found the node
    if (i === 0) {
      if (showSubroles(currentNode)) {
        rows.push(currentNode.subroles)
      }
      continue
    }
    
    // For subsequent levels, find the child node
    const selectedRole = selectedRolesPath.value[i]
    const nextNode = currentNode.subroles.find(role => role.role === selectedRole)
    if (!nextNode) break
    
    currentNode = nextNode
    
    // Add subroles to rows if conditions are met
    if (showSubroles(currentNode)) {
      rows.push(currentNode.subroles)
    } else {
      break
    }
  }
  
  return rows
}

// Get submission status for a role
function getSubmissionStatus(role: DeepReadonly<SubRole>): 'started' | 'completed' | 'requested' | 'validated' | null {
  if (!role.filloutId) return null
  const submission = submissions.value.find(s => s.filloutId === role.filloutId)
  if (!submission) return null
  
  return submission.status
}

// Handle selecting a role at a given level
function selectRole(level: number, roleName: string) {
  // If selecting at the top level
  if (level === 0) {
    // If same role selected, do nothing
    if (selectedRolesPath.value[0] === roleName) {
      return
    }
    
    // Otherwise reset path and select new root
    selectedRolesPath.value = [roleName]
    return
  }
  
  // For deeper levels
  if (selectedRolesPath.value[level] === roleName) {
    // Clicking the same role should collapse its children
    selectedRolesPath.value = selectedRolesPath.value.slice(0, level + 1)
    return
  }
  
  // Selecting a different role at this level
  // Truncate path at the current level and add the new selection
  selectedRolesPath.value = selectedRolesPath.value.slice(0, level)
  selectedRolesPath.value[level] = roleName
}
</script>

<style scoped>
.role-tree-container {
  overflow-x: hidden;
  overflow-y: auto;
  padding-right: 16px; /* Space for scrollbar */
}

.role-tree {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.role-row {
  width: 100%;
}

.subroles-row {
  margin-left: 24px;
}

/* Custom scrollbar styling */
.role-tree-container::-webkit-scrollbar {
  width: 8px;
}

.role-tree-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.role-tree-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.role-tree-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Firefox scrollbar */
.role-tree-container {
  scrollbar-width: thin;
  scrollbar-color: #888 #f1f1f1;
}
</style> 