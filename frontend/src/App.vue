<template>
    <div class="container">
        <header class="mb-4">
            <h1 style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">
                🎙️ Bot Zoom Transcription
            </h1>
            <p class="text-muted">Upload or record audio for automatic transcription using Whisper AI</p>
        </header>

        <div class="grid lg:grid-cols-3 gap-4">
            <!-- Left Panel: Controls -->
            <div>
                <div class="card mb-4">
                    <div class="card-header">
                        <h2 class="card-title">Input Source</h2>
                        <p class="card-description">Choose how to input audio</p>
                    </div>

                    <!-- Tabs -->
                    <div class="tabs">
                        <button class="tab" :class="{ active: activeTab === 'record' }" @click="activeTab = 'record'">
                            Record
                        </button>
                        <button class="tab" :class="{ active: activeTab === 'upload' }" @click="activeTab = 'upload'">
                            Upload
                        </button>
                        <button class="tab" :class="{ active: activeTab === 'latest' }" @click="activeTab = 'latest'">
                            Latest
                        </button>
                    </div>

                    <!-- Tab Content: Record -->
                    <div v-if="activeTab === 'record'" class="mt-2">
                        <div class="text-center">
                            <button class="record-button" :class="{ recording: isRecording }" @click="toggleRecording"
                                :disabled="isProcessing">
                                <svg v-if="!isRecording" xmlns="http://www.w3.org/2000/svg" fill="none"
                                    viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                                </svg>
                                <svg v-else xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24">
                                    <rect x="6" y="6" width="12" height="12" rx="2" />
                                </svg>
                            </button>

                            <div class="flex items-center justify-center gap-2 text-sm">
                                <span class="status-indicator" :class="statusClass"></span>
                                <span class="text-muted">{{ statusText }}</span>
                            </div>

                            <p class="text-xs text-muted mt-2">{{ recordingHint }}</p>
                        </div>
                    </div>

                    <!-- Tab Content: Upload -->
                    <div v-if="activeTab === 'upload'" class="mt-2">
                        <div class="card" style="border-style: dashed; text-align: center; padding: 2rem;">
                            <p class="text-sm mb-2">Drag & drop audio file here</p>
                            <p class="text-xs text-muted mb-2">Supports mp3, wav, m4a, webm</p>
                            <input type="file" ref="fileInput" accept="audio/*" @change="onFileChange" />
                            <button class="btn btn-outline" @click="$refs.fileInput.click()">
                                Choose File
                            </button>
                        </div>
                    </div>

                    <!-- Tab Content: Latest -->
                    <div v-if="activeTab === 'latest'" class="mt-2">
                        <div v-if="latestTranscript" class="card">
                            <p class="text-sm mb-2"><strong>Latest Transcript</strong></p>
                            <div class="text-xs text-muted">
                                <p>ID: {{ latestTranscript.id }}</p>
                                <p>Language: {{ latestTranscript.language }}</p>
                                <p>Segments: {{ latestTranscript.segments?.length || 0 }}</p>
                                <p>Created: {{ formatDate(latestTranscript.created_at) }}</p>
                            </div>
                            <button class="btn btn-primary mt-2" @click="loadLatestTranscript">
                                Load Transcript
                            </button>
                        </div>
                        <div v-else class="text-sm text-muted text-center">
                            <p>No transcripts available yet</p>
                            <button class="btn btn-outline mt-2" @click="fetchLatest">
                                Refresh
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Processing Info -->
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Processing Profile</h2>
                    </div>
                    <div class="text-xs">
                        <div class="flex justify-between mb-2">
                            <span class="text-muted">Engine</span>
                            <span>Whisper · {{ model || 'small' }}</span>
                        </div>
                        <div class="flex justify-between mb-2">
                            <span class="text-muted">Language</span>
                            <span>{{ displayLanguage }}</span>
                        </div>
                        <div class="flex justify-between" v-if="device">
                            <span class="text-muted">Device</span>
                            <span>{{ device.toUpperCase() }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right Panel: Transcript -->
            <div class="card">
                <div class="card-header">
                    <div class="flex justify-between items-center">
                        <div>
                            <h2 class="card-title">Transcript</h2>
                            <p class="card-description">Transcription results</p>
                        </div>
                        <button v-if="segments.length > 0" class="btn btn-outline text-xs" @click="downloadTranscript">
                            Download
                        </button>
                    </div>
                </div>

                <!-- Loading State -->
                <div v-if="isProcessing" class="text-center" style="padding: 3rem;">
                    <div class="spinner" style="width: 2rem; height: 2rem; margin: 0 auto 1rem;"></div>
                    <p class="text-muted">Processing audio...</p>
                </div>

                <!-- Empty State -->
                <div v-else-if="segments.length === 0" class="text-center text-muted" style="padding: 3rem;">
                    <p>No transcript yet</p>
                    <p class="text-xs mt-2">Upload or record audio to get started</p>
                </div>

                <!-- Transcript Segments -->
                <div v-else class="scroll-area">
                    <div v-for="seg in segments" :key="seg.id" class="segment">
                        <div class="segment-header">
                            <span class="badge">{{ seg.speaker }}</span>
                            <span>{{ seg.start.toFixed(1) }}s - {{ seg.end.toFixed(1) }}s</span>
                        </div>
                        <p class="segment-text">{{ seg.text }}</p>
                    </div>
                </div>

                <!-- Full Text Tab -->
                <div v-if="fullText" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #334155;">
                    <h3 class="text-sm mb-2" style="font-weight: 600;">Full Text</h3>
                    <p class="text-sm" style="line-height: 1.6;">{{ fullText }}</p>
                </div>
            </div>
        </div>

        <!-- Toast notifications -->
        <div v-if="toast.show" class="toast" :class="toast.type">
            {{ toast.message }}
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// API base URL
const API_BASE = '/api'

// State
const activeTab = ref('record')
const isRecording = ref(false)
const isProcessing = ref(false)
const segments = ref([])
const fullText = ref('')
const language = ref(null)
const model = ref(null)
const device = ref(null)
const latestTranscript = ref(null)
const fileInput = ref(null)

// MediaRecorder state
let mediaRecorder = null
let mediaStream = null
let recordedChunks = []

// Toast state
const toast = ref({
    show: false,
    message: '',
    type: 'info'
})

// Computed
const displayLanguage = computed(() => {
    if (!language.value) return 'Auto detect'
    const langMap = {
        'id': 'Indonesian',
        'en': 'English',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean',
    }
    return langMap[language.value] || language.value
})

const statusText = computed(() => {
    if (isProcessing.value) return 'Processing · transcribing audio'
    if (isRecording.value) return 'Live · capturing audio'
    return 'Idle · waiting for input'
})

const statusClass = computed(() => {
    if (isProcessing.value) return 'status-processing'
    if (isRecording.value) return 'status-recording'
    return 'status-idle'
})

const recordingHint = computed(() => {
    if (isProcessing.value) return 'Recording stopped. Processing audio...'
    if (isRecording.value) return 'Recording in progress. Click to stop.'
    return 'Click to start recording'
})

// Methods
function showToast(message, type = 'info') {
    toast.value = { show: true, message, type }
    setTimeout(() => {
        toast.value.show = false
    }, 3000)
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        mediaStream = stream
        recordedChunks = []

        mediaRecorder = new MediaRecorder(stream)

        mediaRecorder.ondataavailable = (event) => {
            if (event.data && event.data.size > 0) {
                recordedChunks.push(event.data)
            }
        }

        mediaRecorder.onstop = async () => {
            mediaStream?.getTracks().forEach(t => t.stop())
            mediaStream = null
            isRecording.value = false
            isProcessing.value = true

            try {
                const blob = new Blob(recordedChunks, { type: 'audio/webm' })
                const file = new File([blob], `recording-${Date.now()}.webm`, { type: blob.type })
                await uploadFile(file)
            } catch (err) {
                console.error(err)
                showToast('Failed to process recording', 'error')
            } finally {
                isProcessing.value = false
            }
        }

        mediaRecorder.start()
        isRecording.value = true
        showToast('Recording started', 'success')
    } catch (err) {
        console.error(err)
        showToast('Cannot access microphone', 'error')
    }
}

function stopRecording() {
    if (mediaRecorder) {
        mediaRecorder.stop()
        mediaRecorder = null
    }
}

function toggleRecording() {
    if (isProcessing.value) return
    if (!isRecording.value) {
        startRecording()
    } else {
        stopRecording()
    }
}

async function uploadFile(file) {
    isProcessing.value = true
    segments.value = []
    fullText.value = ''
    language.value = null

    try {
        const formData = new FormData()
        formData.append('file', file)

        const response = await fetch(`${API_BASE}/transcribe`, {
            method: 'POST',
            body: formData
        })

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.status}`)
        }

        const result = await response.json()

        // Update state
        language.value = result.language
        fullText.value = result.text
        segments.value = result.segments || []
        model.value = result.model
        device.value = result.device

        showToast(`Transcription complete: ${segments.value.length} segments`, 'success')
    } catch (err) {
        console.error(err)
        showToast(err.message || 'Upload failed', 'error')
    } finally {
        isProcessing.value = false
    }
}

function onFileChange(event) {
    const file = event.target.files?.[0]
    if (file) {
        uploadFile(file)
    }
}

async function fetchLatest() {
    try {
        const response = await fetch(`${API_BASE}/transcripts/latest`)
        if (response.ok) {
            latestTranscript.value = await response.json()
        } else if (response.status === 404) {
            latestTranscript.value = null
        }
    } catch (err) {
        console.error('Failed to fetch latest:', err)
    }
}

function loadLatestTranscript() {
    if (latestTranscript.value) {
        segments.value = latestTranscript.value.segments || []
        fullText.value = latestTranscript.value.text || ''
        language.value = latestTranscript.value.language
        model.value = latestTranscript.value.model
        device.value = latestTranscript.value.device
        showToast('Loaded latest transcript', 'success')
    }
}

function formatDate(dateStr) {
    if (!dateStr) return 'N/A'
    return new Date(dateStr).toLocaleString()
}

function downloadTranscript() {
    const data = {
        language: language.value,
        text: fullText.value,
        segments: segments.value
    }
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `transcript-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
}

// Lifecycle
onMounted(() => {
    fetchLatest()
})
</script>

<style scoped>
.toast {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    padding: 1rem 1.5rem;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 0.5rem;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    z-index: 1000;
    animation: slideIn 0.3s ease-out;
}

.toast.success {
    border-color: #10b981;
}

.toast.error {
    border-color: #ef4444;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }

    to {
        transform: translateX(0);
        opacity: 1;
    }
}
</style>
