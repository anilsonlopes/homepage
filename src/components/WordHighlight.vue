<template>
  <mark
    tabindex="0"
    class="word-highlight"
    :title="reveal"
  >
    <slot>
      {{ target }}
    </slot>
  </mark>
</template>

<script setup>
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

<style scoped>
.word-highlight {
  border-radius: 3px;
  padding: 0 0.08em;
  color: inherit;
  background: rgb(0 145 80 / 14%);
  box-decoration-break: clone;
  cursor: help;
  transition: color 150ms ease, background-color 150ms ease, box-shadow 150ms ease;
  -webkit-box-decoration-break: clone;
}

.word-highlight:hover {
  color: #ffffff;
  background: #009150;
}

.word-highlight:focus-visible {
  color: #ffffff;
  background: #009150;
  outline: none;
  box-shadow: 0 0 0 3px rgb(0 145 80 / 25%);
}
</style>
