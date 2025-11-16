<template>
  <button type="button" class="bg-neutral-300" :title="reveal">
    <slot>
      {{ target }}
    </slot>
  </button>
</template>

<script setup>
import { defineProps } from 'vue';

defineProps({
  target: {
    type: String,
    required: true
  },
  reveal: {
    type: String,
    required: true
  }
});
</script>