<template>
  <div class="navigation-panel">
    <!-- Vertical Navigation mode -->
    <div v-if="mode === 'vertical'" class="d-flex navigation-container">
      <!-- Navigation sidebar -->
      <v-navigation-drawer 
        :width="drawerWidth" 
        permanent
        class="navigation-sidebar"
      >
        <v-list>
          <v-list-item
            v-for="item in items"
            :key="item.value"
            :to="item.to"
            :active="activeItem === item.value"
            @click="handleItemClick(item.value)"
            :prepend-icon="item.icon"
            :title="item.label"
          ></v-list-item>
        </v-list>
      </v-navigation-drawer>
      
      <!-- Content area -->
      <div class="content-area">
        <div class="content-header d-flex align-center">
          <h2 class="text-h5 font-weight-bold">
            {{ title }}
          </h2>
          <v-spacer></v-spacer>
          <slot name="actions"></slot>
        </div>
        <div class="content-body">
          <slot :name="activeItem" :item="getActiveItem()"></slot>
        </div>
      </div>
    </div>
    
    <!-- Tabs Navigation mode -->
    <div v-else class="tabs-container">
      <v-card class="fill-height d-flex flex-column">
        <v-card-title class="d-flex align-center flex-shrink-0">
          <span>{{ title }}</span>
          <v-spacer></v-spacer>
          <slot name="actions"></slot>
        </v-card-title>
        
        <v-tabs v-model="activeItem" class="flex-shrink-0">
          <v-tab 
            v-for="item in items" 
            :key="item.value" 
            :value="item.value"
          >
            <v-icon v-if="item.icon" start>{{ item.icon }}</v-icon>
            {{ item.label }}
          </v-tab>
        </v-tabs>
        
        <v-card-text class="flex-grow-1 overflow-auto pa-0">
          <v-window v-model="activeItem" class="fill-height">
            <v-window-item
              v-for="item in items"
              :key="item.value"
              :value="item.value"
              class="fill-height"
            >
              <div class="pa-4 fill-height">
                <slot :name="item.value" :item="item"></slot>
              </div>
            </v-window-item>
          </v-window>
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script setup lang="ts">
// Keep the same imports as the rest of the project
import { ref, computed } from 'vue';
import type { NavigationItem } from '@/types/navigation';

const props = defineProps<{
  items: NavigationItem[];
  mode?: 'vertical' | 'tabs';
  title?: string;
  initialItem?: string;
  drawerWidth?: number;
}>();

const emit = defineEmits<{
  'update:activeItem': [value: string];
}>();

// Set initial active item, or default to first item
const activeItem = ref(props.initialItem || (props.items[0]?.value || ''));

function handleItemClick(value: string) {
  activeItem.value = value;
  emit('update:activeItem', value);
}

function getActiveItem(): NavigationItem | undefined {
  return props.items.find((item: NavigationItem) => item.value === activeItem.value);
}
</script>

<style scoped>
.navigation-panel {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.navigation-container {
  height: 100%;
  width: 100%;
  position: relative;
}

.navigation-sidebar {
  position: fixed;
  height: 100%;
  z-index: 1;
}

.content-area {
  flex: 1;
  padding: 16px;
  margin-left: v-bind('drawerWidth + "px"');
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-header {
  flex-shrink: 0;
  margin-bottom: 20px;
}

.content-body {
  flex-grow: 1;
  overflow: auto;
}

.tabs-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.fill-height {
  height: 100%;
}

:deep(.v-window) {
  height: 100%;
}

:deep(.v-window__container) {
  height: 100%;
}

:deep(.v-window-item) {
  height: 100%;
  overflow: auto;
}

:deep(.v-card-text) {
  display: flex;
  flex-direction: column;
}
</style> 