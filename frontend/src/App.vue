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
</style>