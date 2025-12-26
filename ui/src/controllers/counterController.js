import { computed } from "vue";
import counterModel from "../models/counterModel";

export const useCounterController = () => {
  const count = computed(() => counterModel.state.count);
  const updatedAt = computed(() => counterModel.state.updatedAt);

  return {
    count,
    updatedAt,
    increment: counterModel.increment,
    decrement: counterModel.decrement,
    reset: counterModel.reset,
  };
};
