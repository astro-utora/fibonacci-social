<template>
  <div>
    <v-app-bar>
      <router-link to="/" class="d-flex align-center text-decoration-none">
        <img
          :src="logoUrl"
          height="32"
          class="ml-2"
          alt="Logo"
        />
      </router-link>
      <v-app-bar-title>Fibonacci Social - Admin Panel</v-app-bar-title>
      <v-spacer />
      
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            v-bind="props"
          >
            <v-icon>mdi-menu</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item @click="handleLogout">
            <v-list-item-title>
              <v-icon start>mdi-logout</v-icon>
              Logout
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <v-main style="height: calc(100vh - 64px);">
      <div class="d-flex admin-container">
        <!-- Navigation sidebar -->
        <v-navigation-drawer
          permanent
          width="250"
          class="admin-nav"
        >
          <v-list>
            <v-list-item
              v-for="item in navigationItems"
              :key="item.value"
              :to="item.to"
              :title="item.label"
              :prepend-icon="item.icon"
            />
          </v-list>
        </v-navigation-drawer>
        
        <!-- Content area -->
        <div class="admin-content">
          <router-view />
        </div>
      </div>
    </v-main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { logout } from '@/stores/auth'
import type { NavigationItem } from '@/types/navigation'

const router = useRouter()
const route = useRoute()

// Initialize logoUrl with a default value
const logoUrl = ref('')

// Set the logo URL after component is mounted
onMounted(() => {
  logoUrl.value = `${window.location.origin}/logo_sky.png`
})

const navigationItems: NavigationItem[] = [
  { label: 'Dashboard', value: 'dashboard', icon: 'mdi-view-dashboard', to: '/admin' },
  { label: 'Role Tree', value: 'role-tree', icon: 'mdi-file-tree', to: '/admin/role-tree' },
  { label: 'User Forms', value: 'user-forms', icon: 'mdi-form-select', to: '/admin/user-forms' },
  { label: 'Waiting List', value: 'waiting-list', icon: 'mdi-account-clock', to: '/admin/waiting-list' },
  { label: 'Settings', value: 'settings', icon: 'mdi-cog', to: '/admin/settings' },
]

async function handleLogout() {
  await logout()
  router.push('/login')
}
</script>

<style scoped>
.v-app-bar {
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}

.admin-container {
  height: 100%;
}

.admin-nav {
  flex-shrink: 0;
}

.admin-content {
  flex: 1;
  padding: 16px;
  overflow: auto;
}
</style>