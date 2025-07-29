<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <div class="register-icon">
          <i class="fas fa-user-plus fa-3x"></i>
        </div>
        <h2 class="register-title">Create Account</h2>
        <p class="register-subtitle">Join our parking community</p>
      </div>
      
      <form @submit.prevent="doRegister" novalidate class="register-form">
        <div class="form-floating mb-3">
          <input
            v-model.trim="username"
            id="username"
            class="form-control"
            :class="{ 'is-invalid': formSubmitted && username.length < 3 }"
            @blur="usernameTouched = true"
            placeholder="Username"
            minlength="3"
            required
          />
          <label for="username">
            <i class="fas fa-user me-2"></i>Username
          </label>
          <div v-if="formSubmitted && username.length < 3" class="invalid-feedback">
            <i class="fas fa-exclamation-circle me-1"></i>Username must be at least 3 characters.
          </div>
        </div>

        <div class="form-floating mb-3">
          <input
            v-model.trim="email"
            id="email"
            type="email"
            class="form-control"
            :class="{ 'is-invalid': formSubmitted && !validEmail }"
            @blur="emailTouched = true"
            placeholder="Email"
            required
          />
          <label for="email">
            <i class="fas fa-envelope me-2"></i>Email
          </label>
          <div v-if="formSubmitted && !validEmail" class="invalid-feedback">
            <i class="fas fa-exclamation-circle me-1"></i>Enter a valid email address.
          </div>
        </div>

        <div class="form-floating mb-4">
          <input
            v-model="password"
            id="password"
            type="password"
            class="form-control"
            :class="{ 'is-invalid': formSubmitted && password.length < 8 }"
            @blur="passwordTouched = true"
            placeholder="Password"
            minlength="8"
            required
          />
          <label for="password">
            <i class="fas fa-lock me-2"></i>Password
          </label>
          <div v-if="formSubmitted && password.length < 8" class="invalid-feedback">
            <i class="fas fa-exclamation-circle me-1"></i>Password must be at least 8 characters.
          </div>
        </div>

        <button
          class="btn btn-success btn-lg w-100 register-btn"
          :disabled="!isFormValid || loading"
        >
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="fas fa-user-plus me-2"></i>
          {{ loading ? 'Creating Account...' : 'Create Account' }}
        </button>
      </form>
      
      <div class="register-footer">
        <p class="login-link">
          Already have an account?
          <a href="#" @click.prevent="$emit('go-login')" class="login-btn">
            Sign In
          </a>
        </p>
      </div>
      
      <div v-if="error" class="alert alert-danger mt-3 error-alert">
        <i class="fas fa-exclamation-triangle me-2"></i>{{ error }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RegisterView',
  data() {
    return {
      username: '',
      email: '',
      password: '',
      loading: false,
      error: '',
      usernameTouched: false,
      emailTouched: false,
      passwordTouched: false,
      formSubmitted: false, // Track if form has been submitted
    }
  },
  computed: {
    validEmail() {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email)
    },
    isFormValid() {
      return (
        this.username.length >= 3 &&
        this.validEmail &&
        this.password.length >= 8
      )
    }
  },
  methods: {
    async doRegister() {
      this.formSubmitted = true
      this.error = ''
      
      // Check form validation
      if (!this.isFormValid) {
        return
      }
      
      this.loading = true
      try {
        await this.$axios.post('/auth/register', {
          username: this.username,
          email: this.email,
          password: this.password
        })
        this.$emit('go-login')
      } catch (e) {
        this.error = e.response?.data?.error || 'Registration failed'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.register-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 3rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.register-header {
  text-align: center;
  margin-bottom: 2rem;
}

.register-icon {
  display: inline-block;
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin: 0 auto 1.5rem;
  box-shadow: 0 10px 30px rgba(40, 167, 69, 0.3);
}

.register-title {
  color: #2d3748;
  font-weight: 700;
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.register-subtitle {
  color: #718096;
  font-size: 1rem;
  margin-bottom: 0;
}

.register-form {
  margin-bottom: 1.5rem;
}

.form-floating {
  position: relative;
}

.form-floating > .form-control {
  padding: 1rem 1rem 1rem 3rem;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.8);
}

.form-floating > .form-control:focus {
  border-color: #28a745;
  box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25);
  background: white;
}

.form-floating > label {
  padding: 1rem 1rem 1rem 3rem;
  color: #718096;
  font-weight: 500;
}

.form-floating > .form-control:focus ~ label,
.form-floating > .form-control:not(:placeholder-shown) ~ label {
  opacity: 0.65;
  transform: scale(0.85) translateY(-0.5rem) translateX(0.15rem);
}

.register-btn {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  border: none;
  border-radius: 12px;
  padding: 1rem;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(40, 167, 69, 0.4);
}

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(40, 167, 69, 0.6);
}

.register-btn:disabled {
  opacity: 0.6;
  transform: none;
}

.register-footer {
  text-align: center;
}

.login-link {
  color: #718096;
  margin-bottom: 0;
}

.login-btn {
  color: #28a745;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s ease;
}

.login-btn:hover {
  color: #20c997;
  text-decoration: underline;
}

.error-alert {
  border-radius: 12px;
  border: none;
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
  border-left: 4px solid #dc3545;
}

.is-invalid {
  border-color: #dc3545 !important;
}

.invalid-feedback {
  display: block;
  font-size: 0.875rem;
  color: #dc3545;
  margin-top: 0.25rem;
}

@media (max-width: 768px) {
  .register-container {
    padding: 1rem;
  }
  
  .register-card {
    padding: 2rem;
  }
  
  .register-title {
    font-size: 1.75rem;
  }
  
  .register-icon {
    width: 70px;
    height: 70px;
  }
}
</style>