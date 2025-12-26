<template>
  <section class="login">
    <div class="login__card">
      <h1>Sign in</h1>
      <p class="login__subtitle">Use your NEMO credentials to continue.</p>
      <form class="login__form" method="post" action="/login/" @submit="ensureCsrf">
        <input type="hidden" name="csrfmiddlewaretoken" :value="csrfToken" />
        <label>
          Username
          <input type="text" name="username" required autocomplete="username" />
        </label>
        <label>
          Password
          <input type="password" name="password" required autocomplete="current-password" />
        </label>
        <button type="submit">Log in</button>
      </form>
      <p class="login__hint">Forgot your password? Contact your facility administrator.</p>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue';

const csrfToken = ref('');

const ensureCsrf = () => {
  if (!csrfToken.value) {
    csrfToken.value = getCookie('csrftoken');
  }
};

const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop().split(';').shift();
  }
  return '';
};

csrfToken.value = getCookie('csrftoken');
</script>

<style scoped>
.login {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
}

.login__card {
  background: #fff;
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.1);
  width: min(400px, 90vw);
}

.login__subtitle {
  margin-top: 4px;
  color: #6b7280;
}

.login__form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 24px;
}

.login__form label {
  display: flex;
  flex-direction: column;
  font-size: 14px;
  gap: 6px;
  color: #111827;
}

.login__form input {
  border-radius: 8px;
  border: 1px solid #d1d5db;
  padding: 10px 12px;
  font-size: 14px;
}

.login__form button {
  margin-top: 8px;
  background: #0b3d91;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}

.login__form button:hover {
  background: #082f6f;
}

.login__hint {
  margin-top: 16px;
  color: #6b7280;
  font-size: 13px;
}
</style>
