<script setup>
import { ref } from 'vue';
import StopInputForm from './components/StopInputForm.vue';

const submittedStops = ref([]);

function handleSubmit(stops) {
  submittedStops.value = stops;
}
</script>

<template>
  <div class="app-shell">
    <header class="app-shell__header">
      <div class="container app-shell__header-inner">
        <span class="app-shell__brand">Transway</span>
        <span class="app-shell__tagline">Delivery route optimizer</span>
      </div>
    </header>

    <main class="app-shell__main container">
      <StopInputForm @submit="handleSubmit" />
    </main>
  </div>
</template>
