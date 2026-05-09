<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string
    description?: string
  }>(),
  {
    description: '',
  },
)
</script>

<template>
  <div class="app-empty">
    <div class="app-empty-icon">∅</div>
    <div class="app-empty-title">{{ title }}</div>
    <div v-if="description" class="app-empty-desc">{{ description }}</div>
  </div>
</template>

<style scoped>
.app-empty {
  display: grid;
  place-items: center;
  gap: 8px;
  min-height: 180px;
  padding: 42px 20px;
  border: 1px dashed var(--line);
  border-radius: 18px;
  background: rgba(255, 251, 244, 0.68);
  color: var(--muted);
  text-align: center;
}

:root[data-theme='night-focus'] .app-empty {
  background: rgba(26, 33, 27, 0.76);
}

.app-empty-icon {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: var(--panel-strong);
  color: var(--green);
  font-size: 24px;
  font-weight: 800;
}

.app-empty-title {
  color: var(--text);
  font-size: 15px;
  font-weight: 700;
}

.app-empty-desc {
  max-width: 420px;
  font-size: 13px;
  line-height: 1.6;
}
</style>
