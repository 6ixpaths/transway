<script setup>
import { ref } from 'vue';
import LoadingOverlay from './components/LoadingOverlay.vue';
import NotificationSnackbar from './components/NotificationSnackbar.vue';
import OptimizedMap from './components/OptimizedMap.vue';
import RouteSummary from './components/RouteSummary.vue';
import StopInputForm from './components/StopInputForm.vue';
import { ApiError, optimizeRoute } from './services/api';

const form = ref(null);
const route = ref(null);
const loading = ref(false);
const notification = ref(null);

let controller = null;

function notify(message, { variant = 'error', action = null } = {}) {
  notification.value = { id: Date.now(), message, variant, action };
}

async function handleSubmit(stops) {
  controller?.abort();
  const current = new AbortController();
  controller = current;
  loading.value = true;
  notification.value = null;

  try {
    route.value = await optimizeRoute(stops, { signal: current.signal });
  } catch (error) {
    if (error.name === 'AbortError') return;
    route.value = null;
    handleError(error, stops);
  } finally {
    if (controller === current) {
      controller = null;
      loading.value = false;
    }
  }
}

function handleError(error, stops) {
  if (!(error instanceof ApiError)) {
    notify('Something went wrong while optimizing the route.');
    return;
  }

  if (error.code === 'route_not_found' && error.address) {
    form.value?.markInvalid(error.address, "Google Maps couldn't find this address");
  }

  const action = error.isRetryable ? { label: 'Retry', handler: () => handleSubmit(stops) } : null;
  notify(error.message, { action });
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

    <main class="app-shell__main container" :aria-busy="loading">
      <div class="row g-4">
        <div class="col-lg-6 col-xl-5">
          <StopInputForm ref="form" :loading="loading" @submit="handleSubmit" />
        </div>
        <div class="col-lg-6 col-xl-7">
          <div class="app-shell__stack">
            <OptimizedMap :route="route" :loading="loading" />
            <RouteSummary :route="route" :loading="loading" />
          </div>
        </div>
      </div>
    </main>

    <LoadingOverlay :active="loading" message="Optimizing your route…" />
    <NotificationSnackbar :notification="notification" @dismiss="notification = null" />
  </div>
</template>
