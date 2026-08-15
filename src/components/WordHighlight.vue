<template>
  <mark
    tabindex="0"
    class="word-highlight"
    :aria-describedby="reveal ? tooltipId : undefined"
  >
    <slot>
      {{ target }}
    </slot>
    <span v-if="reveal" :id="tooltipId" class="word-tooltip" role="tooltip">
      <span class="tooltip-chrome">
        <span class="tooltip-label"><i aria-hidden="true"></i> quila.dev / contexto</span>
        <span class="tooltip-controls" aria-hidden="true"><i></i><i></i><i></i></span>
      </span>
      <span class="tooltip-copy">{{ reveal }}</span>
    </span>
  </mark>
</template>

<script setup>
import { useId } from 'vue';

const tooltipId = useId();

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
  position: relative;
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

.word-tooltip {
  position: absolute;
  z-index: 20;
  bottom: calc(100% + 10px);
  left: 50%;
  display: flex;
  width: min(420px, calc(100vw - 32px));
  flex-direction: column;
  isolation: isolate;
  border: 1px solid #24211d;
  border-radius: 4px;
  color: #0a0a0a;
  background: #ffffff;
  font-family: 'Archivo', ui-sans-serif, system-ui, sans-serif;
  font-size: 16px;
  font-style: normal;
  font-weight: 400;
  letter-spacing: -0.01em;
  line-height: 1.6;
  opacity: 0;
  pointer-events: none;
  text-align: left;
  text-transform: none;
  transform: translate(-47%, 10px) rotate(1deg);
  transform-origin: bottom center;
  transition: opacity 150ms ease, transform 500ms cubic-bezier(0.22, 1, 0.36, 1);
}

.word-tooltip::before {
  position: absolute;
  z-index: -1;
  inset: 0;
  border: 1px solid #24211d;
  border-radius: 4px;
  background: #009150;
  box-shadow: 0 16px 36px rgb(0 0 0 / 20%);
  content: '';
  transform: translate(6px, 6px) skewX(-1deg);
}

.word-tooltip::after {
  position: absolute;
  z-index: -1;
  top: 100%;
  left: 50%;
  width: 1px;
  height: 10px;
  background: #24211d;
  content: '';
  transform: translateX(-50%);
}

.tooltip-chrome {
  display: flex;
  min-height: 36px;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 0 11px;
  border-radius: 2px 2px 0 0;
  color: #ffffff;
  background: #24211d;
}

.tooltip-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #ffffff;
  font-family: 'Martian Mono', ui-monospace, monospace;
  font-size: 9px;
  font-weight: 500;
  letter-spacing: 0.06em;
  line-height: 1;
  text-transform: uppercase;
}

.tooltip-label i {
  width: 7px;
  height: 7px;
  border-radius: 9999px;
  background: #009150;
}

.tooltip-controls {
  display: flex;
  gap: 5px;
}

.tooltip-controls i {
  width: 7px;
  height: 7px;
  border: 1px solid rgb(255 255 255 / 55%);
  border-radius: 2px;
}

.tooltip-copy {
  display: block;
  padding: 18px 20px 20px;
}

.word-highlight:hover .word-tooltip,
.word-highlight:focus .word-tooltip {
  opacity: 1;
  transform: translate(-50%, 0) rotate(0);
}

.word-highlight:hover .word-tooltip::before,
.word-highlight:focus .word-tooltip::before {
  animation: tooltip-frame-settle 600ms cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes tooltip-frame-settle {
  0% {
    transform: translate(13px, 9px) skewX(-4deg);
  }

  65% {
    transform: translate(4px, 5px) skewX(0);
  }

  100% {
    transform: translate(6px, 6px) skewX(-1deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .word-tooltip {
    transition-duration: 0.01ms;
  }

  .word-highlight:hover .word-tooltip::before,
  .word-highlight:focus .word-tooltip::before {
    animation: none;
  }
}
</style>
