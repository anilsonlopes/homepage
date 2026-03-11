<template>
  <mark
    tabindex="0"
    class="bg-neutral-300 rounded-sm cursor-help transition-colors duration-200 hover:bg-neutral-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-neutral-500"
    :title="reveal"
  >
    <slot>
      {{ target }}
    </slot>
  </mark>
</template>

<script setup>
import { defineProps } from 'vue';

defineProps({
  target: {
    type: String,
    default: ''
  },
  reveal: {
    type: String,
    default: ''
  }
});
</script>