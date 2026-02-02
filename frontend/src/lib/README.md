# Lib Folder

Berisi utility functions, helpers, dan service layer untuk aplikasi.

## Files

### `utils.ts`
General utility functions yang digunakan di berbagai komponen.

**Fungsi yang Ada/Direncanakan:**

```typescript
// String utilities
export function capitalize(str: string): string
export function truncate(str: string, length: number): string
export function slugify(str: string): string

// Date utilities
export function formatDate(date: Date, format: string): string
export function getTimeAgo(date: Date): string
export function formatDuration(seconds: number): string // HH:MM:SS

// File utilities
export function formatFileSize(bytes: number): string // 1.5 MB
export function getFileExtension(filename: string): string
export function isValidFileType(file: File, allowedTypes: string[]): boolean

// Array utilities
export function unique<T>(arr: T[]): T[]
export function groupBy<T, K>(arr: T[], key: (item: T) => K): Map<K, T[]>

// Validation
export function isValidEmail(email: string): boolean
export function isValidPhone(phone: string): boolean
export function isValidUUID(uuid: string): boolean
```

### `api-client.ts` (Planned)
HTTP client untuk berkomunikasi dengan backend API.

```typescript
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
    }
    return Promise.reject(error)
  }
)

// API endpoints
export const api = {
  // Transcript endpoints
  uploadTranscript: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/transcripts/upload', formData)
  },
  
  getTranscripts: () => apiClient.get('/transcripts'),
  
  getTranscript: (id: string) => apiClient.get(`/transcripts/${id}`),
  
  deleteTranscript: (id: string) => apiClient.delete(`/transcripts/${id}`),

  // Analysis endpoints
  analyzeTranscript: (id: string) => apiClient.post(`/transcripts/${id}/analyze`),
  
  getAnalysis: (id: string) => apiClient.get(`/transcripts/${id}/analysis`),

  // Zoom endpoints
  getZoomRecordings: () => apiClient.get('/zoom/recordings'),
  
  syncZoomRecordings: () => apiClient.post('/zoom/sync'),

  // Auth endpoints
  login: (email: string, password: string) =>
    apiClient.post('/auth/login', { email, password }),
  
  signup: (data: SignupData) =>
    apiClient.post('/auth/signup', data),
  
  verifyOTP: (email: string, otp: string) =>
    apiClient.post('/auth/otp/verify', { email, otp })
}

export default apiClient
```

### `store.ts` (Planned)
State management menggunakan Pinia (jika diperlukan).

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))
  
  const isAuthenticated = computed(() => !!token.value)
  
  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('auth_token', newToken)
  }
  
  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')
  }
  
  return { user, token, isAuthenticated, setToken, logout }
})

export const useTranscriptStore = defineStore('transcript', () => {
  const transcripts = ref([])
  const loading = ref(false)
  
  async function fetchTranscripts() {
    loading.value = true
    try {
      const { data } = await api.getTranscripts()
      transcripts.value = data
    } finally {
      loading.value = false
    }
  }
  
  return { transcripts, loading, fetchTranscripts }
})
```

### `composables.ts` (Planned)
Reusable logic menggunakan Vue Composition API.

```typescript
// useTranscriptUpload.ts
export function useTranscriptUpload() {
  const file = ref(null)
  const uploading = ref(false)
  const error = ref(null)
  
  async function handleUpload() {
    uploading.value = true
    try {
      await api.uploadTranscript(file.value)
      // Success
    } catch (err) {
      error.value = err.message
    } finally {
      uploading.value = false
    }
  }
  
  return { file, uploading, error, handleUpload }
}

// useAsync.ts - Generic async handler
export function useAsync(asyncFn, initialValue = null) {
  const data = ref(initialValue)
  const loading = ref(false)
  const error = ref(null)
  
  async function execute() {
    loading.value = true
    try {
      data.value = await asyncFn()
    } catch (err) {
      error.value = err
    } finally {
      loading.value = false
    }
  }
  
  return { data, loading, error, execute }
}
```

## Usage Examples

### Menggunakan API Client
```typescript
import { api } from '@/lib/api-client'

export default {
  async mounted() {
    try {
      const { data } = await api.getTranscripts()
      this.transcripts = data
    } catch (error) {
      console.error('Failed to fetch transcripts:', error)
    }
  }
}
```

### Menggunakan Utilities
```typescript
import { formatDate, formatFileSize, capitalize } from '@/lib/utils'

const date = new Date()
console.log(formatDate(date, 'DD/MM/YYYY'))

console.log(formatFileSize(1536)) // "1.5 MB"

console.log(capitalize('hello')) // "Hello"
```

### Menggunakan Store
```typescript
import { useAuthStore } from '@/lib/store'

export default {
  setup() {
    const authStore = useAuthStore()
    
    const logout = () => {
      authStore.logout()
      router.push('/login')
    }
    
    return { logout }
  }
}
```

## Best Practices

- Keep utilities pure & stateless
- Use TypeScript untuk type safety
- Document function signatures
- Group related functions dalam file terpisah
- Implement error handling di API client
- Cache API responses jika diperlukan
- Use composables untuk reusable logic
- Avoid tight coupling dengan specific components
