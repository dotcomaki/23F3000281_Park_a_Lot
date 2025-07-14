<template>
  <div class="container mt-5">
    <h2>User Dashboard</h2>

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
          :class="{ active: activeTab === 'summary' }"
          href="#"
          @click.prevent="selectTab('summary')"
        >Summary</a>
      </li>
    </ul>

    <div v-if="activeTab === 'summary'">
      <!-- Summary Cards -->
      <div class="row mb-4">
        <div class="col-md-6 mb-3">
          <div class="card p-3 text-center">
            <h5>Total Reservations</h5>
            <p class="fs-3">{{ summary.total_reservations }}</p>
          </div>
        </div>
        <div class="col-md-6 mb-3">
          <div class="card p-3 text-center">
            <h5>Total Spent</h5>
            <p class="fs-3">₹ {{ summary.total_spent.toFixed(2) }}</p>
          </div>
        </div>
      </div>
      <!-- User summary chart -->
      <div class="card mb-4 p-3">
        <h5>Reservations & Spending Summary</h5>
        <canvas id="userSummaryChart"></canvas>
      </div>
    </div>

    <div v-if="activeTab === 'home'">
      <!-- Available Lots -->
      <div class="card mb-4 p-3">
        <h5>Available Parking Lots</h5>
        <div v-if="loadingLots" class="text-center my-3">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-if="errorLots" class="alert alert-danger">{{ errorLots }}</div>
        <table v-if="lots.length" class="table table-hover">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Price/hr</th>
              <th>Available</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="lot in lots" :key="lot.id">
              <td>{{ lot.id }}</td>
              <td>{{ lot.name }}</td>
              <td>₹ {{ lot.price_per_hour }}</td>
              <td>{{ lot.available_spots }}</td>
              <td>
                <button
                  class="btn btn-sm btn-primary"
                  :disabled="lot.available_spots === 0"
                  @click="bookSpot(lot.id)"
                >
                  {{ lot.available_spots ? 'Book' : 'Full' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else-if="!loadingLots">No parking lots available.</p>
      </div>

      <!-- My Reservations -->
      <div class="card p-3">
        <h5>My Reservations</h5>
        <div v-if="loadingResv" class="text-center my-3">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-if="errorResv" class="alert alert-danger">{{ errorResv }}</div>
        <table v-if="reservations.length" class="table table-striped">
          <thead>
            <tr>
              <th>Resv ID</th>
              <th>Lot ID</th>
              <th>Spot ID</th>
              <th>Parked At</th>
              <th>Left At</th>
              <th>Cost</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in reservations" :key="r.id">
              <td>{{ r.id }}</td>
              <td>{{ r.lot_id }}</td>
              <td>{{ r.spot_id }}</td>
              <td>{{ r.parked_at }}</td>
              <td>{{ r.left_at || '—' }}</td>
              <td>{{ r.cost != null ? `₹ ${r.cost.toFixed(2)}` : '—' }}</td>
              <td>
                <button
                  class="btn btn-sm btn-danger"
                  :disabled="r.left_at"
                  @click="releaseSpot(r.id)"
                >
                  {{ r.left_at ? 'Released' : 'Release' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else-if="!loadingResv">You have no reservations.</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import Chart from 'chart.js/auto'

export default {
  name: 'UserDashboard',
  data() {
    return {
      // current tab: 'home' or 'summary'
      activeTab: 'home',
      summary: { total_reservations: 0, total_spent: 0 },
      lots: [],
      reservations: [],
      // Chart.js instance for user summary
      summaryChart: null,
      loadingLots: false,
      loadingResv: false,
      errorLots: '',
      errorResv: ''
    }
  },
  async mounted() {
    // initial load: lots and reservations only
    await Promise.all([
      this.fetchLots(),
      this.fetchReservations()
    ])
  },
  methods: {
      async fetchSummary() {
    try {
      const resp = await axios.get('/user/summary')
      this.summary = resp.data
      // render chart after data update
      this.$nextTick(() => this.renderUserChart())
    } catch {
      // silently ignore summary errors
    }
  },
    async fetchLots() {
      this.loadingLots = true
      this.errorLots = ''
      try {
        const resp = await axios.get('/user/lots')
        this.lots = resp.data
      } catch (e) {
        this.errorLots = e.response?.data?.error || 'Failed to load lots'
      } finally {
        this.loadingLots = false
      }
    },
    async fetchReservations() {
      this.loadingResv = true
      this.errorResv = ''
      try {
        const resp = await axios.get('/user/reservations')
        this.reservations = resp.data
      } catch (e) {
        this.errorResv = e.response?.data?.error || 'Failed to load reservations'
      } finally {
        this.loadingResv = false
      }
    },
    async bookSpot(lotId) {
      try {
        await axios.post('/user/reservations', { lot_id: lotId })
        // refresh data
        await Promise.all([this.fetchSummary(), this.fetchLots(), this.fetchReservations()])
      } catch (e) {
        alert(e.response?.data?.error || 'Booking failed!')
      }
    },
    async releaseSpot(resvId) {
      try {
        await axios.post(`/user/reservations/${resvId}/release`)
        // refresh data
        await Promise.all([this.fetchSummary(), this.fetchLots(), this.fetchReservations()])
      } catch (e) {
        alert(e.response?.data?.error || 'Release failed')
      }
    },

    /**
 * Render the user summary bar chart.
 */
renderUserChart() {
  const canvas = document.getElementById('userSummaryChart')
  if (!canvas) return  // chart tab isn’t active yet
  // Destroy existing chart if present
  if (this.summaryChart) this.summaryChart.destroy()
  // Get canvas context
  const ctx = canvas.getContext('2d')
  this.summaryChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Total Reservations', 'Total Spent'],
      datasets: [{
        label: 'You',
        data: [this.summary.total_reservations, this.summary.total_spent],
      }]
    },
    options: {
      plugins: {
        title: { display: true, text: 'Your Parking Usage Summary' }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  })
},

/**
 * Switches the current dashboard tab.
 */
selectTab(tab) {
  this.activeTab = tab;
  if (tab === 'home') {
    this.fetchLots();
    this.fetchReservations();
  } else if (tab === 'summary') {
    this.fetchSummary();
  }
},
  }
}
</script>

<style scoped>
/* Add any component-specific styles here */
</style>