<template>
  <div>
    <!-- Top bar only when logged in -->
    <NavBar v-if="role" @on-logout="handleLogout" />

    <!-- Not logged in: show login or register -->
    <LoginView
      v-if="!role && !registering"
      @login="onLogin"
      @go-register="registering = true"
    />
    <RegisterView
      v-else-if="!role && registering"
      @go-login="registering = false"
    />

    <!-- Logged in: show the right dashboard -->
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
      role: null,         // 'admin' or 'user' after login
      registering: false, // toggle between login & register
    };
  },
  async mounted() {
    // Check if user is already logged in on page load/refresh
    await this.checkAuthStatus();
  },
  methods: {
    async checkAuthStatus() {
      const token = localStorage.getItem('access_token');
      if (token) {
        // Set the axios default header
        this.$axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        try {
          // Verify the token is still valid by making a test request
          const response = await this.$axios.get('/auth/me');
          this.role = response.data.role;
        } catch (error) {
          // Token is invalid or expired, clear it
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
      // clear the role and bring back to login screen
      localStorage.removeItem('access_token');
      delete this.$axios.defaults.headers.common['Authorization'];
      this.role = null;
      this.registering = false;
    },
  },
};
</script>

<style>
/* global styles if you need them */
</style>