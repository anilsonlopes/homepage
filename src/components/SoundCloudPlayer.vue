<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue';
import { trackEvent } from '@/analytics.js';

const profileUrl = 'https://soundcloud.com/quilamcz';
const playlistResource = 'https://soundcloud.com/quilamcz/sets/homepage';
const fallbackArtwork = 'https://i1.sndcdn.com/avatars-28DTfwQxl2JRM663-mQ1AZg-t500x500.jpg';
const widgetScriptUrl = 'https://w.soundcloud.com/player/api.js';
const playbackStorageKey = 'quila-soundcloud-playback';

const iframeElement = ref(null);
const playerElement = ref(null);
const isReady = ref(false);
const isPlaying = ref(false);
const hasError = ref(false);
const isMinimized = ref(true);
const isClosed = ref(false);
const isMaximized = ref(false);
const volume = ref(100);
const currentTrack = ref(null);
let widget;
let widgetEvents;
let currentTrackId;
let currentSoundIndex = 0;
let lastPlaybackSave = 0;
let isRestoringPlayback = false;
let tickAudioContext;
let lastTickStep = -1;
let activeDrag;
let removeResizeListener;
const playerPosition = reactive({ x: 0, y: 0, initialized: false });

const playerStyle = computed(() => playerPosition.initialized && !isMinimized.value && !isClosed.value && !isMaximized.value
  ? { left: `${playerPosition.x}px`, top: `${playerPosition.y}px` }
  : undefined);

const formattedDuration = computed(() => {
  const totalSeconds = Math.floor((currentTrack.value?.duration || 0) / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = String(totalSeconds % 60).padStart(2, '0');
  return `${minutes}:${seconds}`;
});

const formattedPlays = computed(() => new Intl.NumberFormat('pt-BR', { notation: 'compact' })
  .format(currentTrack.value?.playback_count || 0));
const artworkSource = computed(() => currentTrack.value?.artwork_url?.replace('-large', '-t500x500') || fallbackArtwork);

const iframeSource = computed(() => {
  const parameters = new URLSearchParams({
    url: playlistResource,
    auto_play: 'false',
    show_artwork: 'false',
    show_comments: 'false',
    show_playcount: 'false',
    show_user: 'false',
    visual: 'false'
  });

  return `https://w.soundcloud.com/player/?${parameters}`;
});

function loadWidgetApi() {
  if (window.SC?.Widget) return Promise.resolve(window.SC);
  if (window.soundCloudWidgetPromise) return window.soundCloudWidgetPromise;

  window.soundCloudWidgetPromise = new Promise((resolve, reject) => {
    const existingScript = document.querySelector(`script[src="${widgetScriptUrl}"]`);
    const script = existingScript || document.createElement('script');

    script.addEventListener('load', () => resolve(window.SC), { once: true });
    script.addEventListener('error', reject, { once: true });

    if (!existingScript) {
      script.src = widgetScriptUrl;
      script.async = true;
      document.head.appendChild(script);
    }
  });

  return window.soundCloudWidgetPromise;
}

function updateCurrentTrack(trackChanged = false) {
  widget?.getCurrentSound((track) => {
    if (!track) return;

    const trackId = track.urn || track.id;
    if (trackChanged && currentTrackId && trackId !== currentTrackId) {
      trackEvent('audio_track_change', { provider: 'soundcloud', track_id: trackId });
    }
    currentTrackId = trackId;
    currentTrack.value = track;
  });
}

function savePlaybackState(position) {
  localStorage.setItem(playbackStorageKey, JSON.stringify({
    index: currentSoundIndex,
    position: Math.max(0, Math.round(position || 0)),
    volume: volume.value
  }));
}

function persistPlaybackState() {
  widget?.getCurrentSoundIndex((index) => {
    currentSoundIndex = index;
    widget.getPosition(savePlaybackState);
  });
}

function restorePlaybackState() {
  let savedPlayback;
  try {
    savedPlayback = JSON.parse(localStorage.getItem(playbackStorageKey) || 'null');
  } catch {
    localStorage.removeItem(playbackStorageKey);
  }

  if (Number.isFinite(savedPlayback?.volume)) {
    volume.value = Math.min(100, Math.max(0, savedPlayback.volume));
    widget.setVolume(volume.value);
  } else {
    widget.getVolume((currentVolume) => {
      volume.value = currentVolume;
    });
  }

  if (!Number.isInteger(savedPlayback?.index) || savedPlayback.index < 0) {
    widget.getCurrentSoundIndex((index) => {
      currentSoundIndex = index;
    });
    return;
  }

  isRestoringPlayback = true;
  currentSoundIndex = savedPlayback.index;
  widget.skip(savedPlayback.index);
  widget.pause();
  widget.seekTo(savedPlayback.position || 0);
  window.setTimeout(() => {
    updateCurrentTrack();
    isRestoringPlayback = false;
  }, 500);
}

function togglePlayback() {
  if (!isReady.value) return;

  widget.toggle();
  trackEvent(isPlaying.value ? 'audio_pause' : 'audio_play', {
    provider: 'soundcloud',
    track_id: currentTrack.value?.urn || currentTrack.value?.id || 'profile'
  });
}

function changeTrack(direction) {
  if (!isReady.value) return;

  widget[direction]();
  trackEvent(`audio_${direction === 'prev' ? 'previous' : 'next'}`, { provider: 'soundcloud' });
}

async function playVolumeTick(value) {
  const tickStep = Math.round(value / 4);
  if (tickStep === lastTickStep) return;
  lastTickStep = tickStep;

  const AudioContext = window.AudioContext || window.webkitAudioContext;
  if (!AudioContext) return;

  tickAudioContext ||= new AudioContext();
  if (tickAudioContext.state === 'suspended') {
    try {
      await tickAudioContext.resume();
    } catch {
      return;
    }
  }
  if (tickStep !== lastTickStep) return;

  const now = tickAudioContext.currentTime;
  const oscillator = tickAudioContext.createOscillator();
  const gain = tickAudioContext.createGain();
  oscillator.type = 'square';
  oscillator.frequency.setValueAtTime(980 + value * 4.2, now);
  oscillator.frequency.exponentialRampToValueAtTime(720 + value * 2.4, now + 0.032);
  gain.gain.setValueAtTime(0.055, now);
  gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.035);
  oscillator.connect(gain);
  gain.connect(tickAudioContext.destination);
  oscillator.start(now);
  oscillator.stop(now + 0.038);
}

function updateVolume(event) {
  volume.value = Number(event.target.value);
  widget?.setVolume(volume.value);
  playVolumeTick(volume.value);
}

function trackVolume() {
  persistPlaybackState();
  trackEvent('audio_volume_change', { provider: 'soundcloud', value: volume.value });
}

function constrainPosition(x, y) {
  if (!playerElement.value) return { x, y };

  const bounds = playerElement.value.getBoundingClientRect();
  return {
    x: Math.min(Math.max(12, x), Math.max(12, window.innerWidth - bounds.width - 12)),
    y: Math.min(Math.max(12, y), Math.max(12, window.innerHeight - bounds.height - 12))
  };
}

function setPlayerPosition(x, y) {
  Object.assign(playerPosition, constrainPosition(x, y), { initialized: true });
}

function startPlayerDrag(event) {
  if (!event.isPrimary || !playerElement.value || isMinimized.value || isMaximized.value || event.target.closest('button')) return;

  const bounds = playerElement.value.getBoundingClientRect();
  activeDrag = {
    pointerId: event.pointerId,
    offsetX: event.clientX - bounds.left,
    offsetY: event.clientY - bounds.top,
    moved: false
  };
  event.currentTarget.setPointerCapture(event.pointerId);
}

function movePlayerDrag(event) {
  if (activeDrag?.pointerId !== event.pointerId) return;

  const nextX = event.clientX - activeDrag.offsetX;
  const nextY = event.clientY - activeDrag.offsetY;
  activeDrag.moved ||= Math.abs(nextX - playerPosition.x) > 3 || Math.abs(nextY - playerPosition.y) > 3;
  setPlayerPosition(nextX, nextY);
}

function stopPlayerDrag(event) {
  if (activeDrag?.pointerId !== event.pointerId) return;

  if (activeDrag.moved) {
    localStorage.setItem('quila-player-position', JSON.stringify({ x: playerPosition.x, y: playerPosition.y }));
    trackEvent('audio_player_move', { provider: 'soundcloud' });
  }
  activeDrag = undefined;
}

function savePlayerMode(mode) {
  localStorage.setItem('quila-player-mode', mode);
  trackEvent('audio_player_toggle', { provider: 'soundcloud', state: mode });
}

function minimizePlayer() {
  isClosed.value = false;
  isMaximized.value = false;
  isMinimized.value = true;
  savePlayerMode('minimized');
}

async function maximizePlayer() {
  isClosed.value = false;
  isMinimized.value = false;
  isMaximized.value = true;
  savePlayerMode('maximized');
}

async function openFloatingPlayer() {
  isClosed.value = false;
  isMinimized.value = false;
  isMaximized.value = false;
  savePlayerMode('expanded');
  await nextTick();
  setPlayerPosition(playerPosition.x, playerPosition.y);
}

function closePlayer() {
  if (isPlaying.value) widget?.pause();
  isClosed.value = true;
  isMinimized.value = false;
  isMaximized.value = false;
  savePlayerMode('closed');
}

onMounted(async () => {
  await nextTick();
  let savedPosition;
  try {
    savedPosition = JSON.parse(localStorage.getItem('quila-player-position') || 'null');
  } catch {
    localStorage.removeItem('quila-player-position');
  }
  const savedMode = localStorage.getItem('quila-player-mode');
  isMinimized.value = false;
  isClosed.value = false;
  isMaximized.value = false;
  await nextTick();
  const playerBounds = playerElement.value.getBoundingClientRect();
  const hero = document.querySelector('.hero');
  const heroBounds = hero?.getBoundingClientRect();
  const heroStyles = hero ? getComputedStyle(hero) : null;
  const defaultX = heroBounds
    ? heroBounds.right - Number.parseFloat(heroStyles.paddingRight) - playerBounds.width
    : window.innerWidth - playerBounds.width - 24;
  const defaultY = heroBounds
    ? heroBounds.top + Number.parseFloat(heroStyles.paddingTop)
    : 24;
  setPlayerPosition(
    savedPosition?.x ?? defaultX,
    savedPosition?.y ?? defaultY
  );
  isMinimized.value = !savedMode || savedMode === 'minimized';
  isClosed.value = savedMode === 'closed';
  isMaximized.value = savedMode === 'maximized';

  const handleResize = () => {
    if (!isMinimized.value && !isMaximized.value && !isClosed.value) {
      setPlayerPosition(playerPosition.x, playerPosition.y);
    }
  };
  window.addEventListener('resize', handleResize, { passive: true });
  removeResizeListener = () => window.removeEventListener('resize', handleResize);

  try {
    const soundCloud = await loadWidgetApi();
    widget = soundCloud.Widget(iframeElement.value);
    widgetEvents = soundCloud.Widget.Events;

    widget.bind(widgetEvents.READY, () => {
      isReady.value = true;
      restorePlaybackState();
    });
    widget.bind(widgetEvents.PLAY, () => {
      isPlaying.value = true;
      widget.getCurrentSoundIndex((index) => {
        currentSoundIndex = index;
      });
      updateCurrentTrack(!isRestoringPlayback);
    });
    widget.bind(widgetEvents.PAUSE, () => {
      isPlaying.value = false;
      persistPlaybackState();
    });
    widget.bind(widgetEvents.FINISH, () => {
      isPlaying.value = false;
      savePlaybackState(0);
    });
    widget.bind(widgetEvents.PLAY_PROGRESS, (progress) => {
      const now = Date.now();
      if (now - lastPlaybackSave < 2000) return;
      lastPlaybackSave = now;
      savePlaybackState(progress.currentPosition);
    });
    widget.bind(widgetEvents.ERROR, () => {
      hasError.value = true;
    });
  } catch {
    hasError.value = true;
  }
});

onBeforeUnmount(() => {
  removeResizeListener?.();
  tickAudioContext?.close();
  if (!widget || !widgetEvents) return;
  [widgetEvents.READY, widgetEvents.PLAY, widgetEvents.PAUSE, widgetEvents.FINISH, widgetEvents.PLAY_PROGRESS, widgetEvents.ERROR]
    .forEach((eventName) => widget.unbind(eventName));
});
</script>

<template>
  <section
    ref="playerElement"
    class="soundcloud-player"
    :class="{
      'is-positioned': playerPosition.initialized,
      'is-minimized': isMinimized,
      'is-closed': isClosed,
      'is-maximized': isMaximized
    }"
    :style="playerStyle"
    aria-label="Player de composições no SoundCloud"
  >
    <iframe
      ref="iframeElement"
      class="soundcloud-embed"
      :src="iframeSource"
      title="Composições de Quila no SoundCloud"
      allow="autoplay; encrypted-media"
      aria-hidden="true"
      tabindex="-1"
    ></iframe>

    <button v-if="isClosed" class="player-launcher" type="button" aria-label="Abrir player flutuante do SoundCloud" @click="openFloatingPlayer">
      <svg aria-hidden="true" viewBox="0 0 32 24" fill="none">
        <path d="M12.5 19.5h13.2a5.3 5.3 0 0 0 .5-10.6A8.3 8.3 0 0 0 10.7 7" fill="currentColor" />
        <path d="M3 12v7M6 9.5V19M9 7v12M12 5.5V19" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
      </svg>
    </button>

    <div
      class="player-bar"
      aria-label="Arraste para mover o player"
      @pointerdown="startPlayerDrag"
      @pointermove="movePlayerDrag"
      @pointerup="stopPlayerDrag"
      @pointercancel="stopPlayerDrag"
    >
      <span class="window-controls" aria-label="Controles da janela">
        <button class="window-close" type="button" aria-label="Fechar player" @pointerdown.stop @click="closePlayer"></button>
        <button class="window-minimize" type="button" aria-label="Minimizar player" :disabled="isMinimized" @pointerdown.stop @click="minimizePlayer"></button>
        <button class="window-maximize" type="button" aria-label="Maximizar player" :disabled="isMaximized" @pointerdown.stop @click="maximizePlayer"></button>
      </span>
      <span class="player-label"><i aria-hidden="true"></i> soundcloud / composições</span>
      <span class="player-status">{{ hasError ? 'indisponível' : isReady ? 'arraste / conectado' : 'carregando' }}</span>
    </div>

    <div class="player-body">
      <a
        class="player-artwork"
        :href="currentTrack?.permalink_url || profileUrl"
        target="_blank"
        rel="noopener noreferrer"
        :aria-label="`Abrir ${currentTrack?.title || 'perfil de Quila'} no SoundCloud`"
        @click="trackEvent('audio_link_click', { provider: 'soundcloud' })"
      >
        <img :src="artworkSource" alt="" />
        <span aria-hidden="true">SC</span>
      </a>

      <div class="track-data" aria-live="polite">
        <span>tocando agora</span>
        <strong>{{ currentTrack?.title || (hasError ? 'Abra no SoundCloud' : 'Preparando o player…') }}</strong>
        <a :href="profileUrl" target="_blank" rel="noopener noreferrer">A New Killa ↗</a>
        <div class="track-details">
          <blockquote>
            <p>{{ currentTrack?.description || 'Uma composição publicada por Quila no SoundCloud.' }}</p>
          </blockquote>
          <a
            class="profile-link"
            :href="currentTrack?.user?.permalink_url || profileUrl"
            target="_blank"
            rel="noopener noreferrer"
            @click="trackEvent('audio_link_click', { provider: 'soundcloud', destination: 'profile' })"
          >
            <span><small>autor no SoundCloud</small>{{ currentTrack?.user?.username || 'A New Killa' }}</span>
            <i aria-hidden="true">↗</i>
          </a>
          <dl>
            <div><dt>duração</dt><dd>{{ formattedDuration }}</dd></div>
            <div><dt>gênero</dt><dd>{{ currentTrack?.genre || 'indefinido' }}</dd></div>
            <div><dt>plays</dt><dd>{{ formattedPlays }}</dd></div>
          </dl>
        </div>
      </div>

      <div class="player-controls" aria-label="Controles de reprodução">
        <div class="control-track-summary" aria-hidden="true">
          <img :src="artworkSource" alt="" />
          <span>
            <small>tocando agora</small>
            <strong>{{ currentTrack?.title || 'Preparando o player…' }}</strong>
          </span>
        </div>
        <label
          class="volume-control"
          :class="{ 'is-muted': volume === 0 }"
          :style="{ '--knob-angle': `${-135 + volume * 2.7}deg`, '--volume-level': `${volume * 2.7}deg` }"
        >
          <span class="volume-knob" aria-hidden="true"><i></i></span>
          <span class="sr-only">Volume</span>
          <input
            type="range"
            min="0"
            max="100"
            step="1"
            :value="volume"
            :disabled="!isReady"
            @input="updateVolume"
            @change="trackVolume"
          />
          <output aria-live="polite">{{ volume }}</output>
        </label>
        <button type="button" :disabled="!isReady" aria-label="Faixa anterior" @click="changeTrack('prev')">
          <span aria-hidden="true">←</span>
        </button>
        <button
          class="play-control"
          type="button"
          :disabled="!isReady"
          :aria-label="isPlaying ? 'Pausar' : 'Reproduzir'"
          :aria-pressed="isPlaying"
          @click="togglePlayback"
        >
          <span aria-hidden="true">{{ isPlaying ? 'Ⅱ' : '▶' }}</span>
        </button>
        <button type="button" :disabled="!isReady" aria-label="Próxima faixa" @click="changeTrack('next')">
          <span aria-hidden="true">→</span>
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.soundcloud-player {
  position: fixed;
  z-index: 70;
  right: 24px;
  bottom: 24px;
  width: min(420px, calc(100vw - 24px));
  border: 1px solid rgb(255 255 255 / 34%);
  color: #11100e;
  background: #f2c94c;
  box-shadow: 8px 8px 0 rgb(98 212 156 / 62%);
  opacity: 0;
  transform: rotate(-0.7deg);
  transition: box-shadow 250ms ease, opacity 180ms ease, transform 250ms ease;
}

@media (min-width: 768px) {
  .soundcloud-player:not(.is-minimized) {
    width: clamp(320px, 30vw, 420px);
  }
}

.soundcloud-player.is-positioned {
  right: auto;
  bottom: auto;
  opacity: 1;
}

.soundcloud-player.is-minimized {
  top: auto !important;
  right: 0;
  bottom: 0;
  left: 0 !important;
  display: grid;
  width: 100%;
  grid-template-columns: minmax(210px, 0.35fr) minmax(0, 1fr);
  border-right: 0;
  border-bottom: 0;
  border-left: 0;
  box-shadow: 0 -5px 0 rgb(98 212 156 / 50%);
  transform: none;
}

.soundcloud-player.is-closed {
  top: auto !important;
  right: 12px;
  bottom: 12px;
  left: auto !important;
  width: auto;
  border: 0;
  background: transparent;
  box-shadow: none;
  transform: none;
}

.soundcloud-player.is-closed .player-bar,
.soundcloud-player.is-closed .player-body {
  display: none;
}

.soundcloud-player.is-maximized {
  inset: 0 !important;
  display: flex;
  width: 100%;
  height: 100dvh;
  flex-direction: column;
  overflow: auto;
  border: 0;
  background: #f2c94c;
  box-shadow: none;
  overscroll-behavior: contain;
  transform: none;
}

.soundcloud-player:hover,
.soundcloud-player:focus-within {
  box-shadow: 12px 12px 0 #62d49c;
  transform: rotate(0deg) translateY(-3px);
}

.soundcloud-player.is-minimized:hover,
.soundcloud-player.is-minimized:focus-within {
  box-shadow: 0 -5px 0 #62d49c;
  transform: none;
}

.soundcloud-player.is-closed:hover,
.soundcloud-player.is-closed:focus-within {
  box-shadow: none;
  transform: translateY(-3px);
}

.soundcloud-player.is-maximized:hover,
.soundcloud-player.is-maximized:focus-within {
  box-shadow: none;
  transform: none;
}

.soundcloud-embed {
  position: absolute;
  width: 1px;
  height: 1px;
  border: 0;
  opacity: 0;
  pointer-events: none;
}

.player-bar {
  display: flex;
  min-height: 38px;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 0 12px;
  color: #ffffff;
  background: #11100e;
  font-family: 'Martian Mono', ui-monospace, monospace;
  font-size: 8px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  touch-action: none;
  user-select: none;
}

.window-controls {
  display: flex;
  flex: none;
  align-items: center;
  gap: 7px;
}

.window-controls button {
  width: 11px;
  height: 11px;
  border: 1px solid rgb(0 0 0 / 18%);
  border-radius: 50%;
  padding: 0;
}

.window-close {
  background: #ff5f57;
}

.window-minimize {
  background: #febc2e;
}

.window-maximize {
  background: #28c840;
}

.window-controls button:focus-visible {
  outline: 2px solid #ffffff;
  outline-offset: 2px;
}

.window-controls button:disabled {
  opacity: 0.38;
  filter: grayscale(0.7);
}

.player-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.player-bar i {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #ff5500;
  box-shadow: 0 0 0 3px rgb(255 85 0 / 20%);
}

.player-body {
  display: grid;
  grid-template-columns: 82px minmax(0, 1fr);
  gap: 16px;
  padding: 16px;
}

.soundcloud-player.is-maximized .player-bar {
  position: sticky;
  z-index: 2;
  top: 0;
  order: 1;
  min-height: 48px;
  padding-inline: clamp(16px, 3vw, 48px);
}

.soundcloud-player.is-maximized .player-status {
  display: none;
}

.soundcloud-player.is-maximized .player-body {
  order: 2;
  display: grid;
  width: 100%;
  grid-template-columns: minmax(280px, 0.72fr) minmax(320px, 1fr);
  grid-template-rows: auto auto;
  gap: clamp(28px, 5vw, 80px);
  padding: clamp(32px, 6vw, 96px) clamp(32px, 6vw, 96px) 128px;
}

.soundcloud-player.is-maximized .player-artwork {
  grid-row: 1 / span 2;
  width: 100%;
  max-width: 560px;
  justify-self: end;
}

.soundcloud-player.is-maximized .player-artwork img {
  filter: none;
  mix-blend-mode: normal;
}

.soundcloud-player.is-maximized .player-artwork > span {
  display: none;
}

.soundcloud-player.is-maximized .track-data {
  align-self: center;
}

.soundcloud-player.is-maximized .track-data > span,
.soundcloud-player.is-maximized .track-data > strong,
.soundcloud-player.is-maximized .track-data > a {
  display: none;
}

.soundcloud-player.is-maximized .track-details {
  display: block;
  margin-top: 0;
}

.soundcloud-player.is-maximized .player-controls {
  position: fixed;
  z-index: 4;
  right: 0;
  bottom: 0;
  left: 0;
  min-height: 76px;
  flex-wrap: nowrap;
  justify-content: flex-end;
  gap: 10px;
  padding: 9px clamp(16px, 4vw, 64px);
  border-top: 1px solid #11100e;
  color: #11100e;
  background: #f2c94c;
  box-shadow: 0 -5px 0 rgb(98 212 156 / 50%);
}

.player-artwork {
  position: relative;
  grid-row: span 2;
  aspect-ratio: 1;
  overflow: hidden;
  border: 1px solid #11100e;
  background: #ff5500;
}

.player-artwork img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(1) contrast(1.08);
  mix-blend-mode: multiply;
}

.player-artwork span {
  position: absolute;
  right: 5px;
  bottom: 4px;
  color: #ffffff;
  font-family: 'Martian Mono', ui-monospace, monospace;
  font-size: 8px;
  font-weight: 700;
}

.track-data {
  min-width: 0;
}

.track-data > span,
.track-data a {
  font-family: 'Martian Mono', ui-monospace, monospace;
  font-size: 8px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.track-details {
  display: none;
  max-width: 680px;
  margin-top: clamp(28px, 4vw, 56px);
}

.track-details dl {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin: 28px 0 0;
  border-top: 1px solid #11100e;
  border-bottom: 1px solid #11100e;
}

.track-details .profile-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-top: 32px;
  border-block: 1px solid #11100e;
  padding: 18px 4px;
  font-size: clamp(26px, 3.4vw, 50px);
  font-weight: 800;
  letter-spacing: -0.045em;
  line-height: 0.92;
  transition: color 150ms ease, padding 280ms cubic-bezier(0.22, 1, 0.36, 1);
}

.track-details .profile-link small {
  display: block;
  margin-bottom: 8px;
  font-family: 'Martian Mono', ui-monospace, monospace;
  font-size: 8px;
  font-weight: 500;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  opacity: 0.58;
}

.track-details .profile-link i {
  flex: none;
  font-size: 0.75em;
  font-style: normal;
  transition: transform 280ms cubic-bezier(0.22, 1, 0.36, 1);
}

.track-details .profile-link:hover,
.track-details .profile-link:focus-visible {
  color: #ff5500;
  padding-inline: 12px;
  outline: none;
}

.track-details .profile-link:hover i,
.track-details .profile-link:focus-visible i {
  transform: translate(4px, -4px);
}

.track-details dl > div {
  padding: 12px 14px;
  border-right: 1px solid #11100e;
}

.track-details dl > div:last-child {
  border-right: 0;
}

.track-details dt {
  margin-bottom: 6px;
  font-family: 'Martian Mono', ui-monospace, monospace;
  font-size: 8px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  opacity: 0.58;
}

.track-details dd {
  margin: 0;
  font-weight: 700;
}

.track-details blockquote {
  position: relative;
  margin: 0;
  padding: clamp(28px, 4vw, 52px) clamp(22px, 4vw, 54px);
  border: 1px solid #11100e;
  background: rgb(255 255 255 / 24%);
  box-shadow: 7px 7px 0 rgb(17 16 14 / 18%);
  transform: rotate(-0.5deg);
}

.track-details blockquote::before {
  position: absolute;
  top: -0.24em;
  left: 12px;
  color: #ff5500;
  content: '“';
  font-family: Georgia, serif;
  font-size: clamp(72px, 9vw, 132px);
  line-height: 1;
}

.track-details blockquote p {
  position: relative;
  max-width: 58ch;
  margin: 0;
  font-size: clamp(17px, 1.55vw, 23px);
  font-style: italic;
  font-weight: 550;
  letter-spacing: -0.015em;
  line-height: 1.55;
  white-space: pre-line;
}

.track-data > span {
  opacity: 0.58;
}

.track-data strong {
  display: block;
  margin: 5px 0 7px;
  overflow: hidden;
  font-size: clamp(18px, 2vw, 25px);
  letter-spacing: -0.035em;
  line-height: 1;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.track-data a {
  border-bottom: 1px solid currentColor;
}

.player-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
}

.control-track-summary {
  display: none;
  min-width: 0;
  flex: 1;
  align-items: center;
  gap: 12px;
  margin-right: auto;
}

.soundcloud-player.is-maximized .control-track-summary {
  display: flex;
}

.control-track-summary img {
  width: 48px;
  height: 48px;
  flex: none;
  border: 1px solid #11100e;
  object-fit: cover;
}

.control-track-summary > span {
  min-width: 0;
}

.control-track-summary small {
  display: block;
  margin-bottom: 3px;
  font-family: 'Martian Mono', ui-monospace, monospace;
  font-size: 7px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  opacity: 0.58;
}

.control-track-summary strong {
  display: block;
  overflow: hidden;
  font-size: clamp(14px, 1.6vw, 20px);
  letter-spacing: -0.025em;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.volume-control {
  position: relative;
  display: grid;
  width: 48px;
  height: 48px;
  flex: none;
  place-items: center;
  margin-right: 4px;
  font-family: 'Martian Mono', ui-monospace, monospace;
  font-size: 7px;
  font-weight: 700;
}

.volume-knob {
  position: relative;
  display: block;
  width: 34px;
  height: 34px;
  border: 1px solid #11100e;
  border-radius: 50%;
  background: radial-gradient(circle at 38% 34%, #ffffff 0 4%, #d8b23e 42%, #a88425 100%);
  box-shadow: 0 3px 0 rgb(17 16 14 / 24%);
  transition: box-shadow 180ms ease, transform 220ms cubic-bezier(0.22, 1, 0.36, 1);
}

.volume-knob::before {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  background: conic-gradient(
    from -135deg,
    #ff5500 0deg var(--volume-level),
    rgb(17 16 14 / 20%) var(--volume-level) 270deg,
    transparent 270deg 360deg
  );
  content: '';
  mask: radial-gradient(circle, transparent 58%, #000 61%);
}

.volume-knob i {
  position: absolute;
  inset: 4px;
  border-radius: 50%;
  transform: rotate(var(--knob-angle));
  transition: transform 100ms ease-out;
}

.volume-knob i::after {
  position: absolute;
  top: 0;
  left: 50%;
  width: 2px;
  height: 8px;
  border-radius: 999px;
  background: #11100e;
  content: '';
  transform: translateX(-50%);
}

.volume-control.is-muted .volume-knob i::after {
  background: #ff5500;
}

.volume-control:hover .volume-knob,
.volume-control:focus-within .volume-knob {
  box-shadow: 0 4px 0 rgb(17 16 14 / 28%), 0 0 0 5px rgb(255 85 0 / 16%);
  transform: scale(1.08);
}

.volume-control:has(input:active) .volume-knob {
  box-shadow: 0 1px 0 rgb(17 16 14 / 28%), 0 0 0 8px rgb(255 85 0 / 20%);
  transform: scale(0.94);
}

.volume-control input[type='range'] {
  position: absolute;
  z-index: 2;
  inset: 0;
  width: 100%;
  height: 100%;
  margin: 0;
  opacity: 0;
}

.volume-control output {
  position: absolute;
  bottom: calc(100% + 5px);
  left: 50%;
  min-width: 25px;
  padding: 3px 4px;
  border: 1px solid #11100e;
  border-radius: 2px;
  color: #ffffff;
  background: #11100e;
  font-size: 7px;
  text-align: center;
  opacity: 0;
  transform: translate(-50%, 4px);
  transition: opacity 120ms ease, transform 180ms ease;
  pointer-events: none;
}

.volume-control:hover output,
.volume-control:focus-within output {
  opacity: 1;
  transform: translate(-50%, 0);
}

.volume-control input:disabled {
  cursor: not-allowed;
}

.volume-control:has(input:disabled) {
  opacity: 0.4;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  clip-path: inset(50%);
}

.player-launcher {
  display: grid;
  width: 48px;
  height: 48px;
  place-items: center;
  border: 1px solid #11100e;
  border-radius: 5px;
  color: #ffffff;
  background: #ff5500;
  box-shadow: 5px 5px 0 rgb(17 16 14 / 30%);
  font-family: 'Martian Mono', ui-monospace, monospace;
  font-size: 10px;
  font-weight: 700;
}

.player-launcher svg {
  width: 30px;
  height: 24px;
}

.player-controls button {
  display: grid;
  width: 34px;
  height: 30px;
  place-items: center;
  border: 1px solid #11100e;
  border-radius: 2px;
  color: #11100e;
  background: transparent;
  font-weight: 700;
  transition: color 120ms ease, background-color 120ms ease, transform 120ms ease;
}

.player-controls .play-control {
  width: 46px;
  background: #11100e;
  color: #ffffff;
}

.player-controls button:hover:not(:disabled),
.player-controls button:focus-visible {
  color: #ffffff;
  background: #ff5500;
  outline: none;
  transform: translateY(-2px);
}

.player-controls button:disabled {
  opacity: 0.38;
}

.soundcloud-player.is-minimized .player-bar {
  min-height: 64px;
}

.soundcloud-player.is-minimized .player-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.soundcloud-player.is-minimized .player-status {
  display: none;
}

.soundcloud-player.is-minimized .player-body {
  grid-template-columns: 42px minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
}

.soundcloud-player.is-minimized .player-artwork {
  grid-row: auto;
  width: 42px;
}

.soundcloud-player.is-minimized .track-data strong {
  margin-bottom: 0;
  font-size: 18px;
}

.soundcloud-player.is-minimized .track-data a {
  display: none;
}

@media (max-width: 767px) {
  .soundcloud-player.is-maximized .player-body {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
    gap: 28px;
    padding: 28px 20px 40px;
  }

  .soundcloud-player.is-maximized .player-artwork {
    grid-row: auto;
    width: min(100%, 420px);
    justify-self: center;
  }

  .soundcloud-player.is-maximized .track-data,
  .soundcloud-player.is-maximized .player-controls {
    width: min(100%, 560px);
    justify-self: center;
  }

  .soundcloud-player.is-maximized .player-controls {
    width: 100%;
    min-height: 70px;
    padding: 8px 12px;
  }

  .soundcloud-player.is-maximized .control-track-summary img {
    width: 42px;
    height: 42px;
  }

  .soundcloud-player.is-maximized .volume-control {
    display: none;
  }

}

@media (max-width: 420px) {
  .soundcloud-player {
    width: calc(100vw - 24px);
  }

  .player-body {
    grid-template-columns: 64px minmax(0, 1fr);
    gap: 12px;
    padding: 12px;
  }

  .player-controls button {
    width: 32px;
  }

  .player-controls .play-control {
    width: 42px;
  }

  .soundcloud-player.is-minimized {
    grid-template-columns: 84px minmax(0, 1fr);
  }

  .soundcloud-player.is-minimized .player-bar {
    justify-content: center;
    padding: 0;
  }

  .soundcloud-player.is-minimized .player-label,
  .soundcloud-player.is-minimized .player-status {
    display: none;
  }

  .soundcloud-player.is-minimized .player-body {
    grid-template-columns: minmax(0, 1fr) auto;
  }

  .soundcloud-player.is-minimized .player-artwork {
    display: none;
  }

}
</style>
