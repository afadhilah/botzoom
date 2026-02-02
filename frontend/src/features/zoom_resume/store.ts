/**
 * Pinia store for Transcript feature.
 * Single source of truth for transcript state.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { transcriptApi } from './api'
import type { TranscriptSegment, Transcript } from './types'

export const useTranscriptStore = defineStore('transcript', () => {
    // State - Single transcript (for TranscriptMeeting.vue)
    const segments = ref<TranscriptSegment[]>([])
    const fullText = ref<string>('')
    const language = ref<string | null>(null)

    // State - Transcript list (for TranscriptList.vue)
    const transcripts = ref<Transcript[]>([])
    const currentTranscript = ref<Transcript | null>(null)
    const total = ref(0)
    const skip = ref(0)
    const limit = ref(20)

    // Shared state
    const loading = ref(false)
    const error = ref<string | null>(null)

    // Actions - Upload (existing)
    async function uploadAudio(file: File): Promise<boolean> {
        loading.value = true
        error.value = null

        try {
            const result = await transcriptApi.transcribeAudio(file)

            // Check if we got a transcript_id (async mode)
            if (result.transcript_id) {
                const transcriptId = result.transcript_id

                // Poll for status updates
                const pollInterval = setInterval(async () => {
                    try {
                        const transcript = await transcriptApi.fetchTranscriptById(transcriptId)

                        if (transcript.status === 'DONE') {
                            clearInterval(pollInterval)

                            // Update state with results
                            language.value = transcript.language
                            fullText.value = transcript.full_text || ''
                            segments.value = transcript.segments || []

                            loading.value = false
                            return // Exit polling
                        } else if (transcript.status === 'FAILED') {
                            clearInterval(pollInterval)
                            error.value = transcript.error_message || 'Transcription failed'
                            loading.value = false
                            return // Exit polling
                        }
                        // Continue polling if PENDING or PROCESSING
                    } catch (err: any) {
                        clearInterval(pollInterval)
                        error.value = err.message || 'Failed to check status'
                        loading.value = false
                    }
                }, 2000) // Poll every 2 seconds

                return true
            } else {
                // Legacy synchronous response (if backend returns full result)
                language.value = result.language
                fullText.value = result.text
                segments.value = result.segments
                loading.value = false
                return true
            }
        } catch (err: any) {
            error.value = err.message || 'Failed to transcribe audio'
            console.error('Transcription error:', err)
            loading.value = false
            return false
        }
    }

    // Actions - List management
    async function loadTranscriptList() {
        loading.value = true
        error.value = null

        try {
            const response = await transcriptApi.fetchTranscripts(skip.value, limit.value)
            transcripts.value = response.items
            total.value = response.total
        } catch (err: any) {
            error.value = err.message || 'Failed to load transcripts'
            console.error('Load transcripts error:', err)
        } finally {
            loading.value = false
        }
    }

    async function selectTranscript(id: number) {
        loading.value = true
        error.value = null

        try {
            currentTranscript.value = await transcriptApi.fetchTranscriptById(id)
        } catch (err: any) {
            error.value = err.message || 'Failed to load transcript'
            console.error('Select transcript error:', err)
        } finally {
            loading.value = false
        }
    }

    async function refreshTranscriptStatus(id: number) {
        try {
            const updated = await transcriptApi.fetchTranscriptById(id)
            const index = transcripts.value.findIndex(t => t.id === id)
            if (index !== -1) {
                transcripts.value[index] = updated
            }
            if (currentTranscript.value?.id === id) {
                currentTranscript.value = updated
            }
        } catch (err) {
            console.error('Failed to refresh status:', err)
        }
    }

    function clearTranscript() {
        segments.value = []
        fullText.value = ''
        language.value = null
        error.value = null
    }

    function clearError() {
        error.value = null
    }

    return {
        // State - Single transcript
        segments,
        fullText,
        language,

        // State - List
        transcripts,
        currentTranscript,
        total,
        skip,
        limit,

        // Shared state
        loading,
        error,

        // Actions
        uploadAudio,
        loadTranscriptList,
        selectTranscript,
        refreshTranscriptStatus,
        clearTranscript,
        clearError
    }
})
