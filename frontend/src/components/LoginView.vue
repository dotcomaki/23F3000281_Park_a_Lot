<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="login-icon">
          <i class="fas fa-parking fa-3x"></i>
        </div>
        <h2 class="login-title">Welcome Back</h2>
        <p class="login-subtitle">Sign in to your parking account</p>
      </div>
      
      <form @submit.prevent="doLogin" novalidate class="login-form">
        <div class="form-floating mb-3">
          <input
            v-model.trim="username"
            id="username"
            class="form-control"
            :class="{ 'is-invalid': formSubmitted && !username }"
            @blur="usernameTouched = true"
            placeholder="Username"
            required
          />
          <label for="username">
            <i class="fas fa-user me-2"></i>Username
          </label>
          <div v-if="formSubmitted && !username" class="invalid-feedback">
            <i class="fas fa-exclamation-circle me-1"></i>Username is required.
          </div>
        </div>
        
        <div class="form-floating mb-4">
          <input
            v-model="password"
            id="password"
            type="password"
            class="form-control"
            :class="{ 'is-invalid': formSubmitted && !password }"
            @blur="passwordTouched = true"
            placeholder="Password"
            required
          />
          <label for="password">
            <i class="fas fa-lock me-2"></i>Password
          </label>
          <div v-if="formSubmitted && !password" class="invalid-feedback">
            <i class="fas fa-exclamation-circle me-1"></i>Password is required.
          </div>
        </div>
        
        <button
          class="btn btn-primary btn-lg w-100 login-btn"
          :disabled="!isFormValid || loading"
          type="submit"
        >
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="fas fa-sign-in-alt me-2"></i>
          {{ loading ? 'Signing In...' : 'Sign In' }}
        </button>
      </form>
      
      <div class="login-footer">
        <p class="register-link">
          Don't have an account?
          <a href="#" @click.prevent="$emit('go-register')" class="register-btn">
            Create Account
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
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
      loading: false,
      error: '',
      usernameTouched: false,
      passwordTouched: false,
      formSubmitted: false, // Track if form has been submitted
    }
  },
  computed: {
    isFormValid() {
      return this.username.trim() !== '' && this.password !== ''
    }
  },
  methods: {
    async doLogin() {
      this.formSubmitted = true
      this.error = ''
      
      // Check form validation
      if (!this.isFormValid) {
        return
      }
      
      this.loading = true
      try {
        const { data } = await this.$axios.post('/auth/login', {
          username: this.username,
          password: this.password
        })
        const token = data.access_token
        localStorage.setItem('access_token', token)
        this.$axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        this.$emit('login', data.role, token)
      } catch (e) {
        this.error = e.response?.data?.error || 'Login failed'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 3rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-icon {
  display: inline-block;
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin: 0 auto 1.5rem;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.login-title {
  color: #2d3748;
  font-weight: 700;
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.login-subtitle {
  color: #718096;
  font-size: 1rem;
  margin-bottom: 0;
}

.login-form {
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
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
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

.login-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  padding: 1rem;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
}

.login-btn:disabled {
  opacity: 0.6;
  transform: none;
}

.login-footer {
  text-align: center;
}

.register-link {
  color: #718096;
  margin-bottom: 0;
}

.register-btn {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s ease;
}

.register-btn:hover {
  color: #764ba2;
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
  .login-container {
    padding: 1rem;
  }
  
  .login-card {
    padding: 2rem;
  }
  
  .login-title {
    font-size: 1.75rem;
  }
  
  .login-icon {
    width: 70px;
    height: 70px;
  }
}
</style>