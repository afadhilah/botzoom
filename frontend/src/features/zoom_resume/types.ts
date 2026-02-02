/**
 * TypeScript types for Transcript feature.
 * Matches backend schemas.
 */

export type TranscriptStatus = 'PENDING' | 'PROCESSING' | 'DONE' | 'FAILED'

export interface TranscriptSegment {
    id: number
    start: number
    end: number
    text: string
    speaker: string
}

export interface Transcript {
    id: number
    user_id: number
    audio_url: string
    status: TranscriptStatus
    language: string | null
    full_text: string | null
    segments: TranscriptSegment[] | null
    error_message: string | null
    created_at: string
    updated_at: string
}

export interface TranscriptStatusResponse {
    id: number
    status: TranscriptStatus
    error_message: string | null
}

export interface TranscriptListResponse {
    total: number
    items: Transcript[]
    skip: number
    limit: number
}
