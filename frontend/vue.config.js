const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true
})

module.exports = {
  devServer: {
    proxy: {
      '^/auth': {
        target: 'http://localhost:5001',
        changeOrigin: true
      },
      '^/admin': {
        target: 'http://localhost:5001',
        changeOrigin: true
      },
      '^/user': {
        target: 'http://localhost:5001',
        changeOrigin: true
      }
    }
  }
}