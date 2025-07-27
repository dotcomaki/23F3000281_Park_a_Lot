<template>
  <div class="container mt-5" style="max-width: 400px">
    <h3 class="mb-4">Register</h3>
    <form @submit.prevent="doRegister" novalidate>
      <div class="mb-3">
        <label class="form-label">Username</label>
        <input
          v-model.trim="username"
          class="form-control"
          :class="{ 'is-invalid': usernameTouched && username.length < 3 }"
          @blur="usernameTouched = true"
          minlength="3"
          required
        />
        <div class="invalid-feedback">
          Username must be at least 3 characters.
        </div>
      </div>

      <div class="mb-3">
        <label class="form-label">Email</label>
        <input
          v-model.trim="email"
          type="email"
          class="form-control"
          :class="{ 'is-invalid': emailTouched && !validEmail }"
          @blur="emailTouched = true"
          required
        />
        <div class="invalid-feedback">Enter a valid email.</div>
      </div>

      <div class="mb-3">
        <label class="form-label">Password</label>
        <input
          v-model="password"
          type="password"
          class="form-control"
          :class="{ 'is-invalid': passwordTouched && password.length < 8 }"
          @blur="passwordTouched = true"
          minlength="8"
          required
        />
        <div class="invalid-feedback">
          Password must be at least 5 characters.
        </div>
      </div>

      <button
        class="btn btn-success w-100"
        :disabled="!isFormValid || loading"
      >
        {{ loading ? 'Registering…' : 'Register' }}
      </button>

      <p class="mt-2 text-center">
        <a href="#" @click.prevent="$emit('go-login')">
          Already have an account? Login
        </a>
      </p>
    </form>
    <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
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
        this.password.length >= 5
      )
    }
  },
  methods: {
    async doRegister() {
      this.error = ''
      this.loading = true
      try {
        await this.$axios.post('/auth/register', {
          username: this.username,
          email: this.email,
          password: this.password
        })
        alert('Registration successful! Please log in.')
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
</style>