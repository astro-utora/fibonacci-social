<template>
  <v-app style="width: 100%; height: 100%;">
    <router-view />
    <NotificationBar />
  </v-app>
</template>

<script setup lang="ts">
import NotificationBar from '@/components/NotificationBar.vue'
</script> 