<template>
  <div class="container-fluid mt-4">
    <!-- Enhanced Header with Gradient -->
    <div class="user-header mb-4">
      <div class="row align-items-center">
        <div class="col">
          <h1 class="display-5 fw-bold text-white mb-0">
            <i class="fas fa-tachometer-alt me-3"></i>
            User Dashboard
          </h1>
          <p class="text-white-50 mb-0">Manage your parking reservations</p>
        </div>
        <div class="col-auto">
          <div class="badge bg-light text-dark fs-6 px-3 py-2">
            <i class="fas fa-user me-2"></i>
            User
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
            :class="{ active: activeTab === 'summary' }"
            href="#"
            @click.prevent="selectTab('summary')"
          >
            <i class="fas fa-chart-bar me-2"></i>Summary
          </a>
        </li>
      </ul>
    </div>

    <!-- Summary View -->
    <div v-if="activeTab === 'summary'" class="fade-in">
      <!-- Summary Cards -->
      <div class="row mb-4">
        <div class="col-md-6 mb-3">
          <div class="stats-card bg-primary text-white">
            <div class="stats-icon">
              <i class="fas fa-calendar-alt fa-2x"></i>
            </div>
            <div class="stats-content">
              <h5 class="mb-0">Total Reservations</h5>
              <p class="fs-3 fw-bold mb-0">{{ summary.total_reservations }}</p>
            </div>
          </div>
        </div>
        <div class="col-md-6 mb-3">
          <div class="stats-card bg-success text-white">
            <div class="stats-icon">
              <i class="fas fa-rupee-sign fa-2x"></i>
            </div>
            <div class="stats-content">
              <h5 class="mb-0">Total Spent</h5>
              <p class="fs-3 fw-bold mb-0">₹{{ summary.total_spent.toFixed(2) }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- User summary chart -->
      <div class="enhanced-card">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="fas fa-chart-line me-2 text-primary"></i>
            Reservations & Spending Summary
          </h5>
        </div>
        <div class="card-body">
          <div class="chart-container">
            <canvas id="userSummaryChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Home View -->
    <div v-if="activeTab === 'home'" class="fade-in">
      <!-- Export CSV Card -->
      <div class="enhanced-card mb-4">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="fas fa-download me-2 text-success"></i>
            Export Data
          </h5>
        </div>
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center">
          <div>
            <h6 class="mb-1">
              <i class="fas fa-file-export me-2"></i>Export Your Data
            </h6>
            <p class="mb-0 text-muted small">Download your complete parking history as CSV</p>
          </div>
          <div>
            <button 
              class="btn btn-success"
              :disabled="exportStatus.isExporting"
              @click="triggerExport"
            >
              <span v-if="exportStatus.isExporting" class="spinner-border spinner-border-sm me-2" role="status"></span>
              <i v-else class="fas fa-download me-2"></i>
              {{ exportStatus.isExporting ? 'Generating...' : 'Export CSV' }}
            </button>
          </div>
        </div>
        
        <!-- Export Status Alert -->
        <div v-if="exportStatus.message" class="alert mt-3 mb-0" :class="exportStatus.alertClass" role="alert">
          <i class="fas fa-info-circle me-2"></i>{{ exportStatus.message }}
          <button 
            v-if="exportStatus.downloadUrl" 
            @click="downloadFile"
            class="btn btn-sm btn-success ms-2"
          >
            <i class="fas fa-download me-1"></i>Download CSV
          </button>
        </div>
      </div>
      </div>

      <!-- Available Lots -->
      <div class="enhanced-card mb-4">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="fas fa-parking me-2 text-primary"></i>
            Available Parking Lots
          </h5>
        </div>
        <div class="card-body">
          <div v-if="loadingLots" class="loading-container">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Loading parking lots...</p>
          </div>
          <div v-if="errorLots" class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>{{ errorLots }}
          </div>
          <div v-if="lots.length && !loadingLots" class="table-responsive">
            <table class="table table-hover">
              <thead class="table-dark">
                <tr>
                  <th><i class="fas fa-id-badge me-1"></i>ID</th>
                  <th><i class="fas fa-tag me-1"></i>Name</th>
                  <th><i class="fas fa-rupee-sign me-1"></i>Price/hr</th>
                  <th><i class="fas fa-check-circle me-1"></i>Available</th>
                  <th><i class="fas fa-cogs me-1"></i>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="lot in lots" :key="lot.id" class="table-row-hover">
                  <td><span class="badge bg-secondary">{{ lot.id }}</span></td>
                  <td><strong>{{ lot.name }}</strong></td>
                  <td>₹{{ lot.price_per_hour }}</td>
                  <td>
                    <span 
                      class="badge"
                      :class="lot.available_spots > 0 ? 'bg-success' : 'bg-danger'"
                    >
                      {{ lot.available_spots }}
                    </span>
                  </td>
                  <td>
                    <button
                      class="btn btn-sm btn-primary"
                      :disabled="lot.available_spots === 0"
                      @click="bookSpot(lot.id)"
                    >
                      <i class="fas fa-calendar-plus me-1"></i>
                      {{ lot.available_spots ? 'Book' : 'Full' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else-if="!loadingLots" class="empty-state">
            <i class="fas fa-parking fa-3x text-muted mb-3"></i>
            <p class="text-muted">No parking lots available.</p>
          </div>
        </div>
      </div>

      <!-- My Reservations -->
      <div class="enhanced-card">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="fas fa-list-alt me-2 text-info"></i>
            My Reservations
          </h5>
        </div>
        <div class="card-body">
          <div v-if="loadingResv" class="loading-container">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Loading reservations...</p>
          </div>
          <div v-if="errorResv" class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>{{ errorResv }}
          </div>
          <div v-if="reservations.length && !loadingResv" class="table-responsive">
            <table class="table table-hover">
              <thead class="table-dark">
                <tr>
                  <th><i class="fas fa-id-badge me-1"></i>ID</th>
                  <th><i class="fas fa-parking me-1"></i>Lot ID</th>
                  <th><i class="fas fa-map-marker-alt me-1"></i>Spot ID</th>
                  <th><i class="fas fa-clock me-1"></i>Parked At</th>
                  <th><i class="fas fa-sign-out-alt me-1"></i>Left At</th>
                  <th><i class="fas fa-rupee-sign me-1"></i>Cost</th>
                  <th><i class="fas fa-cogs me-1"></i>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in reservations" :key="r.id" class="table-row-hover">
                  <td><span class="badge bg-info">{{ r.id }}</span></td>
                  <td><span class="badge bg-secondary">{{ r.lot_id }}</span></td>
                  <td><span class="badge bg-warning">{{ r.spot_id }}</span></td>
                  <td>{{ formatDateTime(r.parked_at) }}</td>
                  <td>
                    <span v-if="r.left_at">{{ formatDateTime(r.left_at) }}</span>
                    <span v-else class="badge bg-success">Active</span>
                  </td>
                  <td>
                    <span v-if="r.cost != null" class="fw-bold text-success">₹{{ r.cost.toFixed(2) }}</span>
                    <span v-else class="text-muted">—</span>
                  </td>
                  <td>
                    <button
                      class="btn btn-sm"
                      :class="r.left_at ? 'btn-outline-secondary' : 'btn-danger'"
                      :disabled="r.left_at"
                      @click="releaseSpot(r.id)"
                    >
                      <i :class="r.left_at ? 'fas fa-check' : 'fas fa-sign-out-alt'" class="me-1"></i>
                      {{ r.left_at ? 'Released' : 'Release' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else-if="!loadingResv" class="empty-state">
            <i class="fas fa-calendar-times fa-3x text-muted mb-3"></i>
            <p class="text-muted">You have no reservations.</p>
          </div>
        </div>
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
/* Enhanced User Dashboard Styles */
.user-header {
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

.stats-card {
  display: flex;
  align-items: center;
  padding: 2rem;
  border-radius: 15px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.stats-card:hover {
  transform: translateY(-5px);
}

.stats-icon {
  margin-right: 1.5rem;
  opacity: 0.8;
}

.stats-content h5 {
  font-size: 1rem;
  font-weight: 600;
  opacity: 0.9;
}

.stats-content .fs-3 {
  font-size: 2.5rem !important;
  font-weight: 700;
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

.table-row-hover {
  transition: all 0.2s ease;
}

@media (max-width: 768px) {
  .user-header {
    padding: 1.5rem;
  }
  
  .enhanced-card .card-body {
    padding: 1.5rem;
  }
  
  .stats-card {
    flex-direction: column;
    text-align: center;
  }
  
  .stats-icon {
    margin-right: 0;
    margin-bottom: 1rem;
  }
}
</style>