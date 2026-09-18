<script setup>
import { computed, nextTick, ref } from 'vue';

const props = defineProps({
  loading: { type: Boolean, default: false },
  minStops: { type: Number, default: 2 },
  maxStops: { type: Number, default: 27 },
});

const emit = defineEmits(['submit']);

let nextId = 0;
const createStop = () => ({ id: nextId++, address: '', error: '' });
const blankStops = () => Array.from({ length: props.minStops }, createStop);

const root = ref(null);
const stops = ref(blankStops());

const canAdd = computed(() => stops.value.length < props.maxStops);
const canRemove = computed(() => stops.value.length > props.minStops);

function labelFor(index) {
  if (index === 0) return 'Starting point';
  if (index === stops.value.length - 1) return 'Final destination';
  return 'Delivery address';
}

async function addStop() {
  if (!canAdd.value) return;
  const stop = createStop();
  stops.value.push(stop);
  await nextTick();
  root.value?.querySelector(`#stop-${stop.id}`)?.focus();
}

function removeStop(index) {
  if (canRemove.value) stops.value.splice(index, 1);
}

function moveStop(index, delta) {
  const target = index + delta;
  if (target < 0 || target >= stops.value.length) return;
  const [stop] = stops.value.splice(index, 1);
  stops.value.splice(target, 0, stop);
}

function clearAll() {
  stops.value = blankStops();
}

function submit() {
  let valid = true;
  for (const stop of stops.value) {
    if (!stop.address.trim()) {
      stop.error = 'Enter an address';
      valid = false;
    }
  }
  if (!valid) return;
  emit('submit', stops.value.map((stop) => stop.address.trim()));
}
</script>

<template>
  <form ref="root" class="stop-form tw-card tw-card--elevated" novalidate @submit.prevent="submit">
    <header class="stop-form__header">
      <div>
        <h2 class="stop-form__title">Delivery stops</h2>
        <p class="stop-form__subtitle">
          Your first stop is the starting point and the last is the final destination;
          everything in between gets reordered for the fastest route.
        </p>
      </div>
      <span class="stop-form__counter" aria-live="polite">{{ stops.length }} / {{ maxStops }}</span>
    </header>

    <TransitionGroup tag="ol" name="stop-form__row" class="stop-form__list">
      <li v-for="(stop, index) in stops" :key="stop.id" class="stop-form__row">
        <span
          class="stop-form__badge"
          :class="{
            'stop-form__badge--origin': index === 0,
            'stop-form__badge--destination': index === stops.length - 1,
          }"
        >{{ index + 1 }}</span>

        <div class="tw-field stop-form__field" :class="{ 'tw-field--invalid': stop.error }">
          <input
            :id="`stop-${stop.id}`"
            v-model="stop.address"
            class="tw-field__input"
            type="text"
            placeholder=" "
            autocomplete="street-address"
            :disabled="loading"
            :aria-invalid="Boolean(stop.error)"
            @input="stop.error = ''"
          />
          <label class="tw-field__label" :for="`stop-${stop.id}`">{{ labelFor(index) }}</label>
          <p v-if="stop.error" class="tw-field__error" role="alert">{{ stop.error }}</p>
        </div>

        <div class="stop-form__row-actions">
          <button
            type="button"
            class="stop-form__icon-btn"
            :disabled="loading || index === 0"
            aria-label="Move stop up"
            @click="moveStop(index, -1)"
          >
            <svg class="stop-form__icon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M4 12l1.41 1.41L11 7.83V20h2V7.83l5.58 5.59L20 12l-8-8-8 8z" />
            </svg>
          </button>
          <button
            type="button"
            class="stop-form__icon-btn"
            :disabled="loading || index === stops.length - 1"
            aria-label="Move stop down"
            @click="moveStop(index, 1)"
          >
            <svg class="stop-form__icon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M20 12l-1.41-1.41L13 16.17V4h-2v12.17l-5.58-5.59L4 12l8 8 8-8z" />
            </svg>
          </button>
          <button
            type="button"
            class="stop-form__icon-btn stop-form__icon-btn--danger"
            :disabled="loading || !canRemove"
            aria-label="Remove stop"
            @click="removeStop(index)"
          >
            <svg class="stop-form__icon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
            </svg>
          </button>
        </div>
      </li>
    </TransitionGroup>

    <div class="stop-form__add-row">
      <button type="button" class="tw-btn tw-btn--outlined" :disabled="loading || !canAdd" @click="addStop">
        <svg class="stop-form__icon" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
        </svg>
        Add stop
      </button>
      <p v-if="!canAdd" class="stop-form__hint">Routes are limited to {{ maxStops }} stops.</p>
    </div>

    <footer class="stop-form__actions">
      <button type="button" class="tw-btn tw-btn--text" :disabled="loading" @click="clearAll">Clear</button>
      <button type="submit" class="tw-btn tw-btn--primary" :disabled="loading">
        <span v-if="loading" class="stop-form__spinner" aria-hidden="true"></span>
        {{ loading ? 'Optimizing…' : 'Optimize route' }}
      </button>
    </footer>
  </form>
</template>
