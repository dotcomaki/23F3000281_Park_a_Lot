<template>
  <div class="container-fluid mt-4">
    <!-- Enhanced Header with Gradient -->
    <div class="admin-header mb-4">
      <div class="row align-items-center">
        <div class="col">
          <h1 class="display-5 fw-bold text-white mb-0">
            <i class="fas fa-tachometer-alt me-3"></i>
            Admin Dashboard
          </h1>
          <p class="text-white-50 mb-0">Manage your parking system</p>
        </div>
        <div class="col-auto">
          <div class="badge bg-light text-dark fs-6 px-3 py-2">
            <i class="fas fa-user-shield me-2"></i>
            Administrator
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced Navigation Tabs -->
    <div class="nav-container mb-4">
      <ul class="nav nav-pills nav-fill">
        <li class="nav-item">
          <a
            class="nav-link"
            :class="{ active: activeTab === 'home' }"
            href="#"
            @click.prevent="selectTab('home')"
          >
            <i class="fas fa-home me-2"></i>Home
          </a>
        </li>
        <li class="nav-item">
          <a
            class="nav-link"
            :class="{ active: activeTab === 'users' }"
            href="#"
            @click.prevent="selectTab('users')"
          >
            <i class="fas fa-users me-2"></i>Users
          </a>
        </li>
        <li class="nav-item">
          <a
            class="nav-link"
            :class="{ active: activeTab === 'search' }"
            href="#"
            @click.prevent="selectTab('search')"
          >
            <i class="fas fa-search me-2"></i>Search
          </a>
        </li>
        <li class="nav-item">
          <a
            class="nav-link"
            :class="{ active: activeTab === 'summary' }"
            href="#"
            @click.prevent="selectTab('summary')"
          >
            <i class="fas fa-chart-bar me-2"></i>Summary
          </a>
        </li>
        <li class="nav-item">
          <button
            class="nav-link btn btn-link"
            :class="{ active: activeTab === 'profile' }"
            @click.prevent="selectTab('profile')"
          >
            <i class="fas fa-user-cog me-2"></i>Edit Profile
          </button>
        </li>
      </ul>
    </div>

    <!-- Users View -->
    <div v-if="activeTab === 'users'" class="fade-in">
      <div class="enhanced-card">
        <div class="card-header">
          <h4 class="mb-0">
            <i class="fas fa-users me-2 text-primary"></i>
            Registered Users
          </h4>
        </div>
        <div class="card-body">
          <div v-if="loadingUsers" class="loading-container">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Loading users...</p>
          </div>
          <div v-if="errorUsers" class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>{{ errorUsers }}
          </div>
          <div v-if="users.length && !loadingUsers" class="table-responsive">
            <table class="table table-hover">
              <thead class="table-dark">
                <tr>
                  <th><i class="fas fa-id-badge me-1"></i>ID</th>
                  <th><i class="fas fa-user me-1"></i>Username</th>
                  <th><i class="fas fa-envelope me-1"></i>Email</th>
                  <th><i class="fas fa-user-tag me-1"></i>Role</th>
                  <th><i class="fas fa-calendar me-1"></i>Registered</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in users" :key="u.id" class="table-row-hover">
                  <td><span class="badge bg-secondary">{{ u.id }}</span></td>
                  <td><strong>{{ u.username }}</strong></td>
                  <td>{{ u.email }}</td>
                  <td>
                    <span 
                      class="badge" 
                      :class="u.role === 'admin' ? 'bg-danger' : 'bg-success'"
                    >
                      {{ u.role }}
                    </span>
                  </td>
                  <td>{{ formatDateTime(u.registered_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else-if="!loadingUsers" class="empty-state">
            <i class="fas fa-users fa-3x text-muted mb-3"></i>
            <p class="text-muted">No users found.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Search View -->
    <div v-else-if="activeTab === 'search'" class="fade-in">
      <div class="enhanced-card">
        <div class="card-header">
          <h4 class="mb-0">
            <i class="fas fa-search me-2 text-primary"></i>
            Advanced Search
          </h4>
        </div>
        <div class="card-body">
          <div class="search-form mb-4">
            <div class="row g-3">
              <div class="col-md-3">
                <label class="form-label fw-semibold">
                  <i class="fas fa-filter me-1"></i>Search by
                </label>
                <select v-model="searchBy" class="form-select">
                  <option value="user_id">User ID</option>
                  <option value="lot_name">Parking Lot Name</option>
                  <option value="spot_location">Spot Location</option>
                  <option value="reservation_id">Reservation ID</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">
                  <i class="fas fa-keyboard me-1"></i>Search term
                </label>
                <input
                  v-model.trim="searchValue"
                  class="form-control"
                  placeholder="Enter search term..."
                />
              </div>
              <div class="col-md-3">
                <label class="form-label">&nbsp;</label>
                <button
                  class="btn btn-primary w-100"
                  :disabled="!searchValue.trim() || loadingSearch"
                  @click="performSearch"
                >
                  <span v-if="loadingSearch" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="fas fa-search me-2"></i>
                  {{ loadingSearch ? 'Searching...' : 'Search' }}
                </button>
              </div>
            </div>
          </div>

          <div v-if="searchError" class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>{{ searchError }}
          </div>

          <div v-if="loadingSearch" class="loading-container">
            <div class="spinner-border text-primary"></div>
            <p class="mt-2 text-muted">Searching...</p>
          </div>

          <div v-if="searchResults.length && !loadingSearch" class="table-responsive">
            <table class="table table-hover">
              <thead class="table-dark">
                <tr>
                  <th v-for="header in searchHeaders" :key="header">{{ header }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in searchResults" :key="index">
                  <td v-for="header in searchHeaders" :key="header">
                    <span v-if="header.includes('_at') || header.includes('date') || header === 'timestamp'">
                      {{ formatDateTime(row[header]) }}
                    </span>
                    <span v-else>{{ row[header] }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else-if="!loadingSearch && !searchError && searchValue" class="empty-state">
            <i class="fas fa-search fa-3x text-muted mb-3"></i>
            <p class="text-muted">No results found for "{{ searchValue }}"</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Profile Form -->
    <div v-else-if="activeTab === 'profile'" class="fade-in">
      <div class="enhanced-card">
        <div class="card-header">
          <h4 class="mb-0">
            <i class="fas fa-user-cog me-2 text-primary"></i>
            Edit Profile
          </h4>
        </div>
        <div class="card-body">
          <form @submit.prevent="submitProfile" novalidate>
            <div class="row">
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label fw-semibold">
                    <i class="fas fa-user me-1"></i>Username
                  </label>
                  <input
                    v-model.trim="profile.username"
                    @blur="profileTouched.username = true"
                    :class="{ 'form-control': true, 'is-invalid': profileTouched.username && profile.username.length < 3 }"
                    placeholder="Username"
                    required
                  />
                  <div class="invalid-feedback">Username must be at least 3 characters.</div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label fw-semibold">
                    <i class="fas fa-envelope me-1"></i>Email
                  </label>
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
              </div>
            </div>

            <div class="row">
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label fw-semibold">
                    <i class="fas fa-lock me-1"></i>New Password
                  </label>
                  <input
                    v-model="profile.password"
                    @blur="profileTouched.password = true"
                    type="password"
                    :class="{ 'form-control': true, 'is-invalid': profileTouched.password && profile.password.length > 0 && profile.password.length < 8 }"
                    placeholder="Leave blank to keep current"
                    minlength="8"
                  />
                  <div class="invalid-feedback">Password must be at least 8 characters.</div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label fw-semibold">
                    <i class="fas fa-lock me-1"></i>Confirm Password
                  </label>
                  <input
                    v-model="profile.confirmPassword"
                    @blur="profileTouched.confirmPassword = true"
                    type="password"
                    :class="{ 'form-control': true, 'is-invalid': profileTouched.confirmPassword && profile.password !== profile.confirmPassword }"
                    placeholder="Confirm new password"
                    :disabled="profile.password === ''"
                    minlength="8"
                  />
                  <div class="invalid-feedback">Passwords must match.</div>
                </div>
              </div>
            </div>

            <div class="d-flex gap-2">
              <button
                class="btn btn-primary"
                :disabled="!isProfileFormValid || loadingProfile"
              >
                <span v-if="loadingProfile" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="fas fa-save me-2"></i>
                {{ loadingProfile ? 'Saving...' : 'Save Profile' }}
              </button>
              <button
                type="button"
                class="btn btn-outline-secondary"
                @click="cancelProfile"
              >
                <i class="fas fa-times me-2"></i>Cancel
              </button>
            </div>

            <div v-if="profileError" class="alert alert-danger mt-3">
              <i class="fas fa-exclamation-triangle me-2"></i>{{ profileError }}
            </div>
            <div v-if="profileSuccess" class="alert alert-success mt-3">
              <i class="fas fa-check-circle me-2"></i>{{ profileSuccess }}
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Summary View -->
    <div v-else-if="activeTab === 'summary'" class="fade-in">
      <div class="enhanced-card">
        <div class="card-header">
          <h4 class="mb-0">
            <i class="fas fa-chart-bar me-2 text-primary"></i>
            Analytics Summary
          </h4>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-lg-6 mb-4">
              <div class="chart-container">
                <canvas id="revenueChart"></canvas>
              </div>
            </div>
            <div class="col-lg-6 mb-4">
              <div class="chart-container">
                <canvas id="occupancyChart"></canvas>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Dashboard: Create/Lots Management (Home Tab) -->
    <div v-else-if="activeTab === 'home'" class="fade-in">
      <!-- Create Lot Form -->
      <div class="enhanced-card mb-4">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="fas fa-plus-circle me-2 text-success"></i>
            Create New Parking Lot
          </h5>
        </div>
        <div class="card-body">
          <form @submit.prevent="createLot" novalidate>
            <div class="row g-3">
              <div class="col-md-4">
                <label class="form-label fw-semibold">
                  <i class="fas fa-tag me-1"></i>Name *
                </label>
                <input
                  v-model.trim="newLot.name"
                  @blur="newLotTouched.name = true"
                  :class="{ 'form-control': true, 'is-invalid': newLotTouched.name && !newLot.name }"
                  placeholder="Parking lot name"
                  required
                />
                <div class="invalid-feedback">Name is required.</div>
              </div>
              <div class="col-md-2">
                <label class="form-label fw-semibold">
                  <i class="fas fa-rupee-sign me-1"></i>Price/hr *
                </label>
                <input
                  v-model.number="newLot.price_per_hour"
                  @blur="newLotTouched.price = true"
                  type="number"
                  step="0.01"
                  :class="{ 'form-control': true, 'is-invalid': newLotTouched.price && newLot.price_per_hour <= 0 }"
                  placeholder="0.00"
                  min="0.01"
                  required
                />
                <div class="invalid-feedback">Price must be greater than 0.</div>
              </div>
              <div class="col-md-2">
                <label class="form-label fw-semibold">
                  <i class="fas fa-car me-1"></i>Total Spots *
                </label>
                <input
                  v-model.number="newLot.total_spots"
                  @blur="newLotTouched.spots = true"
                  type="number"
                  :class="{ 'form-control': true, 'is-invalid': newLotTouched.spots && newLot.total_spots < 1 }"
                  placeholder="0"
                  min="1"
                  required
                />
                <div class="invalid-feedback">At least one spot required.</div>
              </div>
              <div class="col-md-2">
                <label class="form-label fw-semibold">
                  <i class="fas fa-map-marker-alt me-1"></i>Address
                </label>
                <input
                  v-model.trim="newLot.address"
                  class="form-control"
                  placeholder="Street address"
                />
              </div>
              <div class="col-md-2">
                <label class="form-label fw-semibold">
                  <i class="fas fa-map-pin me-1"></i>Pin Code
                </label>
                <input
                  v-model.trim="newLot.pincode"
                  class="form-control"
                  placeholder="000000"
                />
              </div>
            </div>
            <div class="mt-3">
              <button class="btn btn-success" :disabled="!isCreateFormValid">
                <i class="fas fa-plus me-2"></i>Create Lot
              </button>
            </div>
            <div v-if="formError" class="alert alert-danger mt-3">
              <i class="fas fa-exclamation-triangle me-2"></i>{{ formError }}
            </div>
          </form>
        </div>
      </div>

      <!-- Edit Lot Form -->
      <div v-if="editing" class="enhanced-card mb-4">
        <div class="card-header bg-warning text-dark">
          <h5 class="mb-0">
            <i class="fas fa-edit me-2"></i>
            Edit Lot #{{ editing.id }}
          </h5>
        </div>
        <div class="card-body">
          <form @submit.prevent="submitEdit" novalidate>
            <div class="row g-3">
              <div class="col-md-4">
                <label class="form-label fw-semibold">Name *</label>
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
                <label class="form-label fw-semibold">Price/hr *</label>
                <input
                  v-model.number="editing.price_per_hour"
                  @blur="editingTouched.price = true"
                  type="number"
                  step="0.01"
                  :class="{ 'form-control': true, 'is-invalid': editingTouched.price && editing.price_per_hour <= 0 }"
                  placeholder="0.00"
                  min="0.01"
                  required
                />
                <div class="invalid-feedback">Price must be greater than 0.</div>
              </div>
              <div class="col-md-3">
                <label class="form-label fw-semibold">Address</label>
                <input
                  v-model.trim="editing.address"
                  class="form-control"
                  placeholder="Address"
                />
              </div>
              <div class="col-md-3">
                <label class="form-label fw-semibold">Pin Code</label>
                <input
                  v-model.trim="editing.pincode"
                  class="form-control"
                  placeholder="Pin code"
                />
              </div>
            </div>
            <div class="mt-3 d-flex gap-2">
              <button class="btn btn-primary" :disabled="!isEditFormValid">
                <i class="fas fa-save me-2"></i>Save Changes
              </button>
              <button
                type="button"
                class="btn btn-outline-secondary"
                @click="cancelEdit"
              >
                <i class="fas fa-times me-2"></i>Cancel
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Lots List -->
      <div class="enhanced-card">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="fas fa-parking me-2 text-primary"></i>
            Parking Lots Management
          </h5>
        </div>
        <div class="card-body">
          <div v-if="error" class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>{{ error }}
          </div>
          
          <div v-if="loading" class="loading-container">
            <div class="spinner-border text-primary"></div>
            <p class="mt-2 text-muted">Loading parking lots...</p>
          </div>

          <div v-if="lots.length && !loading" class="table-responsive">
            <table class="table table-hover">
              <thead class="table-dark">
                <tr>
                  <th><i class="fas fa-id-badge me-1"></i>ID</th>
                  <th><i class="fas fa-tag me-1"></i>Name</th>
                  <th><i class="fas fa-rupee-sign me-1"></i>Price/hr</th>
                  <th><i class="fas fa-car me-1"></i>Total</th>
                  <th><i class="fas fa-check-circle me-1"></i>Available</th>
                  <th><i class="fas fa-cogs me-1"></i>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="lot in lots" :key="lot.id" class="table-row-hover">
                  <td><span class="badge bg-secondary">{{ lot.id }}</span></td>
                  <td><strong>{{ lot.name }}</strong></td>
                  <td>₹{{ lot.price_per_hour }}</td>
                  <td>{{ lot.total_spots }}</td>
                  <td>
                    <span 
                      class="badge"
                      :class="lot.available_spots > 0 ? 'bg-success' : 'bg-danger'"
                    >
                      {{ lot.available_spots }}
                    </span>
                  </td>
                  <td>
                    <div class="btn-group" role="group">
                      <button
                        class="btn btn-sm btn-info"
                        @click.prevent="viewLot(lot)"
                        title="View Details"
                      >
                        <i class="fas fa-eye"></i>
                      </button>
                      <button
                        class="btn btn-sm btn-warning"
                        @click.prevent="startEdit(lot)"
                        title="Edit Lot"
                      >
                        <i class="fas fa-edit"></i>
                      </button>
                      <button
                        class="btn btn-sm btn-danger"
                        @click.prevent="deleteLot(lot.id)"
                        title="Delete Lot"
                      >
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-else-if="!loading" class="empty-state">
            <i class="fas fa-parking fa-3x text-muted mb-3"></i>
            <p class="text-muted">No parking lots found.</p>
            <small class="text-muted">Create your first parking lot using the form above.</small>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Enhanced View Lot Modal -->
  <div
    v-if="selectedLot"
    class="modal fade show"
    style="display: block; background: rgba(0, 0, 0, 0.5);"
  >
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">
        <div class="modal-header bg-primary text-white">
          <h5 class="modal-title">
            <i class="fas fa-parking me-2"></i>
            {{ selectedLot.prime_location_name || ('Parking Lot #' + selectedLot.id) }}
          </h5>
          <button type="button" class="btn-close btn-close-white" @click="selectedLot = null"></button>
        </div>
        <div class="modal-body">
          <div class="occupancy-stats mb-4">
            <div class="row text-center">
              <div class="col-4">
                <div class="stat-card bg-success text-white">
                  <i class="fas fa-check-circle fa-2x mb-2"></i>
                  <h4>{{ selectedLot.available_spots }}</h4>
                  <p class="mb-0">Available</p>
                </div>
              </div>
              <div class="col-4">
                <div class="stat-card bg-danger text-white">
                  <i class="fas fa-car fa-2x mb-2"></i>
                  <h4>{{ selectedLot.total_spots - selectedLot.available_spots }}</h4>
                  <p class="mb-0">Occupied</p>
                </div>
              </div>
              <div class="col-4">
                <div class="stat-card bg-info text-white">
                  <i class="fas fa-calculator fa-2x mb-2"></i>
                  <h4>{{ selectedLot.total_spots }}</h4>
                  <p class="mb-0">Total</p>
                </div>
              </div>
            </div>
          </div>
          
          <hr>
          <h6 class="mb-3">
            <i class="fas fa-th-large me-2"></i>Spot Layout
          </h6>
          <div class="spots-grid">
            <div
              v-for="spot in selectedLot.spots"
              :key="spot.id"
              class="spot-box"
              :class="spot.status === 'A' ? 'available' : 'occupied'"
              @click="spot.status === 'O' && viewSpot(spot.id)"
              :title="spot.status === 'A' ? 'Available' : 'Occupied - Click for details'"
            >
              <i :class="spot.status === 'A' ? 'fas fa-check' : 'fas fa-car'"></i>
              <small>{{ spot.id }}</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Enhanced Spot Details Modal -->
  <div
    v-if="showSpotModal"
    class="modal fade show"
    style="display: block; background: rgba(0,0,0,0.5);"
  >
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header bg-info text-white">
          <h5 class="modal-title">
            <i class="fas fa-info-circle me-2"></i>
            Reservation #{{ spotDetails.reservation_id }}
          </h5>
          <button type="button" class="btn-close btn-close-white" @click="showSpotModal = false; spotDetails = null;"></button>
        </div>
        <div class="modal-body">
          <div class="reservation-details">
            <div class="detail-item">
              <i class="fas fa-user text-primary me-2"></i>
              <strong>User:</strong> {{ spotDetails.username }} (ID: {{ spotDetails.user_id }})
            </div>
            <div class="detail-item">
              <i class="fas fa-envelope text-primary me-2"></i>
              <strong>Email:</strong> {{ spotDetails.email }}
            </div>
            <div class="detail-item">
              <i class="fas fa-clock text-primary me-2"></i>
              <strong>Parked At:</strong> {{ formatDateTime(spotDetails.parked_at) }}
            </div>
            <div class="detail-item">
              <i class="fas fa-rupee-sign text-primary me-2"></i>
              <strong>Cost:</strong> ₹{{ spotDetails.parking_cost }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto'

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
      editingTouched: { name: false, price: false },
      selectedLot: null,

      // For spot details modal
      spotDetails: null,
      showSpotModal: false,

      // Summary data and chart instances
      summaryData: { revenue: [], occupancy: [] },
      summaryCharts: { revenue: null, occupancy: null },

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
        this.editing.price_per_hour > 0
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
      } else if (tab === 'summary') {
        this.fetchSummary()
      }
    },

    // Format datetime for display with smart relative time
    formatDateTime(dateStr) {
      if (!dateStr) return ''
      
      try {
        // Handle both ISO format with Z and without
        const cleanDateStr = dateStr.endsWith('Z') ? dateStr : dateStr + 'Z'
        const date = new Date(cleanDateStr)
        
        if (isNaN(date.getTime())) {
          return dateStr // Return original if parsing fails
        }
        
        const now = new Date()
        const diffMs = now - date
        const diffMins = Math.floor(diffMs / (1000 * 60))
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
        
        // Show relative time for recent dates
        if (diffMins < 1) {
          return 'Just now'
        } else if (diffMins < 60) {
          return `${diffMins} min${diffMins !== 1 ? 's' : ''} ago`
        } else if (diffHours < 24) {
          return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`
        } else if (diffDays < 7) {
          return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`
        } else {
          // Show formatted date for older entries
          return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })
        }
      } catch (e) {
        return dateStr // Return original on any error
      }
    },

    // Fetch all users for Users view
    async fetchUsers() {
      this.loadingUsers = true
      this.errorUsers = ''
      try {
        const resp = await this.$axios.get('/admin/users')
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
        const resp = await this.$axios.get('/admin/search', {
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
        const resp = await this.$axios.get('/auth/me')
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
        await this.$axios.put('/auth/profile', payload)
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
        const resp = await this.$axios.get('/admin/lots')
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
        const resp = await this.$axios.post('/admin/lots', payload)
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
      this.editingTouched = { name: true, price: true }
      if (!this.isEditFormValid) return

      const { id, name, price_per_hour, address, pincode } = this.editing
      try {
        await this.$axios.put(`/admin/lots/${id}`, {
          name,
          price_per_hour,
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
        await this.$axios.delete(`/admin/lots/${lotId}`)
        this.lots = this.lots.filter(l => l.id !== lotId)
      } catch (e) {
        alert(e.response?.data?.error || 'Delete failed')
      }
    },  // end deleteLot

    /**
     * Fetch and show details for a lot, including spot statuses.
     */
    async viewLot(lot) {
      try {
        const resp = await this.$axios.get(`/admin/lots/${lot.id}`);
        this.selectedLot = resp.data;
      } catch (e) {
        alert('Failed to load lot details');
      }
    },

    /**
     * Fetch reservation/user details for an occupied spot.
     */
    async viewSpot(spotId) {
      try {
        const resp = await this.$axios.get(`/admin/spots/${spotId}`);
        this.spotDetails = resp.data;
        this.showSpotModal = true;
      } catch (e) {
        alert(e.response?.data?.error || 'Failed to load spot details');
      }
    },

    /**
     * Load summary data for charts.
     */
    async fetchSummary() {
      try {
        const resp = await this.$axios.get('/admin/summary')
        this.summaryData = resp.data
        this.$nextTick(() => this.renderCharts())
      } catch {
        alert('Failed to load summary')
      }
    },


    renderCharts() {
      // destroy existing charts, if any
      if (this.summaryCharts.revenue) this.summaryCharts.revenue.destroy()
      if (this.summaryCharts.occupancy) this.summaryCharts.occupancy.destroy()

      // Revenue doughnut
      const revCtx = document.getElementById('revenueChart').getContext('2d')
      this.summaryCharts.revenue = new Chart(revCtx, {
        type: 'doughnut',
        data: {
          labels: this.summaryData.revenue.map(r => r.lot_name),
          datasets: [{
            data: this.summaryData.revenue.map(r => r.revenue)
          }]
        },
        options: {
          plugins: { title: { display: true, text: 'Revenue by Parking Lot' } }
        }
      })

      // Occupancy bar chart
      const occCtx = document.getElementById('occupancyChart').getContext('2d')
      this.summaryCharts.occupancy = new Chart(occCtx, {
        type: 'bar',
        data: {
          labels: this.summaryData.occupancy.map(o => o.lot_name),
          datasets: [
            { label: 'Available', data: this.summaryData.occupancy.map(o => o.available) },
            { label: 'Occupied', data: this.summaryData.occupancy.map(o => o.occupied) }
          ]
        },
        options: {
          plugins: { title: { display: true, text: 'Available vs Occupied Spots' } },
          responsive: true,
          scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } }
        }
      })
    },
  }
}
</script>

<style scoped>
/* Enhanced Admin Dashboard Styles */
.admin-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.nav-container {
  background: white;
  border-radius: 15px;
  padding: 0.5rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.nav-pills .nav-link {
  border-radius: 10px;
  margin: 0 0.25rem;
  transition: all 0.3s ease;
  font-weight: 500;
}

.nav-pills .nav-link:hover {
  background-color: #f8f9fa;
  transform: translateY(-2px);
}

.nav-pills .nav-link.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.enhanced-card {
  background: white;
  border-radius: 15px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
  border: none;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.enhanced-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.enhanced-card .card-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 3px solid #667eea;
  padding: 1.5rem;
}

.enhanced-card .card-body {
  padding: 2rem;
}

.loading-container {
  text-align: center;
  padding: 3rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
}

.table-hover tbody tr:hover {
  background-color: #f8f9fa;
  transform: scale(1.01);
  transition: all 0.2s ease;
}

.table-dark th {
  background: linear-gradient(135deg, #495057 0%, #343a40 100%);
  border: none;
}

.search-form {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 10px;
  border: 2px dashed #dee2e6;
}

.spots-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  padding: 1rem;
}

.spot-box {
  width: 60px;
  height: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.spot-box:hover {
  transform: scale(1.1);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.spot-box.available {
  background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
  border-color: #28a745;
  color: #155724;
}

.spot-box.occupied {
  background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
  border-color: #dc3545;
  color: #721c24;
}

.occupancy-stats .stat-card {
  padding: 1.5rem;
  border-radius: 10px;
  margin: 0 0.5rem;
}

.detail-item {
  padding: 0.75rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-item:last-child {
  border-bottom: none;
}

.btn-group .btn {
  margin: 0 2px;
}

.fade-in {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.chart-container {
  background: white;
  padding: 1rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.form-label.fw-semibold {
  color: #495057;
  margin-bottom: 0.5rem;
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.btn {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.alert {
  border-radius: 10px;
  border: none;
}

.badge {
  font-size: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
}

.reservation-details {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 10px;
}

@media (max-width: 768px) {
  .admin-header {
    padding: 1.5rem;
  }
  
  .enhanced-card .card-body {
    padding: 1.5rem;
  }
  
  .spots-grid {
    gap: 5px;
  }
  
  .spot-box {
    width: 50px;
    height: 50px;
  }
}
</style>