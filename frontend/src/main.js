import { createApp } from 'vue'
import App from './App.vue'

// Bootstrap CSS and JS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// FontAwesome Icons
import '@fortawesome/fontawesome-free/css/all.min.css'

import axios from 'axios'

axios.defaults.withCredentials = true
axios.defaults.baseURL = 'http://localhost:5001'

const token = localStorage.getItem('access_token')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

const app = createApp(App)
app.config.globalProperties.$axios = axios
app.mount('#app')