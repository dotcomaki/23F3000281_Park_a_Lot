<template>
  <div>
    <NavBar v-if="role" @on-logout="handleLogout" />

    <LoginView
      v-if="!role && !registering"
      @login="onLogin"
      @go-register="registering = true"
    />
    <RegisterView
      v-else-if="!role && registering"
      @go-login="registering = false"
    />

    <AdminDashboard v-else-if="role === 'admin'" />
    <UserDashboard  v-else />
  </div>
</template>

<script>
import LoginView      from "./components/LoginView.vue";
import RegisterView   from "./components/RegisterView.vue";
import AdminDashboard from "./components/AdminDashboard.vue";
import UserDashboard  from "./components/UserDashboard.vue";
import NavBar         from "./components/NavBar.vue";

export default {
  name: "App",
  components: {
    LoginView,
    RegisterView,
    AdminDashboard,
    UserDashboard,
    NavBar,
  },
  data() {
    return {
      role: null,
      registering: false,
    };
  },
  async mounted() {
    await this.checkAuthStatus();
  },
  methods: {
    async checkAuthStatus() {
      const token = localStorage.getItem('access_token');
      if (token) {
        this.$axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        try {
          const response = await this.$axios.get('/auth/me');
          this.role = response.data.role;
        } catch (error) {
          localStorage.removeItem('access_token');
          delete this.$axios.defaults.headers.common['Authorization'];
          this.role = null;
        }
      }
    },
    onLogin(role) {
      this.role = role;
    },
    handleLogout() {
      localStorage.removeItem('access_token');
      delete this.$axios.defaults.headers.common['Authorization'];
      this.role = null;
      this.registering = false;
    },
  },
};
</script>

<style>
/* Global styles for the entire app */
body {
  margin: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: #f8f9fa;
}

* {
  box-sizing: border-box;
}

/* Smooth transitions for all elements */
* {
  transition: box-shadow 0.3s ease, transform 0.3s ease;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

/* Enhanced focus states */
.form-control:focus,
.form-select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

/* Enhanced button styles */
.btn {
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-1px);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.btn-success {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  border: none;
}

.btn-danger {
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  border: none;
}

.btn-warning {
  background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
  border: none;
  color: #212529;
}

.btn-info {
  background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
  border: none;
}

/* Enhanced alerts */
.alert {
  border-radius: 10px;
  border: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

/* Enhanced badges */
.badge {
  font-size: 0.75rem;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
}

/* Enhanced modals */
.modal-content {
  border-radius: 15px;
  border: none;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.modal-header {
  border-bottom: 1px solid #f0f0f0;
  border-radius: 15px 15px 0 0;
}

.modal-footer {
  border-top: 1px solid #f0f0f0;
  border-radius: 0 0 15px 15px;
}

/* Animation classes */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Loading animation */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.pulse {
  animation: pulse 2s infinite;
}
</style>