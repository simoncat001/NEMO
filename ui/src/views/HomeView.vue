<template>
  <main class="home">
    <div class="info">
      <h2>目录结构</h2>
      <ul>
        <li><strong>models</strong>：业务数据与状态</li>
        <li><strong>controllers</strong>：视图逻辑与交互</li>
        <li><strong>views</strong>：页面级展示</li>
      </ul>
    </div>
    <CounterPanel
      title="计数示例"
      :count="count"
      :updated-at="formattedTime"
      :increment="increment"
      :decrement="decrement"
      :reset="reset"
    />
  </main>
</template>

<script setup>
import { computed } from "vue";
import CounterPanel from "../components/CounterPanel.vue";
import { useCounterController } from "../controllers/counterController";

const { count, updatedAt, increment, decrement, reset } = useCounterController();

const formattedTime = computed(() => updatedAt.value.toLocaleTimeString());
</script>

<style scoped>
.home {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 24px;
}

.info {
  background: #f1f5f9;
  border-radius: 16px;
  padding: 24px;
}

.info h2 {
  margin-top: 0;
}

.info ul {
  margin: 0;
  padding-left: 18px;
  color: #334155;
}

@media (max-width: 900px) {
  .home {
    grid-template-columns: 1fr;
  }
}
</style>
