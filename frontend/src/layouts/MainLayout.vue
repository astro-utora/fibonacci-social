<template>
  <div style="width: 100vw; height: 100vh;">
    <v-app-bar>
      <router-link to="/" class="d-flex align-center text-decoration-none">
        <img
          :src="logoUrl"
          height="32"
          class="ml-2"
        />
      </router-link>
      <v-app-bar-title>Fibonacci Social</v-app-bar-title>
      <v-spacer></v-spacer>
      
      <!-- Project Settings button (when a project is active) -->
      <v-btn
        v-if="activeProject"
        variant="text"
        :to="projectSettingsUrl"
        prepend-icon="mdi-cog"
      >
        Project Settings
      </v-btn>
      
      <!-- Admin Panel button (when no project is active) -->
      <v-btn
        v-else-if="isAdmin"
        variant="text"
        to="/admin"
        prepend-icon="mdi-shield-account"
      >
        Admin Panel
      </v-btn>

      <v-menu v-if="isAuthenticated">
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            v-bind="props"
          >
            <v-icon>mdi-menu</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item @click="showInviteDialog = true">
            <v-list-item-title>
              <v-icon start>mdi-account-plus</v-icon>
              Invite User
            </v-list-item-title>
          </v-list-item>
          <v-list-item @click="handleLogout">
            <v-list-item-title>
              <v-icon start>mdi-logout</v-icon>
              Logout
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <v-main style="width: 100%; height: 100%;">
      <WaitingListGuard>
        <router-view />
      </WaitingListGuard>
    </v-main>

    <InvitationDialog v-model="showInviteDialog" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'effector-vue/composition'
import { $user, $isAuthenticated, $isAdmin, logout } from '@/stores/auth'
import InvitationDialog from '@/components/InvitationDialog.vue'
import { $activeProject } from '@/stores/project'
import type { Project } from '@/types/project'
import WaitingListGuard from '@/components/WaitingListGuard.vue'

const router = useRouter()
const user = useStore($user)
const isAdmin = useStore($isAdmin)
const isAuthenticated = useStore($isAuthenticated)
const activeProject = useStore<Project | null>($activeProject)

const logoUrl = ref(`${window.location.origin}/logo_white.jpeg`)
const showInviteDialog = ref(false)

// Fix for the project settings URL
const projectSettingsUrl = computed(() => 
  activeProject.value ? `/project-settings/${activeProject.value.id}` : ''
)

function handleLogout() {
  logout()
  router.push('/login')
}
</script> 