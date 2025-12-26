import { reactive } from "vue";

const state = reactive({
  count: 0,
  updatedAt: new Date(),
});

const increment = () => {
  state.count += 1;
  state.updatedAt = new Date();
};

const decrement = () => {
  state.count -= 1;
  state.updatedAt = new Date();
};

const reset = () => {
  state.count = 0;
  state.updatedAt = new Date();
};

export default {
  state,
  increment,
  decrement,
  reset,
};
