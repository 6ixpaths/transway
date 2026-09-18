<script setup>
import { onBeforeUnmount, watch } from 'vue';

const props = defineProps({
  notification: { type: Object, default: null },
  duration: { type: Number, default: 8000 },
});

const emit = defineEmits(['dismiss']);

let timer = null;

function clearTimer() {
  clearTimeout(timer);
  timer = null;
}

function dismiss() {
  clearTimer();
  emit('dismiss');
}

function runAction() {
  const { action } = props.notification;
  dismiss();
  action.handler();
}

watch(
  () => props.notification,
  (notification) => {
    clearTimer();
    if (notification && props.duration > 0) timer = setTimeout(dismiss, props.duration);
  },
  { immediate: true },
);

onBeforeUnmount(clearTimer);
</script>

<template>
  <Transition name="snackbar">
    <div
      v-if="notification"
      :key="notification.id"
      class="snackbar"
      :class="`snackbar--${notification.variant}`"
      role="alert"
    >
      <span class="snackbar__message">{{ notification.message }}</span>
      <button v-if="notification.action" type="button" class="snackbar__action" @click="runAction">
        {{ notification.action.label }}
      </button>
      <button type="button" class="snackbar__close" aria-label="Dismiss notification" @click="dismiss">
        <svg class="snackbar__icon" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
        </svg>
      </button>
    </div>
  </Transition>
</template>
