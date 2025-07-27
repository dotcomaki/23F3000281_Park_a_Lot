<template>
  <div class="container mt-5" style="max-width: 400px">
    <h3 class="mb-4">Login</h3>
    <form @submit.prevent="doLogin" novalidate>
      <div class="mb-3">
        <label class="form-label">Username</label>
        <input
          v-model.trim="username"
          class="form-control"
          :class="{ 'is-invalid': usernameTouched && !username }"
          @blur="usernameTouched = true"
          required
        />
        <div class="invalid-feedback">Username is required.</div>
      </div>
      <div class="mb-3">
        <label class="form-label">Password</label>
        <input
          v-model="password"
          type="password"
          class="form-control"
          :class="{ 'is-invalid': passwordTouched && !password }"
          @blur="passwordTouched = true"
          required
        />
        <div class="invalid-feedback">Password is required.</div>
      </div>
      <button
        class="btn btn-primary w-100"
        :disabled="!isFormValid || loading"
        type="submit"
      >
        {{ loading ? 'Logging in…' : 'Login' }}
      </button>
    </form>
    <p class="mt-2 text-center">
      <a href="#" @click.prevent="$emit('go-register')">
        Don’t have an account? Register
      </a>
    </p>
    <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
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
    }
  },
  computed: {
    isFormValid() {
      return this.username.trim() !== '' && this.password !== ''
    }
  },
  methods: {
    async doLogin() {
      this.error = ''
      this.loading = true
      try {
        const { data } = await this.$axios.post('/auth/login', {
          username: this.username,
          password: this.password
        })
        // Store JWT and set default auth header
        const token = data.access_token
        localStorage.setItem('access_token', token)
        this.$axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        // emit the role back to App.vue
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