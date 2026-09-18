<script setup>
defineProps({
  active: { type: Boolean, default: false },
  message: { type: String, default: 'Working…' },
});
</script>

<template>
  <Transition name="loading-overlay">
    <div v-if="active" class="loading-overlay" role="status" aria-live="polite">
      <div class="loading-overlay__panel">
        <span class="loading-overlay__spinner" aria-hidden="true"></span>
        <span class="loading-overlay__message">{{ message }}</span>
      </div>
    </div>
  </Transition>
</template>
