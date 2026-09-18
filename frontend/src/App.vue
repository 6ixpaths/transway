<script setup>
import { ref } from 'vue';
import RouteSummary from './components/RouteSummary.vue';
import StopInputForm from './components/StopInputForm.vue';

const submittedStops = ref([]);
const route = ref(null);
const loading = ref(false);

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
      <div class="row g-4">
        <div class="col-lg-6 col-xl-5">
          <StopInputForm :loading="loading" @submit="handleSubmit" />
        </div>
        <div class="col-lg-6 col-xl-7">
          <RouteSummary :route="route" :loading="loading" />
        </div>
      </div>
    </main>
  </div>
</template>
