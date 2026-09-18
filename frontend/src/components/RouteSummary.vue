<script setup>
import { computed, ref } from 'vue';

const props = defineProps({
  route: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  // Litres per 100 km used for the fuel estimate
  fuelEconomy: { type: Number, default: 8 },
});

const METERS_PER_KM = 1000;
const METERS_PER_MILE = 1609.344;
const LITRES_PER_GALLON = 3.785411784;
const MPG_CONVERSION = 235.215;

const units = ref('metric');
const isMetric = computed(() => units.value === 'metric');
const distanceUnit = computed(() => (isMetric.value ? 'km' : 'mi'));
const fuelUnit = computed(() => (isMetric.value ? 'L' : 'gal'));

const numberFormat = new Intl.NumberFormat(undefined, { maximumFractionDigits: 1 });
const fmt = (value) => numberFormat.format(value);

function metersToUnits(meters) {
  return meters / (isMetric.value ? METERS_PER_KM : METERS_PER_MILE);
}

function formatDuration(totalMinutes) {
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (hours === 0) return `${minutes} min`;
  return minutes === 0 ? `${hours} h` : `${hours} h ${minutes} min`;
}

const subtitle = computed(() => {
  if (props.loading) return 'Optimizing your route…';
  if (!props.route) return 'Waiting for stops';
  return `${props.route.stops.length} stops · optimized order`;
});

const totalDistance = computed(() => metersToUnits(props.route.total_distance_meters));

const fuelEstimate = computed(() => {
  const litres = (props.route.total_distance_km * props.fuelEconomy) / 100;
  return isMetric.value ? litres : litres / LITRES_PER_GALLON;
});

const fuelHint = computed(() =>
  isMetric.value
    ? `at ${props.fuelEconomy} L/100 km`
    : `at ${Math.round(MPG_CONVERSION / props.fuelEconomy)} mpg`,
);

const reorderedCount = computed(
  () => props.route.stops.filter((stop) => stop.original_index !== stop.position - 1).length,
);

function badgeClass(index) {
  return {
    'route-summary__stop-badge--origin': index === 0,
    'route-summary__stop-badge--destination': index === props.route.stops.length - 1,
  };
}
</script>

<template>
  <section class="route-summary tw-card tw-card--elevated" aria-live="polite">
    <header class="route-summary__header">
      <div>
        <h2 class="route-summary__title">Route summary</h2>
        <p class="route-summary__subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="route && !loading" class="route-summary__units" role="group" aria-label="Distance units">
        <button
          type="button"
          class="route-summary__unit"
          :class="{ 'route-summary__unit--active': isMetric }"
          :aria-pressed="isMetric"
          @click="units = 'metric'"
        >km</button>
        <button
          type="button"
          class="route-summary__unit"
          :class="{ 'route-summary__unit--active': !isMetric }"
          :aria-pressed="!isMetric"
          @click="units = 'imperial'"
        >mi</button>
      </div>
    </header>

    <div v-if="loading" class="route-summary__metrics" aria-busy="true">
      <div v-for="n in 4" :key="n" class="route-summary__metric">
        <span class="route-summary__skeleton route-summary__skeleton--label"></span>
        <span class="route-summary__skeleton route-summary__skeleton--value"></span>
      </div>
    </div>

    <div v-else-if="!route" class="route-summary__empty">
      <svg class="route-summary__empty-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 010-5 2.5 2.5 0 010 5z" />
      </svg>
      <p class="route-summary__empty-title">No route yet</p>
      <p class="route-summary__empty-text">
        Add your delivery stops and optimize to see total distance, drive time and fuel estimates.
      </p>
    </div>

    <template v-else>
      <dl class="route-summary__metrics">
        <div class="route-summary__metric route-summary__metric--primary">
          <dt class="route-summary__metric-label">Total distance</dt>
          <dd class="route-summary__metric-value">
            {{ fmt(totalDistance) }}
            <span class="route-summary__metric-unit">{{ distanceUnit }}</span>
          </dd>
        </div>
        <div class="route-summary__metric">
          <dt class="route-summary__metric-label">Drive time</dt>
          <dd class="route-summary__metric-value">{{ formatDuration(route.total_duration_minutes) }}</dd>
        </div>
        <div class="route-summary__metric">
          <dt class="route-summary__metric-label">Estimated fuel</dt>
          <dd class="route-summary__metric-value">
            {{ fmt(fuelEstimate) }}
            <span class="route-summary__metric-unit">{{ fuelUnit }}</span>
          </dd>
          <span class="route-summary__metric-hint">{{ fuelHint }}</span>
        </div>
        <div class="route-summary__metric">
          <dt class="route-summary__metric-label">Stops reordered</dt>
          <dd class="route-summary__metric-value">{{ reorderedCount }}</dd>
          <span class="route-summary__metric-hint">of {{ route.stops.length }}</span>
        </div>
      </dl>

      <ol class="route-summary__itinerary">
        <li v-for="(stop, index) in route.stops" :key="stop.position" class="route-summary__stop">
          <span class="route-summary__stop-badge" :class="badgeClass(index)">{{ stop.position }}</span>
          <div class="route-summary__stop-body">
            <span class="route-summary__stop-address">{{ stop.formatted_address }}</span>
            <span v-if="route.legs[index]" class="route-summary__leg">
              {{ fmt(metersToUnits(route.legs[index].distance_meters)) }} {{ distanceUnit }}
              · {{ formatDuration(Math.round(route.legs[index].duration_seconds / 60)) }}
            </span>
          </div>
        </li>
      </ol>
    </template>
  </section>
</template>
