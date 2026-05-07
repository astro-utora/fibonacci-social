<template>
  <role-tree-editor-panel
    description="Define the global role tree structure. This will be used as the default template for all users."
    :is-admin="true"
  />
</template>

<script setup lang="ts">
import RoleTreeEditorPanel from '@/components/roles/RoleTreeEditorPanel.vue'
</script> 