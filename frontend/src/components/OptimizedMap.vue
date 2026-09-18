<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { importLibrary, setOptions } from '@googlemaps/js-api-loader';

const props = defineProps({
  route: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  apiKey: { type: String, default: process.env.GOOGLE_MAPS_API_KEY },
  mapId: { type: String, default: process.env.GOOGLE_MAPS_MAP_ID || 'DEMO_MAP_ID' },
  defaultCenter: { type: Object, default: () => ({ lat: 39.5, lng: -98.35 }) },
  defaultZoom: { type: Number, default: 4 },
});

const FIT_PADDING_PX = 48;

const canvas = ref(null);
const status = ref(props.apiKey ? 'loading' : 'unconfigured');
const errorMessage = ref('');

let map = null;
let sdk = null;
let polyline = null;
let markers = [];

const subtitle = computed(() => {
  if (status.value === 'unconfigured') return 'Map unavailable';
  if (props.loading) return 'Optimizing your route…';
  if (!props.route) return 'Waiting for stops';
  return `${props.route.stops.length} stops · optimized order`;
});

function themeColor(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function pinOptions(index, count) {
  if (index === 0) {
    return { background: themeColor('--tw-primary'), borderColor: themeColor('--tw-primary-dark'), glyphColor: themeColor('--tw-on-primary') };
  }
  if (index === count - 1) {
    return { background: themeColor('--tw-on-primary-container'), borderColor: themeColor('--tw-on-primary-container'), glyphColor: themeColor('--tw-on-primary') };
  }
  return { background: themeColor('--tw-primary-container'), borderColor: themeColor('--tw-primary-dark'), glyphColor: themeColor('--tw-on-primary-container') };
}

function clearOverlays() {
  if (polyline) {
    polyline.setMap(null);
    polyline = null;
  }
  markers.forEach((marker) => { marker.map = null; });
  markers = [];
}

function drawRoute(route) {
  polyline = new sdk.Polyline({
    map,
    path: sdk.encoding.decodePath(route.polyline),
    strokeColor: themeColor('--tw-primary-dark'),
    strokeOpacity: 0.9,
    strokeWeight: 5,
  });

  markers = route.stops.map((stop, index) => {
    const pin = new sdk.PinElement({ ...pinOptions(index, route.stops.length), glyph: String(stop.position) });
    return new sdk.AdvancedMarkerElement({
      map,
      position: stop.location,
      title: `${stop.position}. ${stop.formatted_address}`,
      content: pin.element,
      zIndex: route.stops.length - index,
    });
  });

  map.fitBounds(new sdk.LatLngBounds(route.bounds.southwest, route.bounds.northeast), FIT_PADDING_PX);
}

function renderRoute(route) {
  if (!map || status.value !== 'ready') return;
  clearOverlays();
  if (!route) {
    map.setCenter(props.defaultCenter);
    map.setZoom(props.defaultZoom);
    return;
  }

  // The SDK can throw (e.g. on an auth-failed map); an exception escaping a watcher would break the app
  try {
    drawRoute(route);
  } catch (error) {
    clearOverlays();
    status.value = 'error';
    errorMessage.value = 'Could not draw the route on the map.';
  }
}

async function initMap() {
  setOptions({ key: props.apiKey, v: 'weekly' });
  // Google reports invalid / restricted keys through this global rather than a rejected promise
  window.gm_authFailure = () => {
    status.value = 'error';
    errorMessage.value = 'Google Maps rejected the API key. Check GOOGLE_MAPS_API_KEY and its referrer restrictions.';
  };

  try {
    const [{ Map, Polyline, LatLngBounds }, { AdvancedMarkerElement, PinElement }, { encoding }] = await Promise.all([
      importLibrary('maps'),
      importLibrary('marker'),
      importLibrary('geometry'),
    ]);
    sdk = { Polyline, LatLngBounds, AdvancedMarkerElement, PinElement, encoding };
    map = new Map(canvas.value, {
      center: props.defaultCenter,
      zoom: props.defaultZoom,
      mapId: props.mapId,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: true,
    });
    status.value = 'ready';
    renderRoute(props.route);
  } catch (error) {
    status.value = 'error';
    errorMessage.value = 'Could not load Google Maps. Check your connection and try again.';
  }
}

watch(() => props.route, renderRoute);

onMounted(() => {
  if (props.apiKey) initMap();
});

onBeforeUnmount(() => {
  clearOverlays();
  map = null;
});
</script>

<template>
  <section class="optimized-map tw-card tw-card--elevated">
    <header class="optimized-map__header">
      <h2 class="optimized-map__title">Route map</h2>
      <p class="optimized-map__subtitle">{{ subtitle }}</p>
    </header>

    <div class="optimized-map__frame">
      <div ref="canvas" class="optimized-map__canvas"></div>

      <div v-if="status === 'unconfigured'" class="optimized-map__state">
        <svg class="optimized-map__state-icon" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M20.5 3l-.16.03L15 5.1 9 3 3.36 4.9c-.21.07-.36.25-.36.48V20.5c0 .28.22.5.5.5l.16-.03L9 18.9l6 2.1 5.64-1.9c.21-.07.36-.25.36-.48V3.5c0-.28-.22-.5-.5-.5zM15 19l-6-2.11V5l6 2.11V19z" />
        </svg>
        <p class="optimized-map__state-title">Map unavailable</p>
        <p class="optimized-map__state-text">
          Add <code>GOOGLE_MAPS_API_KEY</code> to <code>frontend/.env</code> and restart the dev server to enable the map.
        </p>
      </div>

      <div v-else-if="status === 'error'" class="optimized-map__state optimized-map__state--error" role="alert">
        <svg class="optimized-map__state-icon" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
        </svg>
        <p class="optimized-map__state-title">Map failed to load</p>
        <p class="optimized-map__state-text">{{ errorMessage }}</p>
      </div>

      <div v-else-if="status === 'loading'" class="optimized-map__state">
        <span class="optimized-map__spinner" aria-hidden="true"></span>
        <p class="optimized-map__state-title">Loading map…</p>
      </div>

      <div v-else-if="loading" class="optimized-map__state optimized-map__state--overlay">
        <span class="optimized-map__spinner" aria-hidden="true"></span>
        <p class="optimized-map__state-title">Optimizing route…</p>
      </div>

      <div v-else-if="!route" class="optimized-map__state optimized-map__state--overlay">
        <p class="optimized-map__state-title">Your optimized route will appear here</p>
      </div>
    </div>

    <ul v-if="route && status === 'ready'" class="optimized-map__legend">
      <li class="optimized-map__legend-item">
        <span class="optimized-map__swatch optimized-map__swatch--origin"></span> Start
      </li>
      <li class="optimized-map__legend-item">
        <span class="optimized-map__swatch"></span> Delivery stop
      </li>
      <li class="optimized-map__legend-item">
        <span class="optimized-map__swatch optimized-map__swatch--destination"></span> Final destination
      </li>
    </ul>
  </section>
</template>
