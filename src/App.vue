<script setup>
import { onBeforeUnmount, onMounted } from 'vue';
import WordHighlight from './components/WordHighlight.vue';

const socialLinks = [
  { name: 'Twitch', handle: '@quilamcz', href: 'https://www.twitch.tv/quilamcz' },
  { name: 'YouTube', handle: '@quilamcz', href: 'https://www.youtube.com/@quilamcz' },
  { name: 'Instagram', handle: '@quilamcz', href: 'https://www.instagram.com/quilamcz/' },
  { name: 'TikTok', handle: '@nissobmx', href: 'https://www.tiktok.com/@quilamcz' },
  { name: 'Discord', handle: 'Servidor de quila', href: 'https://discord.gg/t2qcYDnKGd' },
  { name: 'E-mail', handle: 'nissobmx@gmail.com', href: 'mailto:nissobmx@gmail.com' }
];

let revealObserver;

onMounted(() => {
  const revealElements = document.querySelectorAll('[data-reveal]');

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) {
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

onBeforeUnmount(() => revealObserver?.disconnect());
</script>

<template>
  <div class="site-shell">
    <nav class="site-nav" aria-label="Navegação principal" data-reveal>
      <a class="brand" href="/" aria-label="quila.dev — página inicial">
        <span class="brand-mark" aria-hidden="true">q</span>
        <span>quila.dev</span>
      </a>

      <span class="availability">
        <span class="availability-dot" aria-hidden="true"></span>
        disponível para projetos
      </span>
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

          <a class="contact-link" href="#contato">
            vamos conversar
            <span aria-hidden="true">↓</span>
          </a>
        </div>
      </section>

      <section id="contato" class="contact" aria-labelledby="contact-title">
        <div class="contact-heading" data-reveal>
          <p class="eyebrow"><span>02</span> contato</p>
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

    <footer class="site-footer" data-reveal>
      <ul class="metadata" aria-label="Informações pessoais">
        <li><span>local</span><WordHighlight target="Maceió, BRA" reveal="Cidade natal do Quila" /></li>
        <li><span>nascimento</span><time datetime="1992-08-21">21 ago 1992</time></li>
        <li><span>contato</span><a href="mailto:nissobmx@gmail.com">nissobmx@gmail.com</a></li>
      </ul>
      <p class="copyright">© {{ new Date().getFullYear() }} quila.dev</p>
    </footer>
  </div>
</template>
