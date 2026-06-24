import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  const config = ref({
    chunk_size: 500,
    chunk_overlap: 100,
    split_mode: 'zh',
    top_k: 5
  })

  const files = ref([])

  const updateConfig = (newConfig) => {
    config.value = { ...config.value, ...newConfig }
  }

  const updateFiles = (newFiles) => {
    files.value = newFiles
  }

  return {
    config,
    files,
    updateConfig,
    updateFiles
  }
})