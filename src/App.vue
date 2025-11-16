<script setup>
import WordHighlight from './components/WordHighlight.vue';

</script>

<template>
  <nav class="bg-neutral-900 text-neutral-400 text-center p-5">
    <a class="hover:text-white" href="/">quila.dev</a>
  </nav>
  <main class="container mx-auto py-20 text-center selection:bg-red-600 selection:text-white">
    <h1 class="text-4xl font-serif leading-snug max-w-xl mx-auto">
      Experimentos de um desenvolvedor frontend web
      <WordHighlight target="psuedo-autodidata"
        reveal="O sujeito não tem diploma e não consegue reconhecer que aprender tudo sozinho, já que toda informação obtida partiu de alguém antes." />
    </h1>
    <p class="max-w-3xl mx-auto mt-10 leading-loose">
      Oi, eu sou o
      <WordHighlight target="Quila" reveal="Vulgo para Anilson Lopes dos Santos" /> Mexo com os códigos há 16 anos, 9
      deles focado no
      desenvolvimento front-end para <word-highlight target="web" reveal="Você está aqui!" />. Acredito que o
      desenvolvimento
      <word-highlight target="performático" reveal="Veja bem! É o desenvolvimento que deve ser performático!" />,
      acessível e escalável pode ser alcançado se fizer o que
      eu digo. <word-highlight reveal="Fiz piadinha mas a conversa é séria!">
        <em>Hehe</em>
      </word-highlight>.
    </p>

    <ul class="font-mono flex space-x-5 items-center justify-center text-xs mx-auto mt-10">
      <span><word-highlight target="Maceió" reveal="Cidade natal do quila"></word-highlight>, BRA</span>
      <span>꠵</span>
      <span>Agosto 21, 1992</span>
      <span>꠵</span>
      <span>nissobmx@gmail.com</span>
    </ul>
  </main>
</template>

<style scoped></style>
