import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

export const ask = (query) => {
  return api.post('/ask', { query })
}

export const getConfig = () => {
  return api.get('/config')
}

export const buildDb = (params) => {
  return api.post('/build-db', params)
}

export const getFiles = () => {
  return api.get('/files')
}

export const previewFile = (filename) => {
  return api.get(`/preview/${filename}`)
}

export const deleteFile = (filename) => {
  return api.delete(`/file/${filename}`)
}

export const uploadFile = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const getChunks = () => {
  return api.get('/chunks')
}

export default api