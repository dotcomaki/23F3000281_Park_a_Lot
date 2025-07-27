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
      <!-- Export CSV Button -->
      <div class="card mb-4 p-3">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h6>Export Your Data</h6>
            <p class="mb-0 text-muted small">Download your complete parking history as CSV</p>
          </div>
          <div>
            <button 
              class="btn btn-outline-primary"
              :disabled="exportStatus.isExporting"
              @click="triggerExport"
            >
              <span v-if="exportStatus.isExporting" class="spinner-border spinner-border-sm me-2" role="status"></span>
              {{ exportStatus.isExporting ? 'Generating...' : 'Export CSV' }}
            </button>
          </div>
        </div>
        
        <!-- Export Status Alert -->
        <div v-if="exportStatus.message" class="alert mt-3 mb-0" :class="exportStatus.alertClass" role="alert">
          {{ exportStatus.message }}
          <button 
            v-if="exportStatus.downloadUrl" 
            @click="downloadFile"
            class="btn btn-sm btn-success ms-2"
          >
            Download CSV
          </button>
        </div>
      </div>

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
              <th>ID</th>
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
              <td>{{ formatDateTime(r.parked_at) }}</td>
              <td>{{ r.left_at ? formatDateTime(r.left_at) : '—' }}</td>
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
      errorResv: '',
      // Export status
      exportStatus: {
        isExporting: false,
        taskId: null,
        message: '',
        alertClass: '',
        downloadUrl: null
      }
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
      const resp = await this.$axios.get('/user/summary')
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
        const resp = await this.$axios.get('/user/lots')
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
        const resp = await this.$axios.get('/user/reservations');
        this.reservations = resp.data
      } catch (e) {
        this.errorResv = e.response?.data?.error || 'Failed to load reservations'
      } finally {
        this.loadingResv = false
      }
    },
    async bookSpot(lotId) {
      try {
        await this.$axios.post('/user/reservations', { lot_id: lotId })
        // refresh data
        await Promise.all([this.fetchSummary(), this.fetchLots(), this.fetchReservations()])
      } catch (e) {
        alert(e.response?.data?.error || 'Booking failed!')
      }
    },
    async releaseSpot(resvId) {
      try {
        await this.$axios.post(`/user/reservations/${resvId}/release`)
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

/**
 * Trigger CSV export
 */
async triggerExport() {
  this.exportStatus.isExporting = true;
  this.exportStatus.message = '';
  this.exportStatus.downloadUrl = null;
  
  try {
    const response = await this.$axios.post('/user/export');
    this.exportStatus.taskId = response.data.task_id;
    this.exportStatus.message = 'Export started! Checking status...';
    this.exportStatus.alertClass = 'alert-info';
    
    // Start polling for status
    this.pollExportStatus();
  } catch (error) {
    this.exportStatus.isExporting = false;
    this.exportStatus.message = 'Failed to start export: ' + (error.response?.data?.error || error.message);
    this.exportStatus.alertClass = 'alert-danger';
  }
},

/**
 * Poll export status
 */
async pollExportStatus() {
  if (!this.exportStatus.taskId) return;
  
  try {
    const response = await this.$axios.get(`/user/export/${this.exportStatus.taskId}/status`);
    const { state, download_url, error } = response.data;
    
    if (state === 'SUCCESS') {
      this.exportStatus.isExporting = false;
      this.exportStatus.message = 'Export completed successfully! Your CSV file is ready for download.';
      this.exportStatus.alertClass = 'alert-success';
      this.exportStatus.downloadUrl = download_url;
    } else if (state === 'FAILURE') {
      this.exportStatus.isExporting = false;
      this.exportStatus.message = 'Export failed: ' + (error || 'Unknown error');
      this.exportStatus.alertClass = 'alert-danger';
    } else if (state === 'PENDING' || state === 'PROGRESS') {
      // Continue polling
      setTimeout(() => this.pollExportStatus(), 2000);
    }
  } catch (error) {
    this.exportStatus.isExporting = false;
    this.exportStatus.message = 'Failed to check export status: ' + (error.response?.data?.error || error.message);
    this.exportStatus.alertClass = 'alert-danger';
  }
},

/**
 * Download the CSV file with proper authentication
 */
async downloadFile() {
  if (!this.exportStatus.downloadUrl) return;
  
  try {
    // Get the JWT token from localStorage or wherever it's stored
    const token = localStorage.getItem('access_token') || 
                  this.$axios.defaults.headers.common['Authorization']?.replace('Bearer ', '');
    
    if (!token) {
      this.exportStatus.message = 'Authentication required. Please log in again.';
      this.exportStatus.alertClass = 'alert-danger';
      return;
    }
    
    const response = await this.$axios.get(this.exportStatus.downloadUrl, {
      responseType: 'blob', // Important for file downloads
      headers: {
        'Authorization': `Bearer ${token.replace('Bearer ', '')}`
      }
    });
    
    // Create blob link to download
    const blob = new Blob([response.data], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    // Extract filename from response headers or use default
    const contentDisposition = response.headers['content-disposition'];
    let filename = 'parking_history.csv';
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }
    
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    link.remove();
    window.URL.revokeObjectURL(url);
    
  } catch (error) {
    if (error.response?.status === 401) {
      this.exportStatus.message = 'Authentication expired. Please log in again.';
    } else {
      this.exportStatus.message = 'Failed to download file: ' + (error.response?.data?.error || error.message);
    }
    this.exportStatus.alertClass = 'alert-danger';
  }
},

/**
 * Format datetime string to user-friendly format
 */
formatDateTime(dateTimeString) {
  if (!dateTimeString) return '—';
  
  try {
    const date = new Date(dateTimeString);
    
    // Check if date is valid
    if (isNaN(date.getTime())) return dateTimeString;
    
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);
    
    // If it's within 24 hours, show relative time
    if (diffInHours < 24) {
      const options = {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      };
      const timeStr = date.toLocaleTimeString('en-US', options);
      
      if (diffInHours < 1) {
        const diffInMinutes = Math.floor((now - date) / (1000 * 60));
        if (diffInMinutes < 1) return 'Just now';
        if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
      }
      
      if (date.toDateString() === now.toDateString()) {
        return `Today ${timeStr}`;
      } else {
        return `Yesterday ${timeStr}`;
      }
    }
    
    // For older dates, show full date and time
    const options = {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    };
    
    return date.toLocaleDateString('en-US', options);
  } catch (error) {
    console.warn('Error formatting date:', error);
    return dateTimeString;
  }
},
  }
}
</script>

<style scoped>
/* Add any component-specific styles here */
</style>