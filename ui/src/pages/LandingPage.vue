<template>
  <section class="landing">
    <header class="landing__header">
      <div>
        <h1>{{ landingData.site_title || 'NEMO' }}</h1>
        <p class="landing__welcome">Welcome back, {{ landingData.user?.display_name || 'user' }}.</p>
      </div>
      <div v-if="landingData.user?.access_expiration" class="landing__banner" :class="`landing__banner--${landingData.access_expiration_banner}`">
        <span>Your access expires on {{ landingData.user.access_expiration }}.</span>
      </div>
    </header>

    <div class="landing__grid">
      <section class="landing__card" v-if="landingData.upcoming_reservations.length">
        <h2>Upcoming reservations</h2>
        <ul>
          <li v-for="reservation in landingData.upcoming_reservations" :key="reservation.id">
            <div class="landing__item-title">{{ reservation.title }}</div>
            <div class="landing__item-detail">{{ reservation.start }} → {{ reservation.end }}</div>
            <div class="landing__item-detail">{{ reservation.resource_name }}</div>
          </li>
        </ul>
      </section>

      <section class="landing__card" v-if="landingData.alerts.length || landingData.disabled_resources.length">
        <h2>Alerts & outages</h2>
        <ul>
          <li v-for="alert in landingData.alerts" :key="`alert-${alert.id}`" class="landing__alert">
            <strong>{{ alert.title || 'Alert' }}</strong>
            <p v-html="alert.contents"></p>
          </li>
          <li v-for="resource in landingData.disabled_resources" :key="`resource-${resource.id}`" class="landing__alert">
            <strong>Resource outage: {{ resource.name }}</strong>
            <p>{{ resource.restriction_message }}</p>
          </li>
        </ul>
      </section>

      <section class="landing__card" v-if="landingData.usage_events.length">
        <h2>Current {{ landingData.facility_name }} use</h2>
        <ul>
          <li v-for="usage in landingData.usage_events" :key="usage.id">
            <div>You are using <strong>{{ usage.tool_name }}</strong> for {{ usage.project_name }}.</div>
            <div class="landing__item-detail">Started {{ usage.start }}</div>
          </li>
        </ul>
      </section>

      <section class="landing__card" v-if="landingData.landing_page_choices.length">
        <h2>Quick links</h2>
        <div class="landing__choices">
          <a
            v-for="choice in landingData.landing_page_choices"
            :key="choice.id"
            class="landing__choice"
            :href="choice.url"
            :target="choice.open_in_new_tab ? '_blank' : '_self'"
            rel="noopener noreferrer"
          >
            <img :src="choice.image_url" :alt="choice.name" />
            <span>{{ choice.name }}</span>
            <span v-if="choice.notification_count" class="landing__badge">{{ choice.notification_count }}</span>
          </a>
        </div>
      </section>
    </div>

    <div v-if="loading" class="landing__loading">Loading landing data…</div>
    <div v-if="error" class="landing__error">{{ error }}</div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue';
import { fetchLandingData } from '../api/nemoUi';

const landingData = reactive({
  site_title: '',
  facility_name: '',
  access_expiration_banner: null,
  user: null,
  alerts: [],
  disabled_resources: [],
  usage_events: [],
  upcoming_reservations: [],
  landing_page_choices: []
});

const loading = ref(true);
const error = ref('');

onMounted(async () => {
  try {
    const response = await fetchLandingData();
    Object.assign(landingData, response);
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to load landing data.';
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.landing__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 24px;
}

.landing__banner {
  padding: 12px 16px;
  border-radius: 8px;
  background: #e7f0ff;
  border: 1px solid #b8d0ff;
  color: #0b3d91;
}

.landing__banner--warning {
  background: #fff7e6;
  border-color: #ffd591;
  color: #ad6800;
}

.landing__banner--danger {
  background: #fff1f0;
  border-color: #ffa39e;
  color: #a8071a;
}

.landing__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.landing__card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

.landing__card h2 {
  margin-top: 0;
  font-size: 18px;
}

.landing__item-title {
  font-weight: 600;
}

.landing__item-detail {
  font-size: 12px;
  color: #5f6b7a;
}

.landing__alert {
  padding: 12px;
  border-radius: 8px;
  background: #fff1f0;
  margin-bottom: 12px;
}

.landing__choices {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.landing__choice {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-radius: 12px;
  background: #f5f6f8;
  text-decoration: none;
  color: inherit;
  position: relative;
}

.landing__choice img {
  height: 64px;
  width: 64px;
  object-fit: contain;
}

.landing__badge {
  position: absolute;
  top: 8px;
  right: 12px;
  background: #0b3d91;
  color: #fff;
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 12px;
}

.landing__loading,
.landing__error {
  margin-top: 16px;
  font-size: 14px;
}

.landing__error {
  color: #a8071a;
}

.landing__welcome {
  margin: 8px 0 0;
  color: #4b5563;
}
</style>
