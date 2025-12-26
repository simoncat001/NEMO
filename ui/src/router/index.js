import { createRouter, createWebHistory } from 'vue-router';
import LandingPage from '../pages/LandingPage.vue';
import LoginPage from '../pages/LoginPage.vue';
import { legacyRoutes } from '../legacyRoutes';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'landing', component: LandingPage },
    { path: '/login', name: 'login', component: LoginPage },
    ...legacyRoutes
  ]
});

export default router;
