<template>
  <div class="container mt-5">
    <!-- Navbar -->
    <ul class="nav nav-tabs mb-4">
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: activeTab === 'home' }"
          href="#"
          @click.prevent="selectTab('home')"
        >Home</a>
      </li>
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: activeTab === 'users' }"
          href="#"
          @click.prevent="selectTab('users')"
        >Users</a>
      </li>
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: activeTab === 'search' }"
          href="#"
          @click.prevent="selectTab('search')"
        >Search</a>
      </li>
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: activeTab === 'summary' }"
          href="#"
          @click.prevent="selectTab('summary')"
        >Summary</a>
      </li>
      <li class="nav-item ms-auto">
        <button
          class="btn btn-link nav-link"
          @click.prevent="selectTab('profile')"
        >Edit Profile</button>
      </li>
    </ul>

    <!-- Users View -->
    <div v-if="activeTab === 'users'">
      <h3>Registered Users</h3>
      <div v-if="loadingUsers" class="text-center my-3">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-if="errorUsers" class="alert alert-danger">{{ errorUsers }}</div>
      <table v-if="users.length" class="table table-striped">
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Role</th>
            <th>Registered At</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.username }}</td>
            <td>{{ u.email }}</td>
            <td>{{ u.role }}</td>
            <td>{{ u.registered_at }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else-if="!loadingUsers" class="mt-4">No users found.</p>
    </div>

    <!-- Search View -->
    <div v-else-if="activeTab === 'search'">
      <h3>Search</h3>
      <div class="row g-2 align-items-center mb-3">
        <!-- Dropdown for "Search by" -->
        <div class="col-md-3">
          <label class="form-label">Search by</label>
          <select
            v-model="searchBy"
            class="form-select"
          >
            <option value="user_id">User ID</option>
            <option value="lot_name">Parking Lot Name</option>
            <option value="spot_location">Spot Location (Address/Pin)</option>
            <option value="reservation_id">Reservation ID</option>
            <!-- Add more options as needed -->
          </select>
        </div>
        <!-- Text input for search string -->
        <div class="col-md-5">
          <label class="form-label">Search term</label>
          <input
            v-model.trim="searchValue"
            class="form-control"
            placeholder="Enter search term"
          />
        </div>
        <!-- Button to trigger search -->
        <div class="col-md-2">
          <label class="form-label">&nbsp;</label>
          <button
            class="btn btn-primary w-100"
            :disabled="!searchValue.trim() || loadingSearch"
            @click="performSearch"
          >
            {{ loadingSearch ? 'Searching…' : 'Search' }}
          </button>
        </div>
      </div>

      <!-- Display search results -->
      <div v-if="searchError" class="alert alert-danger">{{ searchError }}</div>

      <div v-if="loadingSearch" class="text-center my-3">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <table v-if="searchResults.length && !loadingSearch" class="table table-bordered">
        <thead>
          <tr>
            <th v-for="header in searchHeaders" :key="header">{{ header }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in searchResults" :key="index">
            <td v-for="header in searchHeaders" :key="header">
              {{ row[header] }}
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else-if="!loadingSearch && !searchError" class="mt-4">No results found.</p>
    </div>

    <!-- Edit Profile Form -->
    <div v-else-if="activeTab === 'profile'" class="card p-4 mb-4">
      <h5>Edit Profile</h5>
      <form @submit.prevent="submitProfile" novalidate>
        <div class="mb-3">
          <label class="form-label">Username</label>
          <input
            v-model.trim="profile.username"
            @blur="profileTouched.username = true"
            :class="{ 'form-control': true, 'is-invalid': profileTouched.username && profile.username.length < 3 }"
            placeholder="Username"
            required
          />
          <div class="invalid-feedback">
            Username is required and must be at least 3 characters.
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label">Email</label>
          <input
            v-model.trim="profile.email"
            @blur="profileTouched.email = true"
            type="email"
            :class="{ 'form-control': true, 'is-invalid': profileTouched.email && !validEmail }"
            placeholder="Email"
            required
          />
          <div class="invalid-feedback">Enter a valid email address.</div>
        </div>

        <div class="mb-3">
          <label class="form-label">New Password</label>
          <input
            v-model="profile.password"
            @blur="profileTouched.password = true"
            type="password"
            :class="{ 'form-control': true, 'is-invalid': profileTouched.password && profile.password.length > 0 && profile.password.length < 8 }"
            placeholder="Leave blank to keep current password"
            minlength="8"
          />
          <div class="invalid-feedback">
            Password must be at least 8 characters if you choose to change it.
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label">Confirm New Password</label>
          <input
            v-model="profile.confirmPassword"
            @blur="profileTouched.confirmPassword = true"
            type="password"
            :class="{ 'form-control': true, 'is-invalid': profileTouched.confirmPassword && profile.password !== profile.confirmPassword }"
            placeholder="Confirm new password"
            :disabled="profile.password === ''"
            minlength="8"
          />
          <div class="invalid-feedback">
            Passwords must match.
          </div>
        </div>

        <button
          class="btn btn-primary"
          :disabled="!isProfileFormValid || loadingProfile"
        >
          {{ loadingProfile ? 'Saving…' : 'Save Profile' }}
        </button>
        <button
          type="button"
          class="btn btn-link ms-2"
          @click="cancelProfile"
        >
          Cancel
        </button>

        <div v-if="profileError" class="alert alert-danger mt-3">
          {{ profileError }}
        </div>
        <div v-if="profileSuccess" class="alert alert-success mt-3">
          {{ profileSuccess }}
        </div>
      </form>
    </div>

    <!-- Main Dashboard: Create/Lots Management (Home Tab) -->
    <div v-else>
      <h2>Admin Dashboard</h2>

      <!-- Create Lot Form -->
      <div class="card mb-4 p-3">
        <h5>Create New Lot</h5>
        <form @submit.prevent="createLot" novalidate>
          <div class="row g-2">
            <div class="col-md-4">
              <input
                v-model.trim="newLot.name"
                @blur="newLotTouched.name = true"
                :class="{ 'form-control': true, 'is-invalid': newLotTouched.name && !newLot.name }"
                placeholder="Name"
                required
              />
              <div class="invalid-feedback">Name is required.</div>
            </div>
            <div class="col-md-2">
              <input
                v-model.number="newLot.price_per_hour"
                @blur="newLotTouched.price = true"
                type="number"
                step="0.01"
                :class="{ 'form-control': true, 'is-invalid': newLotTouched.price && newLot.price_per_hour <= 0 }"
                placeholder="Price/hr"
                min="0.01"
                required
              />
              <div class="invalid-feedback">Price must be greater than 0.</div>
            </div>
            <div class="col-md-2">
              <input
                v-model.number="newLot.total_spots"
                @blur="newLotTouched.spots = true"
                type="number"
                :class="{ 'form-control': true, 'is-invalid': newLotTouched.spots && newLot.total_spots < 1 }"
                placeholder="Spots"
                min="1"
                required
              />
              <div class="invalid-feedback">At least one spot is required.</div>
            </div>
            <div class="col-md-2">
              <input
                v-model.trim="newLot.address"
                class="form-control"
                placeholder="Address"
              />
            </div>
            <div class="col-md-2">
              <input
                v-model.trim="newLot.pincode"
                class="form-control"
                placeholder="Pin code"
              />
            </div>
          </div>
          <button class="btn btn-success btn-sm mt-2" :disabled="!isCreateFormValid">
            Create Lot
          </button>
          <div v-if="formError" class="text-danger mt-1">{{ formError }}</div>
        </form>
      </div>

      <!-- Edit Lot Form -->
      <div v-if="editing" class="card mb-4 p-3">
        <h5>Edit Lot #{{ editing.id }}</h5>
        <form @submit.prevent="submitEdit" novalidate>
          <div class="row g-2">
            <div class="col-md-4">
              <input
                v-model.trim="editing.name"
                @blur="editingTouched.name = true"
                :class="{ 'form-control': true, 'is-invalid': editingTouched.name && !editing.name }"
                placeholder="Name"
                required
              />
              <div class="invalid-feedback">Name is required.</div>
            </div>
            <div class="col-md-2">
              <input
                v-model.number="editing.price_per_hour"
                @blur="editingTouched.price = true"
                type="number"
                step="0.01"
                :class="{ 'form-control': true, 'is-invalid': editingTouched.price && editing.price_per_hour <= 0 }"
                placeholder="Price/hr"
                min="0.01"
                required
              />
              <div class="invalid-feedback">Price must be greater than 0.</div>
            </div>
            <div class="col-md-2">
              <input
                v-model.number="editing.total_spots"
                @blur="editingTouched.spots = true"
                type="number"
                :class="{ 'form-control': true, 'is-invalid': editingTouched.spots && editing.total_spots < 1 }"
                placeholder="Spots"
                min="1"
                required
              />
              <div class="invalid-feedback">At least one spot is required.</div>
            </div>
            <div class="col-md-2">
              <input
                v-model.trim="editing.address"
                class="form-control"
                placeholder="Address"
              />
            </div>
            <div class="col-md-2">
              <input
                v-model.trim="editing.pincode"
                class="form-control"
                placeholder="Pin code"
              />
            </div>
          </div>
          <button class="btn btn-primary btn-sm mt-2" :disabled="!isEditFormValid">
            Save Changes
          </button>
          <button
            type="button"
            class="btn btn-link btn-sm mt-2"
            @click="cancelEdit"
          >
            Cancel
          </button>
        </form>
      </div>

      <!-- List of Lots -->
      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-if="loading" class="text-center my-4">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <table v-if="lots.length" class="table table-striped">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Price/hr</th>
            <th>Total Spots</th>
            <th>Available</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lot in lots" :key="lot.id">
            <td>{{ lot.id }}</td>
            <td>{{ lot.name }}</td>
            <td>{{ lot.price_per_hour }}</td>
            <td>{{ lot.total_spots }}</td>
            <td>{{ lot.available_spots }}</td>
            <td>
              <button
                class="btn btn-sm btn-danger me-1"
                @click="deleteLot(lot.id)"
              >Delete</button>
              <button
                class="btn btn-sm btn-secondary"
                @click="startEdit(lot)"
              >Edit</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else-if="!loading" class="mt-4">
        <p>No parking lots found.</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AdminDashboard',
  data() {
    return {
      // Current tab: 'home', 'users', 'search', 'summary', 'profile'
      activeTab: 'home',

      // For users view
      users: [],
      loadingUsers: false,
      errorUsers: '',

      // For search view
      searchBy: 'user_id',
      searchValue: '',
      searchResults: [],
      loadingSearch: false,
      searchError: '',

      // For lots management
      lots: [],
      loading: false,
      error: '',
      newLot: {
        name: '',
        price_per_hour: null,
        total_spots: null,
        address: '',
        pincode: ''
      },
      formError: '',
      editing: null,
      newLotTouched: { name: false, price: false, spots: false },
      editingTouched: { name: false, price: false, spots: false },

      // For profile editing
      profile: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      profileTouched: {
        username: false,
        email: false,
        password: false,
        confirmPassword: false
      },
      loadingProfile: false,
      profileError: '',
      profileSuccess: ''
    }
  },
  computed: {
    // Validation for create lot
    isCreateFormValid() {
      return (
        this.newLot.name.trim() !== '' &&
        this.newLot.price_per_hour > 0 &&
        this.newLot.total_spots >= 1
      )
    },
    // Validation for edit lot
    isEditFormValid() {
      return (
        this.editing &&
        this.editing.name.trim() !== '' &&
        this.editing.price_per_hour > 0 &&
        this.editing.total_spots >= 1
      )
    },
    // Validation for profile form
    validEmail() {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.profile.email)
    },
    isProfileFormValid() {
      const usernameValid = this.profile.username.trim().length >= 3
      const emailValid = this.validEmail
      let passwordValid = true
      let confirmValid = true

      if (this.profile.password) {
        passwordValid = this.profile.password.length >= 8
        confirmValid = this.profile.password === this.profile.confirmPassword
      }
      return usernameValid && emailValid && passwordValid && confirmValid
    },
    // Compute headers for searchResults table
    searchHeaders() {
      if (!this.searchResults.length) return []
      return Object.keys(this.searchResults[0])
    }
  },
  async mounted() {
    await this.fetchLots()
  },
  methods: {
    // Tab selection handler
    selectTab(tab) {
      this.activeTab = tab
      if (tab === 'users') {
        this.fetchUsers()
      } else if (tab === 'home') {
        this.fetchLots()
      } else if (tab === 'search') {
        this.searchResults = []
        this.searchError = ''
        this.searchValue = ''
      }
    },

    // Fetch all users for Users view
    async fetchUsers() {
      this.loadingUsers = true
      this.errorUsers = ''
      try {
        const resp = await axios.get('/admin/users')
        this.users = resp.data
      } catch (e) {
        this.errorUsers = e.response?.data?.error || 'Failed to load users'
      } finally {
        this.loadingUsers = false
      }
    },

    // Perform search based on selected criteria
    async performSearch() {
      if (!this.searchValue.trim()) return
      this.loadingSearch = true
      this.searchError = ''
      this.searchResults = []
      try {
        // Example endpoint: /admin/search?by=user_id&q=123
        const resp = await axios.get('/admin/search', {
          params: {
            by: this.searchBy,
            q: this.searchValue.trim()
          }
        })
        this.searchResults = resp.data
      } catch (e) {
        this.searchError = e.response?.data?.error || 'Search failed'
      } finally {
        this.loadingSearch = false
      }
    },

    // Open and preload profile form
    async openEditProfile() {
      this.activeTab = 'profile'
      this.profileError = ''
      this.profileSuccess = ''
      this.loadingProfile = true
      try {
        const resp = await axios.get('/auth/me')
        const user = resp.data
        this.profile.username = user.username
        this.profile.email = user.email
        this.profile.password = ''
        this.profile.confirmPassword = ''
        this.profileTouched = { username: false, email: false, password: false, confirmPassword: false }
      } catch (e) {
        this.profileError = 'Failed to fetch profile'
      } finally {
        this.loadingProfile = false
      }
    },
    cancelProfile() {
      this.activeTab = 'home'
      this.profileError = ''
      this.profileSuccess = ''
    },
    async submitProfile() {
      this.profileTouched = {
        username: true,
        email: true,
        password: true,
        confirmPassword: true
      }
      if (!this.isProfileFormValid) return

      this.profileError = ''
      this.profileSuccess = ''
      this.loadingProfile = true

      try {
        const payload = {
          username: this.profile.username,
          email: this.profile.email
        }
        if (this.profile.password) {
          payload.password = this.profile.password
        }
        await axios.put('/auth/profile', payload)
        this.profileSuccess = 'Profile updated successfully.'
      } catch (e) {
        this.profileError = e.response?.data?.error || 'Failed to update profile'
      } finally {
        this.loadingProfile = false
      }
    },

    // Fetch lots for Home view
    async fetchLots() {
      this.loading = true
      this.error = ''
      try {
        const resp = await axios.get('/admin/lots')
        this.lots = resp.data
      } catch (e) {
        this.error = e.response?.data?.error || 'Failed to load lots'
      } finally {
        this.loading = false
      }
    },

    // Lot creation
    async createLot() {
      this.formError = ''
      this.newLotTouched = { name: true, price: true, spots: true }
      if (!this.isCreateFormValid) return

      try {
        const payload = {
          name: this.newLot.name,
          price_per_hour: this.newLot.price_per_hour,
          total_spots: this.newLot.total_spots,
          address: this.newLot.address || undefined,
          pincode: this.newLot.pincode || undefined
        }
        const resp = await axios.post('/admin/lots', payload)
        this.lots.push({
          id: resp.data.lot_id,
          name: this.newLot.name,
          price_per_hour: this.newLot.price_per_hour,
          total_spots: this.newLot.total_spots,
          available_spots: this.newLot.total_spots,
          address: this.newLot.address || null,
          pincode: this.newLot.pincode || null
        })
        this.newLot = {
          name: '',
          price_per_hour: null,
          total_spots: null,
          address: '',
          pincode: ''
        }
        this.newLotTouched = { name: false, price: false, spots: false }
      } catch (e) {
        this.formError = e.response?.data?.error || 'Failed to create lot'
      }
    },

    // Start editing a lot
    startEdit(lot) {
      this.editing = { ...lot }
      this.editingTouched = { name: false, price: false, spots: false }
    },
    cancelEdit() {
      this.editing = null
    },
    async submitEdit() {
      this.editingTouched = { name: true, price: true, spots: true }
      if (!this.isEditFormValid) return

      const { id, name, price_per_hour, total_spots, address, pincode } = this.editing
      try {
        await axios.put(`/admin/lots/${id}`, {
          name,
          price_per_hour,
          total_spots,
          address,
          pincode
        })
        const idx = this.lots.findIndex(l => l.id === id)
        this.lots.splice(idx, 1, { ...this.editing })
        this.editing = null
      } catch (e) {
        alert(e.response?.data?.error || 'Update failed')
      }
    },

    // Delete a lot
    async deleteLot(lotId) {
      if (!confirm('Really delete this parking lot?')) return
      try {
        await axios.delete(`/admin/lots/${lotId}`)
        this.lots = this.lots.filter(l => l.id !== lotId)
      } catch (e) {
        alert(e.response?.data?.error || 'Delete failed')
      }
    }
  }
}
</script>

<style scoped>
/* component-specific styles, if needed */
</style>