<template>
  <nav class="navbar navbar-expand-lg enhanced-navbar">
    <div class="container-fluid">
      <a class="navbar-brand" href="#">
        <div class="brand-container">
          <div class="brand-icon">
            <i class="fas fa-parking"></i>
          </div>
          <span class="brand-text">ParkingApp</span>
        </div>
      </a>
      <div class="navbar-nav ms-auto">
        <button class="btn btn-logout" @click="logout">
          <i class="fas fa-sign-out-alt me-2"></i>
          Logout
        </button>
      </div>
    </div>
  </nav>
</template>
  
  <script>
  export default {
    name: "NavBar",
    emits: ["on-logout"],
    methods: {
      async logout() {
        try {
          await this.$axios.post("/auth/logout");
          this.$emit("on-logout");
        } catch (e) {
          console.error("Logout failed:", e);
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .enhanced-navbar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
    padding: 1rem 0;
    border: none;
  }

  .brand-container {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .brand-icon {
    width: 45px;
    height: 45px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.2rem;
    transition: all 0.3s ease;
  }

  .brand-icon:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: rotate(5deg) scale(1.05);
  }

  .brand-text {
    color: white;
    font-weight: 700;
    font-size: 1.5rem;
    letter-spacing: -0.5px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .navbar-brand {
    text-decoration: none;
    transition: all 0.3s ease;
  }

  .navbar-brand:hover {
    transform: translateY(-2px);
  }

  .btn-logout {
    background: rgba(255, 255, 255, 0.15);
    border: 2px solid rgba(255, 255, 255, 0.3);
    color: white;
    padding: 0.5rem 1.25rem;
    border-radius: 25px;
    font-weight: 600;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
  }

  .btn-logout:hover {
    background: rgba(255, 255, 255, 0.25);
    border-color: rgba(255, 255, 255, 0.5);
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  }

  .btn-logout:active {
    transform: translateY(0);
  }

  @media (max-width: 768px) {
    .brand-text {
      font-size: 1.25rem;
    }
    
    .brand-icon {
      width: 40px;
      height: 40px;
    }
    
    .btn-logout {
      padding: 0.4rem 1rem;
      font-size: 0.9rem;
    }
  }
  </style>