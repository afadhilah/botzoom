/**
 * API client for Transcript feature.
 * Uses native Fetch API with token injection.
 */
import { http } from '@/services/http'
import API_CONFIG from '@/services/config'
import type { Transcript, TranscriptStatusResponse, TranscriptListResponse } from './types'

const BASE_URL = API_CONFIG.baseURL

export const transcriptApi = {
    /**
     * Upload audio file for transcription (legacy endpoint).
     * Returns immediate result (synchronous) or transcript_id (async).
     */
    async transcribeAudio(file: File): Promise<{
        transcript_id?: number
        status?: string
        message?: string
        language: string | null
        text: string
        segments: Array<{
            id: number
            start: number
            end: number
            text: string
            speaker: string
        }>
        model?: string
        device?: string
    }> {
        const formData = new FormData()
        formData.append('file', file)

        // Get auth token from localStorage
        const token = localStorage.getItem('access_token')

        const response = await fetch(`${BASE_URL}/transcribe`, {
            method: 'POST',
            body: formData,
            headers: {
                ...(token ? { 'Authorization': `Bearer ${token}` } : {})
            }
        })

        if (!response.ok) {
            const error = await response.text()
            throw new Error(`Backend error: ${response.status} ${error}`)
        }

        return response.json()
    },

    /**
     * Fetch paginated list of transcripts for current user.
     */
    async fetchTranscripts(skip: number = 0, limit: number = 20): Promise<TranscriptListResponse> {
        return await http.get<TranscriptListResponse>(`/transcripts?skip=${skip}&limit=${limit}`)
    },
    async fetchLatestZoomTranscript(): Promise<Transcript> {
    return await http.get<Transcript>('/transcripts/latest')
},

    /**
     * Join Zoom meeting with bot.
     */
    async joinZoomMeeting(meetingLink: string): Promise<{ message: string, bot_id: string }> {
        return await http.post<{ message: string, bot_id: string }>('/zoom/join', {
            meeting_link: meetingLink
        })
    },

    /**
     * End Zoom bot session.
     */
    async endZoomBot(botId: string): Promise<{ 
        message: string
        bot_id: string
        pid: number
        transcript?: {
            status: string
            transcript_id: number
            language?: string
            segments_count?: number
            error?: string
        }
    }> {
        return await http.post('/zoom/end', {
            bot_id: botId
        })
    },

    /**
     * Fetch single transcript by ID.
     */
    async fetchTranscriptById(id: number): Promise<Transcript> {
        return await http.get<Transcript>(`/transcripts/${id}`)
    },

    /**
     * Check transcript processing status.
     */
    async checkStatus(id: number): Promise<TranscriptStatusResponse> {
        return await http.get<TranscriptStatusResponse>(`/transcripts/${id}/status`)
    }
}
