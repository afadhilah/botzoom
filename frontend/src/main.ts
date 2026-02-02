import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import { router } from "./router"
import { setupAuthInterceptor } from './services/auth.interceptor'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Setup auth interceptor
setupAuthInterceptor()

app.mount('#app')
