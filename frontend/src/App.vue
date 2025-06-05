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
  methods: {
    onLogin(role) {
      this.role = role;
    },
    handleLogout() {
      // clear the role and bring back to login screen
      this.role = null;
      this.registering = false;
    },
  },
};
</script>

<style>
/* global styles if you need them */
</style>