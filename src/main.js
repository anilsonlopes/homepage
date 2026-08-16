import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App)

if (import.meta.env.DEV) {
  const { createGtag } = await import('vue-gtag')

  app.use(createGtag({
    tagId: 'G-K1BE8B5GBQ'
  }))
}

app.mount('#app')
