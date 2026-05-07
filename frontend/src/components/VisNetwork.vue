<template>
  <div ref="networkContainer" class="network-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Network } from 'vis-network'

interface GraphNode {
  id: string;
  label: string;
  color?: string;
}

interface GraphEdge {
  from: string;
  to: string;
  label: string;
}

const props = defineProps<{
  nodes: GraphNode[];
  edges: GraphEdge[];
  options: Record<string, any>;
}>()

const networkContainer = ref<HTMLDivElement | null>(null)
let network: Network | null = null

onMounted(() => {
  if (networkContainer.value) {
    network = new Network(
      networkContainer.value,
      { nodes: props.nodes, edges: props.edges },
      props.options
    )
  }
})
</script>

<style scoped>
.network-container {
  width: 100%;
  height: 100%;
}
</style> 