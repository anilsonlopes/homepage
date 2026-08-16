<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue';
import WordHighlight from './components/WordHighlight.vue';
import { trackEvent } from '@/analytics.js';

const socialLinks = [
  { name: 'Twitch', handle: '@quilamcz', href: 'https://www.twitch.tv/quilamcz' },
  { name: 'YouTube', handle: '@quilamcz', href: 'https://www.youtube.com/@quilamcz' },
  { name: 'Instagram', handle: '@quilamcz', href: 'https://www.instagram.com/quilamcz/' },
  { name: 'TikTok', handle: '@nissobmx', href: 'https://www.tiktok.com/@quilamcz' },
  { name: 'Discord', handle: 'Servidor de quila', href: 'https://discord.gg/t2qcYDnKGd' },
  { name: 'E-mail', handle: 'nissobmx@gmail.com', href: 'mailto:nissobmx@gmail.com' }
];

const muralNotes = reactive([
  { id: 'local', label: 'local', value: 'Maceió, BRA', x: 8, y: 13, rotation: -4, color: '#f2c94c', z: 1 },
  { id: 'tempo', label: 'trajetória', value: '16 anos com código', x: 55, y: 10, rotation: 3, color: '#62d49c', z: 2 },
  { id: 'nascimento', label: 'desde', value: '21 ago 1992', x: 18, y: 58, rotation: 2, color: '#8db8ff', z: 3 },
  { id: 'stack', label: 'ferramentas', value: 'Vue · Nuxt · Bun', x: 54, y: 56, rotation: -3, color: '#d5a6ff', z: 4 },
  { id: 'contato', label: 'contato', value: 'nissobmx@gmail.com', x: 35, y: 34, rotation: -1, color: '#ff927d', z: 5 }
]);

const experiments = [
  {
    number: '01',
    title: 'yTv',
    description: 'Simulador de programação de TV com vídeos do YouTube, grade predefinida, reprodução sincronizada e comerciais autorais.',
    tags: ['Nuxt', 'Vue', 'TypeScript'],
    href: 'https://ytv.quila.dev',
    repository: 'https://github.com/anilsonlopes/ytv',
    status: 'no ar',
    color: '#c63228',
    pattern: 'diagonal'
  },
  {
    number: '02',
    title: 'Ranking',
    description: 'Ferramenta para criar e compartilhar páginas com listas visuais que simulam rankings.',
    tags: ['Nuxt', 'Vue', 'Tailwind'],
    href: 'https://ranking.quila.dev',
    repository: 'https://github.com/anilsonlopes/ranking',
    status: 'no ar',
    color: '#d76b00',
    pattern: 'grid'
  },
  {
    number: '03',
    title: 'Toggle',
    description: 'Aplicativo minimalista para comunicar, sem distrações, se você está disponível ou ocupado.',
    tags: ['Nuxt', 'PWA', 'Nuxt Content'],
    href: 'https://toggle.quila.dev',
    repository: 'https://github.com/anilsonlopes/toggle',
    status: 'no ar',
    color: '#007a46',
    pattern: 'checker'
  },
  {
    number: '04',
    title: 'Live',
    description: 'Experiência focada para assistir ao canal Quila na Twitch, com abertura animada e player imersivo.',
    tags: ['Nuxt 4', 'Vue', 'Twitch'],
    href: 'https://live.quila.dev',
    repository: 'https://github.com/anilsonlopes/live',
    status: 'no ar',
    color: '#7138a8',
    pattern: 'cross'
  },
  {
    number: '05',
    title: 'Pseudo',
    description: 'Protótipo visual de uma plataforma social com órbitas animadas e estrutura de rotas para conversas.',
    tags: ['Nuxt', 'Vue', 'Motion'],
    href: 'https://pseudo.quila.studio',
    repository: 'https://github.com/anilsonlopes/pseudo',
    status: 'protótipo',
    color: '#1768c4',
    pattern: 'dots'
  },
  {
    number: '06',
    title: 'Context Directory',
    description: 'Base de conhecimento em português, estruturada em Markdown para consumo por agentes de IA.',
    tags: ['Nuxt 4', 'Docus', 'Markdown'],
    href: 'https://context-directory.labafero.com',
    repository: 'https://github.com/anilsonlopes/context-directory',
    status: 'no ar',
    color: '#00777c',
    pattern: 'horizontal'
  }
];

const activeExperimentIndex = ref(0);
const activeExperiment = computed(() => experiments[activeExperimentIndex.value]);
const cursorElement = ref(null);
const muralBoard = ref(null);
const theme = ref('light');
let activeMuralDrag;
let muralZIndex = muralNotes.length;

function toggleTheme() {
  theme.value = theme.value === 'light' ? 'dark' : 'light';
  document.documentElement.dataset.theme = theme.value;
  localStorage.setItem('quila-theme', theme.value);
  trackEvent('theme_change', { theme: theme.value });
}

function selectExperiment(index, interactionMethod = 'click') {
  activeExperimentIndex.value = index;
  trackEvent('select_content', {
    content_type: 'experiment',
    content_id: experiments[index].title.toLowerCase().replaceAll(' ', '-'),
    interaction_method: interactionMethod
  });
}

function trackNavigation(destination) {
  trackEvent('navigation_click', { destination });
}

function trackExperimentLink(destination) {
  trackEvent('experiment_link_click', {
    experiment_id: activeExperiment.value.title.toLowerCase().replaceAll(' ', '-'),
    destination
  });
}

function trackContact(channel) {
  trackEvent('contact_click', { channel: channel.toLowerCase() });
}

function navigateTabs(event) {
  const keys = ['ArrowLeft', 'ArrowRight', 'Home', 'End'];
  if (!keys.includes(event.key)) return;

  event.preventDefault();

  let nextIndex = activeExperimentIndex.value;
  if (event.key === 'Home') nextIndex = 0;
  if (event.key === 'End') nextIndex = experiments.length - 1;
  if (event.key === 'ArrowLeft') {
    nextIndex = (activeExperimentIndex.value - 1 + experiments.length) % experiments.length;
  }
  if (event.key === 'ArrowRight') {
    nextIndex = (activeExperimentIndex.value + 1) % experiments.length;
  }

  selectExperiment(nextIndex, 'keyboard');
  nextTick(() => document.getElementById(`experiment-tab-${activeExperimentIndex.value}`)?.focus());
}

function startMuralDrag(event, note) {
  if (!event.isPrimary || !muralBoard.value) return;

  muralZIndex += 1;
  note.z = muralZIndex;
  activeMuralDrag = {
    id: note.id,
    pointerId: event.pointerId,
    startX: event.clientX,
    startY: event.clientY,
    noteX: note.x,
    noteY: note.y,
    moved: false
  };
  event.currentTarget.setPointerCapture(event.pointerId);
}

function moveMuralDrag(event, note) {
  if (activeMuralDrag?.id !== note.id || activeMuralDrag.pointerId !== event.pointerId || !muralBoard.value) return;

  const board = muralBoard.value.getBoundingClientRect();
  const noteBounds = event.currentTarget.getBoundingClientRect();
  const deltaX = ((event.clientX - activeMuralDrag.startX) / board.width) * 100;
  const deltaY = ((event.clientY - activeMuralDrag.startY) / board.height) * 100;
  const maxX = Math.max(2, 98 - (noteBounds.width / board.width) * 100);
  const maxY = Math.max(2, 98 - (noteBounds.height / board.height) * 100);
  note.x = Math.min(maxX, Math.max(2, activeMuralDrag.noteX + deltaX));
  note.y = Math.min(maxY, Math.max(2, activeMuralDrag.noteY + deltaY));
  activeMuralDrag.moved ||= Math.abs(event.clientX - activeMuralDrag.startX) > 4
    || Math.abs(event.clientY - activeMuralDrag.startY) > 4;
}

function stopMuralDrag(event, note) {
  if (activeMuralDrag?.pointerId !== event.pointerId) return;
  if (activeMuralDrag.moved) {
    trackEvent('mural_note_move', { note_id: note.id, interaction_method: 'pointer' });
  }
  activeMuralDrag = undefined;
}

function moveMuralNote(event, note) {
  const directions = {
    ArrowLeft: [-2, 0],
    ArrowRight: [2, 0],
    ArrowUp: [0, -2],
    ArrowDown: [0, 2]
  };
  const movement = directions[event.key];
  if (!movement) return;

  event.preventDefault();
  const board = muralBoard.value?.getBoundingClientRect();
  const noteBounds = event.currentTarget.getBoundingClientRect();
  const maxX = board ? Math.max(2, 98 - (noteBounds.width / board.width) * 100) : 82;
  const maxY = board ? Math.max(2, 98 - (noteBounds.height / board.height) * 100) : 78;
  note.x = Math.min(maxX, Math.max(2, note.x + movement[0]));
  note.y = Math.min(maxY, Math.max(2, note.y + movement[1]));
  trackEvent('mural_note_move', { note_id: note.id, interaction_method: 'keyboard' });
}

let revealObserver;
let removeCursorListeners;
let removeThemeListener;

onMounted(() => {
  theme.value = document.documentElement.dataset.theme || 'light';
  const systemTheme = window.matchMedia('(prefers-color-scheme: dark)');
  const handleSystemThemeChange = (event) => {
    if (localStorage.getItem('quila-theme')) return;

    theme.value = event.matches ? 'dark' : 'light';
    document.documentElement.dataset.theme = theme.value;
  };

  systemTheme.addEventListener('change', handleSystemThemeChange);
  removeThemeListener = () => systemTheme.removeEventListener('change', handleSystemThemeChange);

  const revealElements = document.querySelectorAll('[data-reveal]');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (window.matchMedia('(pointer: fine)').matches && cursorElement.value) {
    const cursor = cursorElement.value;

    const handlePointerMove = (event) => {
      cursor.style.setProperty('--cursor-x', `${event.clientX}px`);
      cursor.style.setProperty('--cursor-y', `${event.clientY}px`);
      cursor.classList.add('is-visible');
    };

    const handlePointerLeave = () => cursor.classList.remove('is-visible');
    const handlePointerEnter = () => cursor.classList.add('is-visible');

    document.documentElement.classList.add('custom-cursor');
    window.addEventListener('pointermove', handlePointerMove, { passive: true });
    document.documentElement.addEventListener('mouseleave', handlePointerLeave);
    document.documentElement.addEventListener('mouseenter', handlePointerEnter);

    removeCursorListeners = () => {
      window.removeEventListener('pointermove', handlePointerMove);
      document.documentElement.removeEventListener('mouseleave', handlePointerLeave);
      document.documentElement.removeEventListener('mouseenter', handlePointerEnter);
      document.documentElement.classList.remove('custom-cursor');
    };
  }

  if (reducedMotion || !('IntersectionObserver' in window)) {
    revealElements.forEach((element) => element.classList.add('is-visible'));
    return;
  }

  document.documentElement.classList.add('reveal-ready');
  revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;

      entry.target.classList.add('is-visible');
      revealObserver.unobserve(entry.target);
    });
  }, {
    rootMargin: '0px 0px -8% 0px',
    threshold: 0.12
  });

  revealElements.forEach((element) => revealObserver.observe(element));
});

onBeforeUnmount(() => {
  revealObserver?.disconnect();
  removeCursorListeners?.();
  removeThemeListener?.();
});
</script>

<template>
  <div class="site-shell">
    <span ref="cursorElement" class="inverted-cursor" aria-hidden="true"></span>
    <nav class="site-nav" aria-label="Navegação principal" data-reveal>
      <a class="brand" href="/" aria-label="quila.dev — página inicial">
        <span class="brand-mark" aria-hidden="true">q</span>
        <span>quila.dev</span>
      </a>

      <div class="nav-actions">
        <span class="availability">
          <span class="availability-dot" aria-hidden="true"></span>
          disponível para projetos
        </span>
        <button
          class="theme-toggle"
          type="button"
          :aria-pressed="theme === 'dark'"
          :aria-label="theme === 'dark' ? 'Ativar tema claro' : 'Ativar tema escuro'"
          @click="toggleTheme"
        >
          <span class="theme-toggle-track" aria-hidden="true">
            <span class="theme-toggle-thumb">
              <svg class="theme-icon theme-icon-sun" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="8" r="2.5" stroke="currentColor" />
                <path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.05 3.05l1.4 1.4M11.55 11.55l1.4 1.4M12.95 3.05l-1.4 1.4M4.45 11.55l-1.4 1.4" stroke="currentColor" stroke-linecap="round" />
              </svg>
              <svg class="theme-icon theme-icon-moon" viewBox="0 0 16 16" fill="none">
                <path d="M13.5 10.3A5.7 5.7 0 0 1 5.7 2.5a5.7 5.7 0 1 0 7.8 7.8Z" stroke="currentColor" stroke-linejoin="round" />
              </svg>
            </span>
          </span>
        </button>
      </div>
    </nav>

    <main>
      <section class="hero" aria-labelledby="hero-title">
        <p class="eyebrow" data-reveal><span>01</span> sobre</p>

        <h1 id="hero-title" data-reveal style="--reveal-delay: 80ms">
          Experimentos de um desenvolvedor frontend web
          <WordHighlight
            target="psuedo-autodidata"
            reveal="O sujeito não tem diploma e não consegue reconhecer que aprender tudo sozinho, já que toda informação obtida partiu de alguém antes."
          />
        </h1>

        <div class="hero-footer" data-reveal style="--reveal-delay: 160ms">
          <p class="intro">
            Oi, eu sou o
            <WordHighlight target="Quila" reveal="Vulgo para Anilson Lopes dos Santos" />. Mexo com os códigos há 16 anos, 9
            deles focado no desenvolvimento front-end para
            <WordHighlight target="web" reveal="Você está aqui!" />. Acredito que o desenvolvimento
            <WordHighlight target="performático" reveal="Veja bem! É o desenvolvimento que deve ser performático!" />,
            acessível e escalável pode ser alcançado se fizer o que eu digo.
            <WordHighlight reveal="Fiz piadinha mas a conversa é séria!"><em>Hehe</em></WordHighlight>.
          </p>

          <a class="contact-link" href="#contato" @click="trackNavigation('contact')">
            vamos conversar
            <span aria-hidden="true">↓</span>
          </a>
        </div>
      </section>

      <section class="experiments" aria-labelledby="experiments-title">
        <div class="experiments-heading" data-reveal>
          <p class="eyebrow"><span>02</span> experimentos</p>
          <h2 id="experiments-title">Ideias em<br>movimento.</h2>
          <p>
            Um espaço para testar tecnologias, desmontar padrões e transformar curiosidade em experiências para a web.
          </p>
        </div>

        <div class="experiment-browser" data-reveal>
          <div class="experiment-tabs" role="tablist" aria-label="Selecionar experimento" @keydown="navigateTabs">
            <button
              v-for="(experiment, index) in experiments"
              :id="`experiment-tab-${index}`"
              :key="experiment.title"
              type="button"
              role="tab"
              :aria-selected="activeExperimentIndex === index"
              :aria-controls="`experiment-panel-${index}`"
              :tabindex="activeExperimentIndex === index ? 0 : -1"
              :style="{ '--tab-color': experiment.color }"
              @click="selectExperiment(index, 'click')"
            >
              <span>{{ experiment.number }}</span>
              {{ experiment.title }}
            </button>
          </div>

          <Transition name="experiment-panel" mode="out-in">
            <article
              :id="`experiment-panel-${activeExperimentIndex}`"
              :key="activeExperiment.title"
              :class="['experiment-card', `pattern-${activeExperiment.pattern}`]"
              :style="{ '--experiment-color': activeExperiment.color }"
              role="tabpanel"
              :aria-labelledby="`experiment-tab-${activeExperimentIndex}`"
              tabindex="0"
            >
              <div class="experiment-meta">
                <span>experimento {{ activeExperiment.number }}</span>
                <span class="experiment-status"><i aria-hidden="true"></i> {{ activeExperiment.status }}</span>
              </div>
              <h3>{{ activeExperiment.title }}</h3>
              <p>{{ activeExperiment.description }}</p>
              <ul class="experiment-tags" :aria-label="`Tecnologias de ${activeExperiment.title}`">
                <li v-for="tag in activeExperiment.tags" :key="tag">{{ tag }}</li>
              </ul>
              <div class="experiment-actions">
                <a
                  :href="activeExperiment.href"
                  target="_blank"
                  rel="noopener noreferrer"
                  @click="trackExperimentLink('project')"
                >
                  visitar <span aria-hidden="true">↗</span>
                </a>
                <a
                  :href="activeExperiment.repository"
                  target="_blank"
                  rel="noopener noreferrer"
                  @click="trackExperimentLink('repository')"
                >ver código</a>
              </div>
            </article>
          </Transition>
        </div>
      </section>

      <section id="contato" class="contact" aria-labelledby="contact-title">
        <div class="contact-heading" data-reveal>
          <p class="eyebrow"><span>03</span> contato</p>
          <h2 id="contact-title">Onde me<br>encontrar.</h2>
        </div>

        <ul class="social-links" aria-label="Redes sociais e contato">
          <li
            v-for="(social, index) in socialLinks"
            :key="social.name"
            data-reveal
            :style="{ '--reveal-delay': `${index * 55}ms` }"
          >
            <a
              :href="social.href"
              :target="social.href.startsWith('http') ? '_blank' : undefined"
              :rel="social.href.startsWith('http') ? 'noopener noreferrer' : undefined"
              @click="trackContact(social.name)"
            >
              <span class="social-index">{{ String(index + 1).padStart(2, '0') }}</span>
              <span class="social-name">{{ social.name }}</span>
              <span class="social-handle">{{ social.handle }}</span>
              <span class="social-arrow" aria-hidden="true">↗</span>
            </a>
          </li>
        </ul>
      </section>
    </main>

    <footer class="site-footer">
      <div class="footer-panel-bar">
        <span><i aria-hidden="true"></i> 04 / mural</span>
        <span>arraste os cartões para reorganizar</span>
      </div>

      <div ref="muralBoard" class="footer-mural" aria-label="Mural interativo sobre Quila">
        <button
          v-for="note in muralNotes"
          :key="note.id"
          class="mural-note"
          type="button"
          :style="{
            '--note-x': `${note.x}%`,
            '--note-y': `${note.y}%`,
            '--note-rotation': `${note.rotation}deg`,
            '--note-color': note.color,
            '--note-z': note.z
          }"
          :aria-label="`${note.label}: ${note.value}. Arraste ou use as setas para mover.`"
          @pointerdown="startMuralDrag($event, note)"
          @pointermove="moveMuralDrag($event, note)"
          @pointerup="stopMuralDrag($event, note)"
          @pointercancel="stopMuralDrag($event, note)"
          @keydown="moveMuralNote($event, note)"
        >
          <span>{{ note.label }}</span>
          <strong>{{ note.value }}</strong>
          <i aria-hidden="true"></i>
        </button>
      </div>

      <div class="footer-bottom">
        <p class="footer-signature">feito em Maceió para a web.</p>
        <p class="copyright">© {{ new Date().getFullYear() }} quila.dev</p>
      </div>
    </footer>
  </div>
</template>
