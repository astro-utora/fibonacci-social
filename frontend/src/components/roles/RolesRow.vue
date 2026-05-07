<template>
  <div class="roles-row">
    <div class="roles-container">
      <div class="roles-scroll">
        <!-- Active Roles -->
        <div class="roles-list">
          <RoleCard
            v-for="role in activeRoles"
            :key="role.role"
            :role="role"
            :is-selected="selectedRole === role.role"
            @select="selectRole"
          />

          <!-- Inactive Roles (shown when expanded) -->
          <transition-group name="slide">
            <RoleCard
              v-for="role in visibleInactiveRoles"
              :key="role.role"
              :role="role"
              :is-selected="selectedRole === role.role"
              @select="selectRole"
            />

            <!-- Expansion Button -->
            <v-btn
              v-if="!hideExpandButton && inactiveRoles.length > 0"
              :key="'expand-btn'"
              variant="outlined"
              class="expand-btn"
              @click="expanded = !expanded"
            >
              <v-icon>{{ expanded ? 'mdi-chevron-left' : 'mdi-chevron-right' }}</v-icon>
              {{ expanded ? '' : `+${inactiveRoles.length}` }}
            </v-btn>
          </transition-group>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useStore } from 'effector-vue/composition'
import { $filloutSubmissions, FilloutSubmission } from '@/stores/fillout'
import type { SubRole } from '@/types'
import RoleCard from './RoleCard.vue'

const props = defineProps<{
  roles: SubRole[],
  selectedRole: string,
  forceExpand: boolean,
  hideExpandButton: boolean
}>()

const emit = defineEmits<{
  selectRole: [role: string]
}>()

const expanded = ref(props.forceExpand)
const submissions = useStore<FilloutSubmission[]>($filloutSubmissions)

function getSubmissionStatus(role: SubRole): 'started' | 'completed' | 'requested' | null {
  if (!role.filloutId) return null
  const submission = submissions.value.find(s => s.filloutId === role.filloutId)
  return submission?.status || null
}

const activeRoles = computed(() => 
  props.roles.filter((role) => {
    if (!expanded.value && role.role === props.selectedRole) return true
    const status = getSubmissionStatus(role)
    return status === 'started' || status === 'completed' || status === 'requested'
  })
)

const inactiveRoles = computed(() => 
  props.roles.filter((role) => {
    if (!expanded.value && role.role === props.selectedRole) return false
    const status = getSubmissionStatus(role)
    return status !== 'started' && status !== 'completed' && status !== 'requested'
  })
)

const visibleInactiveRoles = computed(() => 
  expanded.value ? inactiveRoles.value : []
)

function selectRole(role: SubRole) {
  emit('selectRole', role.role)
}
</script>

<style scoped>
.roles-row {
  padding: 16px 0;
  position: relative;
}

.roles-container {
  position: relative;
  width: 100%;
}

.roles-scroll {
  width: 100%;
  overflow-x: auto;
  /* Reserve space for scrollbar to prevent content shift */
  scrollbar-width: thin; /* Firefox */
  scrollbar-color: transparent transparent; /* Firefox: thumb color, track color */
  /* Add smooth scrolling */
  scroll-behavior: smooth;
  /* Add padding to bottom to reserve space for scrollbar */
  padding-bottom: 12px;
  margin-bottom: -12px; /* Offset the padding to maintain layout */
}

/* Style scrollbar for Chrome/Safari/Opera */
.roles-scroll::-webkit-scrollbar {
  height: 8px; /* Height of the scrollbar */
  width: auto;
  display: block; /* Always reserve the space */
  background-color: transparent;
}

.roles-scroll::-webkit-scrollbar-thumb {
  background-color: transparent; /* Initially transparent */
  border-radius: 4px;
}

/* Show scrollbar on hover */
.roles-scroll:hover::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2); /* Semi-transparent on hover */
}

.roles-scroll:hover {
  scrollbar-color: rgba(0, 0, 0, 0.2) transparent; /* Firefox: visible on hover */
}

.roles-list {
  display: inline-flex; /* Changed from flex to inline-flex */
  align-items: stretch;
  gap: 8px;
  padding: 0px 4px; /* Add padding to prevent shadow clipping */
  min-width: min-content; /* Ensure it takes at least the width of all cards */
}

.expand-btn {
  height: auto;
  align-self: stretch;
  display: flex;
  align-items: center;
}

/* Transition animations */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.slide-move {
  transition: transform 0.3s ease;
}

/* Add fade effect on the right when content is scrollable */
.roles-container::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  width: 32px;
  background: linear-gradient(to right, transparent, white);
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.roles-container:hover::after {
  opacity: 1;
}

/* Add fade effect on the left when scrolled */
.roles-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 32px;
  background: linear-gradient(to left, transparent, white);
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 1;
}

.roles-container:hover::before {
  opacity: 1;
}
</style>

