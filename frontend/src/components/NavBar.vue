<template>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">ParkingApp</a>
        <div class="d-flex">
          <button class="btn btn-outline-danger" @click="logout">
            Logout
          </button>
        </div>
      </div>
    </nav>
  </template>
  
  <script>
  import axios from "axios";
  
  export default {
    name: "NavBar",
    emits: ["on-logout"],
    methods: {
      async logout() {
        try {
          await axios.post("/auth/logout");
          this.$emit("on-logout");
        } catch (e) {
          console.error("Logout failed:", e);
        }
      },
    },
  };
  </script>
  
  <style scoped>
  /* You can adjust spacing or colors here if you like */
  </style>