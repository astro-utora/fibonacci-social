import { createApp } from 'vue'
import App from './App.vue'
import axios from 'axios'
import { checkAuthFx } from '@/stores/auth'
import router from './router'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi
    }
  }
})

// Configure axios
axios.defaults.baseURL = import.meta.env.VITE_API_URL

const app = createApp(App)

// Initialize auth state before mounting
checkAuthFx().then(() => {
  app
    .use(vuetify)
    .use(router)
    .mount('#app')
}) 