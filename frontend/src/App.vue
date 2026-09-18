<script setup>
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
      <section class="tw-card tw-card--elevated">
        <header class="tw-card__header">
          <h2 class="tw-card__title">Plan a route</h2>
          <p class="tw-card__subtitle">Add your delivery stops to get the most efficient order.</p>
        </header>
        <div class="tw-card__body">
          <div class="tw-field">
            <input id="demo-stop" class="tw-field__input" type="text" placeholder=" " />
            <label class="tw-field__label" for="demo-stop">Delivery address</label>
          </div>
        </div>
        <footer class="tw-card__actions">
          <button type="button" class="tw-btn tw-btn--text">Clear</button>
          <button type="button" class="tw-btn tw-btn--primary">Optimize route</button>
        </footer>
      </section>
    </main>
  </div>
</template>
