<template>
  <mark
    ref="triggerElement"
    tabindex="0"
    class="word-highlight"
    :aria-describedby="reveal ? tooltipId : undefined"
    @mouseenter="showTooltip"
    @mouseleave="hideTooltip"
    @focusin="showTooltip"
    @focusout="hideTooltip"
    @keydown.esc="hideTooltip"
  >
    <slot>
      {{ target }}
    </slot>
  </mark>

  <Teleport to="body">
    <span
      v-if="reveal"
      :id="tooltipId"
      ref="tooltipElement"
      :class="['word-tooltip', { 'is-open': isOpen }]"
      :data-placement="placement"
      role="tooltip"
    >
      <span class="tooltip-chrome">
        <span class="tooltip-label"><i aria-hidden="true"></i> quila.dev / contexto</span>
        <span class="tooltip-controls" aria-hidden="true"><i></i><i></i><i></i></span>
      </span>
      <span class="tooltip-copy">{{ reveal }}</span>
    </span>
  </Teleport>
</template>

<script setup>
import { autoUpdate, computePosition, flip, offset, shift } from '@floating-ui/dom';
import { nextTick, onBeforeUnmount, ref, useId } from 'vue';

const tooltipId = useId();
const triggerElement = ref(null);
const tooltipElement = ref(null);
const isOpen = ref(false);
const placement = ref('top');
let stopAutoUpdate;

const props = defineProps({
  target: {
    type: String,
    default: ''
  },
  reveal: {
    type: String,
    default: ''
  }
});

async function updatePosition() {
  if (!triggerElement.value || !tooltipElement.value) return;

  const position = await computePosition(triggerElement.value, tooltipElement.value, {
    placement: 'top',
    strategy: 'fixed',
    middleware: [
      offset(12),
      flip({ padding: 16 }),
      shift({ padding: 16 })
    ]
  });

  placement.value = position.placement;
  Object.assign(tooltipElement.value.style, {
    left: `${position.x}px`,
    top: `${position.y}px`
  });
}

async function showTooltip() {
  if (!props.reveal || isOpen.value) return;

  isOpen.value = true;
  await nextTick();
  stopAutoUpdate?.();
  stopAutoUpdate = autoUpdate(triggerElement.value, tooltipElement.value, updatePosition);
}

function hideTooltip() {
  isOpen.value = false;
  stopAutoUpdate?.();
  stopAutoUpdate = undefined;
}

onBeforeUnmount(() => stopAutoUpdate?.());
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
  position: fixed;
  z-index: 9998;
  top: 0;
  left: 0;
  display: flex;
  width: min(420px, calc(100vw - 32px));
  flex-direction: column;
  isolation: isolate;
  border: 1px solid var(--color-primary);
  border-radius: 4px;
  color: var(--color-text);
  background: var(--color-background);
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
  transform: translateY(var(--tooltip-entry-y, 10px)) rotate(1deg);
  transform-origin: bottom center;
  transition: opacity 150ms ease, transform 500ms cubic-bezier(0.22, 1, 0.36, 1);
}

.word-tooltip::before {
  position: absolute;
  z-index: -1;
  inset: 0;
  border: 1px solid var(--color-primary);
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
  background: var(--color-primary);
  content: '';
  transform: translateX(-50%);
}

.word-tooltip[data-placement^='bottom'] {
  --tooltip-entry-y: -10px;
}

.word-tooltip[data-placement^='bottom']::after {
  top: auto;
  bottom: 100%;
}

.tooltip-chrome {
  display: flex;
  min-height: 36px;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 0 11px;
  border-radius: 2px 2px 0 0;
  color: var(--color-on-primary);
  background: var(--color-primary);
}

.tooltip-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-on-primary);
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

.word-tooltip.is-open {
  opacity: 1;
  transform: translateY(0) rotate(0);
}

.word-tooltip.is-open::before {
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

  .word-tooltip.is-open::before {
    animation: none;
  }
}
</style>
