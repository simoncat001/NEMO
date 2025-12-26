<template>
  <section class="panel">
    <div class="panel-header">
      <h2>{{ title }}</h2>
      <span class="badge">MVC Controller</span>
    </div>
    <p class="count">{{ count }}</p>
    <div class="controls">
      <button type="button" @click="decrement">-</button>
      <button type="button" @click="reset">重置</button>
      <button type="button" @click="increment">+</button>
    </div>
    <p class="timestamp">最近更新：{{ updatedAt }}</p>
  </section>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  count: {
    type: Number,
    required: true,
  },
  updatedAt: {
    type: String,
    required: true,
  },
  increment: {
    type: Function,
    required: true,
  },
  decrement: {
    type: Function,
    required: true,
  },
  reset: {
    type: Function,
    required: true,
  },
});
</script>

<style scoped>
.panel {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h2 {
  margin: 0;
  font-size: 20px;
}

.badge {
  background: #e0f2fe;
  color: #0369a1;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.count {
  margin: 0;
  font-size: 40px;
  font-weight: 700;
  text-align: center;
}

.controls {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.controls button {
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  background: #2563eb;
  color: white;
  font-size: 14px;
  cursor: pointer;
}

.controls button:nth-child(2) {
  background: #64748b;
}

.controls button:hover {
  filter: brightness(0.95);
}

.timestamp {
  margin: 0;
  color: #64748b;
  font-size: 12px;
  text-align: center;
}
</style>
