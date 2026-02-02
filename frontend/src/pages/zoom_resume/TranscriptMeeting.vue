<!-- src/pages/TranscriptMeeting.vue -->
<script setup lang="ts">
import { ref, computed } from "vue"
import { useTranscriptStore } from '@/features/zoom_resume/store'

import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from "@/components/ui/tabs"
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
// import { Toaster } from "@/components/ui/sonner"
import { toast } from "vue-sonner"
import { Play } from "lucide-vue-next"

// Initialize transcript store
const transcriptStore = useTranscriptStore()

import { onMounted } from 'vue'
import type { Transcript } from '@/features/zoom_resume/types'
import { transcriptApi } from '@/features/zoom_resume/api'


const latestZoomTranscript = ref<Transcript | null>(null)
const zoomMeetingLink = ref('')
const isJoiningZoom = ref(false)

const props = defineProps<{
  isDialogOpen: boolean
  selectedTranscript: Transcript | null
}>()

const emit = defineEmits<{
  (e: 'update:isDialogOpen', value: boolean): void
  (e: 'update:selectedTranscript', value: Transcript | null): void
}>()

async function loadLatestZoomTranscript() {
  try {
    const res = await transcriptApi.fetchLatestZoomTranscript()
    latestZoomTranscript.value = res
  } catch (err) {
    console.error('Failed to load latest zoom transcript', err)
  }
}

async function joinZoomMeeting() {
  if (!zoomMeetingLink.value) return
  
  isJoiningZoom.value = true
  try {
    await transcriptApi.joinZoomMeeting(zoomMeetingLink.value)
    
    toast.success('Bot joining meeting', {
      description: 'Zoom bot is joining the meeting and will start recording.',
    })
    
    // Clear input
    zoomMeetingLink.value = ''
    
    // Reload latest transcript after a delay
    setTimeout(() => {
      loadLatestZoomTranscript()
    }, 5000)
  } catch (err: any) {
    console.error('Failed to join Zoom meeting', err)
    toast.error('Failed to join meeting', {
      description: err?.message || 'Could not start Zoom bot',
    })
  } finally {
    isJoiningZoom.value = false
  }
}

onMounted(() => {
  loadLatestZoomTranscript()
})


// const isRecording = ref(false)
// const recordingLabel = computed(() =>
//   isRecording.value ? "Stop recording" : "Start recording"
// )

// const recordingHint = computed(() =>
//   isRecording.value
//     ? "Recording in progress. Click to stop and send audio to backend."
//     : "Ready when you are. Click to start capturing your meeting audio."
// )

// const statusText = computed(() =>
//   isRecording.value ? "Live · capturing audio" : "Idle · waiting for input"
// )

// const statusColor = computed(() =>
//   isRecording.value ? "bg-emerald-500" : "bg-slate-300"
// )

// const toggleRecording = () => {
//   // TODO: sambungin ke MediaRecorder / API
//   isRecording.value = !isRecording.value
// }

const audioUrl = ref<string | null>(null)
const audioRef = ref<HTMLAudioElement | null>(null)

// simpan URL audio setiap kali ada file baru (upload / record)
function setAudioSourceFromFile(file: File) {
  if (audioUrl.value) {
    URL.revokeObjectURL(audioUrl.value)
  }
  audioUrl.value = URL.createObjectURL(file)
}

const isRecording = ref(false)
const isProcessingRecording = ref(false)

const recordingHint = computed(() => {
  if (isProcessingRecording.value) {
    return "Recording stopped. Processing audio and sending to backend..."
  }
  return isRecording.value
    ? "Recording in progress. Click to stop and send audio to backend."
    : "Ready when you are. Click to start capturing your meeting audio."
})

const statusText = computed(() => {
  if (isProcessingRecording.value) return "Processing · transcribing audio"
  return isRecording.value ? "Live · capturing audio" : "Idle · waiting for input"
})

const statusColor = computed(() => {
  if (isProcessingRecording.value) return "bg-amber-400"
  return isRecording.value ? "bg-emerald-500" : "bg-slate-300"
})

// --- MediaRecorder state ---
const mediaRecorder = ref<MediaRecorder | null>(null)
const mediaStream = ref<MediaStream | null>(null)
let recordedChunks: BlobPart[] = []

async function startRecording() {
  try {
    if (!("mediaDevices" in navigator) || !navigator.mediaDevices.getUserMedia) {
      toast.error("Recording not supported", {
        description: "Browser ini tidak mendukung audio recording.",
      })
      return
    }

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaStream.value = stream

    recordedChunks = []
    const recorder = new MediaRecorder(stream)
    mediaRecorder.value = recorder

    recorder.ondataavailable = (event: BlobEvent) => {
      if (event.data && event.data.size > 0) {
        recordedChunks.push(event.data)
      }
    }

    recorder.onstop = async () => {
      // stop semua track mic
      mediaStream.value?.getTracks().forEach((t) => t.stop())
      mediaStream.value = null
      isRecording.value = false
      isProcessingRecording.value = true

      try {
        const blob = new Blob(recordedChunks, { type: "audio/webm" })
        const file = new File(
          [blob],
          `meeting-recording-${Date.now()}.webm`,
          { type: blob.type }
        )

        // pakai pipeline yang sama dengan upload file biasa
        setAudioSourceFromFile(file)
        await uploadFile(file)
      } catch (err: any) {
        console.error(err)
        toast.error("Failed to process recording", {
          description: err?.message ?? "Unknown error",
        })
      } finally {
        isProcessingRecording.value = false
      }
    }

    recorder.start()
    isRecording.value = true

    toast.success("Recording started", {
      description: "Mic is now capturing meeting audio.",
    })
  } catch (err: any) {
    console.error(err)
    toast.error("Cannot start recording", {
      description:
        err?.name === "NotAllowedError"
          ? "Permission untuk mikrofon ditolak."
          : err?.message ?? "Unknown error",
    })
  }
}

function stopRecording() {
  if (!mediaRecorder.value) return
  try {
    mediaRecorder.value.stop()
    mediaRecorder.value = null
  } catch (err) {
    console.error(err)
  }
}

const toggleRecording = () => {
  if (isProcessingRecording.value) return
  if (!isRecording.value) {
    void startRecording()
  } else {
    stopRecording()
  }
}

// const segments = ref([
//   {
//     id: 1,
//     start: "00:01",
//     end: "00:18",
//     speaker: "Speaker 1",
//     text: "Oke, kita mulai meeting hari ini. Fokus ke progres integrasi Zoom dan pipeline WhisperX.",
//   },
//   {
//     id: 2,
//     start: "00:19",
//     end: "00:42",
//     speaker: "Speaker 2",
//     text: "Dari sisi backend, webhook sudah stabil. Yang perlu kita rapikan tinggal handler untuk error saat download rekaman.",
//   },
//   {
//     id: 3,
//     start: "00:43",
//     end: "01:05",
//     speaker: "Speaker 1",
//     text: "Sip. Untuk frontend, kita butuh tampilan transcript yang enak dibaca dan mudah dicari keyword-nya.",
//   },
// ])

interface TranscriptSegment {
  id: number
  start: number
  end: number
  speaker: string
  text: string
}

const isUploading = ref(false)
const segments = ref<TranscriptSegment[]>([])
const fullText = ref("")
const language = ref<string | null>(null)
const model = ref<string | null>(null)
const device = ref<string | null>(null)

// Language code to display name mapping
const languageMap: Record<string, string> = {
  'id': 'Indonesian',
  'indonesian': 'Indonesian',
  'en': 'English',
  'english': 'English',
  'zh': 'Chinese',
  'chinese': 'Chinese',
  'ja': 'Japanese',
  'japanese': 'Japanese',
  'ko': 'Korean',
  'korean': 'Korean',
  'es': 'Spanish',
  'spanish': 'Spanish',
  'fr': 'French',
  'french': 'French',
  'de': 'German',
  'german': 'German',
  'ar': 'Arabic',
  'arabic': 'Arabic',
}

const displayLanguage = computed(() => {
  if (!language.value) return 'Auto detect'
  return languageMap[language.value.toLowerCase()] || language.value
})

const fileInput = ref<HTMLInputElement | null>(null)

async function uploadFile(file: File): Promise<void> {
  setAudioSourceFromFile(file)
  isUploading.value = true
  
  // Clear previous results
  language.value = null
  fullText.value = ""
  segments.value = []
  
  try {
    // Use transcript store (now with async polling)
    const success = await transcriptStore.uploadAudio(file)
    
    if (!success) {
      throw new Error(transcriptStore.error || 'Transcription failed')
    }
    

    // Wait for polling to complete by watching store state
    const checkResults = setInterval(() => {
      if (!transcriptStore.loading) {
        clearInterval(checkResults)
        
        // Update UI with results from store
        language.value = transcriptStore.language
        fullText.value = transcriptStore.fullText
        segments.value = transcriptStore.segments
        model.value = null
        device.value = null
        
        isUploading.value = false
        
        if (segments.value.length > 0) {
          toast({
            title: "Transcription completed",
            description: `${segments.value.length} segments loaded.`,
          })
        }
      }
    }, 500) // Check every 500ms
    
  } catch (err: any) {
    console.error(err)
    isUploading.value = false
    toast({
      title: "Upload failed",
      description: err?.message ?? transcriptStore.error ?? "Unknown error",
      variant: "destructive",
    })
  }
}


const onFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement | null
  if (!target?.files || target.files.length === 0) return

  const file = target.files[0]
  if (file) {
    uploadFile(file)
  }
}

const openFileDialog = () => {
  fileInput.value?.click()
}

function onPlaySegment(seg: TranscriptSegment) {
  if (!audioRef.value || !audioUrl.value) {
    toast.error("Audio tidak tersedia", {
      description: "Upload atau rekam audio dulu sebelum memutar segmen.",
    })
    return
  }

  const audio = audioRef.value

  // pastikan src sudah ter-set
  if (!audio.src || audio.src !== audioUrl.value) {
    audio.src = audioUrl.value
  }

  // lompat ke waktu mulai segmen
  audio.currentTime = seg.start

  // play
  void audio.play().catch((err) => {
    console.error(err)
    toast.error("Gagal memutar audio", {
      description: err?.message ?? "Unknown error",
    })
  })
}


import { InfoIcon } from 'lucide-vue-next'
import { InputGroup, InputGroupAddon, InputGroupButton, InputGroupInput, InputGroupText } from '@/components/ui/input-group'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { AudioLinesIcon } from 'lucide-vue-next'


</script>

<template>
  <audio ref="audioRef" class="hidden" />
  <div class="w-full h-full flex flex-col gap-6">
    <!-- MAIN CONTENT -->

    <div class="w-1/3 mx-auto flex items-center gap-2">
      <InputGroup>
        <InputGroupInput placeholder="example.com" class="!pl-1" />
        <InputGroupAddon>
          <InputGroupText>https://</InputGroupText>
        </InputGroupAddon>
        <InputGroupAddon align="inline-end">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger as-child>
                <InputGroupButton class="rounded-full" size="icon-xs">
                  <InfoIcon class="size-4" />
                </InputGroupButton>
              </TooltipTrigger>
              <TooltipContent>This is content in a tooltip.</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </InputGroupAddon>
      </InputGroup>
      <Button>Start</Button>
    </div>
    <Separator class="my-4" />
    <section
      class="grid gap-4 items-start lg:grid-cols-[minmax(0,360px)_minmax(0,1fr)]"
    >
      <!-- LEFT COLUMN: controls -->
      <div class="space-y-4">
        <!-- Mode: record / upload -->
        <Card>
          <CardHeader>
            <CardTitle class="text-sm">Input source</CardTitle>
            <CardDescription class="text-xs">
              Pilih cara memasukkan audio: rekam langsung atau unggah file.
            </CardDescription>
          </CardHeader>
           
          <CardContent class="pt-0">
           
            <Tabs default-value="record" class="w-full">
              <TabsList class="grid w-full grid-cols-3">
                <TabsTrigger value="record" class="text-xs">
                  Record
                </TabsTrigger>
                    <TabsTrigger value="latest" class="text-xs">
                  Zoom
                </TabsTrigger>
                <TabsTrigger value="upload" class="text-xs">
                  Upload file
                </TabsTrigger>
              </TabsList>

              <!-- TAB: RECORD -->
              <TabsContent value="record" class="space-y-4">
                <!-- <div class="flex items-center justify-center gap-2 text-xs">
                  <span
                    class="inline-flex h-2 w-2 rounded-full"
                    :class="statusColor"
                  />
                  <span class="text-muted-foreground">
                    {{ statusText }}
                  </span>
                </div> -->
                  <!-- <p class="text-[11px] text-muted-foreground leading-relaxed">
                    Sistem akan menyimpan audio sementara dan mengirimkannya
                    ke backend untuk diproses dengan WhisperX setelah rekaman
                    dihentikan.
                  </p> -->

                <div class="flex flex-col items-center justify-center gap-4 m-12">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger as-child>
                        <Button
                          :data-active="isRecording"
                          class="rounded-full size-32 data-[active=true]:bg-orange-100 data-[active=true]:text-orange-700 dark:data-[active=true]:bg-orange-800 dark:data-[active=true]:text-orange-100"
                          :aria-pressed="isRecording"
                          size="icon"
                          aria-label="Voice Mode"
                          @click="toggleRecording"
                        >
                          <AudioLinesIcon class="size-14" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Voice Mode</TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                  <div class="flex items-center justify-center gap-2 text-xs">
                    <span
                      class="inline-flex h-2 w-2 rounded-full"
                      :class="statusColor"
                    />
                    <span class="text-muted-foreground">
                      {{ statusText }}
                    </span>
                  </div>
                </div>

                <!-- <Button
                  class="mx-auto flex items-center text-sm"
                  :variant="isRecording ? 'destructive' : 'default'"
                  :disabled="isProcessingRecording"
                  type="button"
                  @click="toggleRecording"
                >
                <span v-if="isProcessingRecording">Processing recording...</span>
                <span v-else>{{ recordingLabel }}</span>
                </Button> -->



                <p class="text-[11px] text-muted-foreground">
                  {{ recordingHint }}
                </p>
              </TabsContent>
               <TabsContent value="latest" class="mt-4 space-y-3">
    <div class="space-y-2">
      <label class="text-sm font-medium">Zoom Meeting Link or ID</label>
      <div class="flex gap-2">
        <input
          v-model="zoomMeetingLink"
          type="text"
          placeholder="https://zoom.us/j/123456789 or 123456789"
          class="flex-1 px-3 py-2 text-sm border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
        />
        <Button
          @click="joinZoomMeeting"
          :disabled="isJoiningZoom || !zoomMeetingLink"
        >
          {{ isJoiningZoom ? 'Joining...' : 'Join' }}
        </Button>
      </div>
      <p class="text-xs text-muted-foreground">
        Bot akan otomatis join ke meeting dan merekam audio untuk ditranskripsi.
      </p>
    </div>

    <Separator class="my-3" />

    <div v-if="latestZoomTranscript" class="p-4 border rounded-lg">
      <p class="text-sm text-muted-foreground mb-2">
        Latest Zoom Transcript
      </p>

      <Button
        variant="outline"
        @click="
          () => {
            emit('update:selectedTranscript', latestZoomTranscript!)
            emit('update:isDialogOpen', true)
          }
        "
      >
        Open Latest Zoom Transcript (ID: {{ latestZoomTranscript?.id }})
      </Button>
    </div>

    <div v-else class="text-sm text-muted-foreground text-center py-4">
      Belum ada transcript Zoom terbaru
    </div>
  </TabsContent>
              <!-- TAB: UPLOAD -->
              <TabsContent value="upload" class="mt-4 space-y-3">
                <div
                  class="border border-dashed border-muted-foreground/40 rounded-lg px-4 py-6 text-center space-y-2"
                >
                  <p class="text-xs font-medium">
                    Drag &amp; drop file audio di sini
                  </p>
                  <p class="text-[11px] text-muted-foreground">
                    Mendukung format mp3, wav, m4a. Durasi disarankan &lt; 2 jam.
                  </p>
                  <input
                    type="file"
                    accept="audio/*"
                    class="hidden"
                    ref="fileInput"
                    @change="onFileChange"
                  />
                  <Button
                    size="sm"
                    class="rounded-full text-xs mt-1"
                    variant="outline"
                    @click="openFileDialog"
                  >
                    Pilih file dari perangkat
                  </Button>

                </div>
                <p class="text-[11px] text-muted-foreground">
                  Setelah diunggah, file akan diantrikan untuk proses
                  transkripsi dan muncul di panel preview.
                </p>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <!-- Small info card -->
        <Card>
          <CardHeader>
            <CardTitle class="text-sm">Processing profile</CardTitle>
          </CardHeader>
          <CardContent class="space-y-2 text-[11px]">
            <div class="flex justify-between">
              <span class="text-muted-foreground">Engine</span>
              <span class="font-medium">
                {{ model ? `Whisper · ${model}` : 'Whisper · base' }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">Speaker diarization</span>
              <span class="font-medium">Disabled</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">Language</span>
              <span class="font-medium">{{ displayLanguage }}</span>
            </div>
            <div v-if="device" class="flex justify-between">
              <span class="text-muted-foreground">Device</span>
              <span class="font-medium">{{ device.toUpperCase() }}</span>
            </div>
          </CardContent>
          <CardFooter class="pt-1">
            <p class="text-[11px] text-muted-foreground">
              Pengaturan ini nanti bisa diubah di halaman settings pipeline.
            </p>
          </CardFooter>
        </Card>
      </div>

      <!-- RIGHT COLUMN: transcript preview -->
      <Card class="flex flex-col">
        <CardHeader>
          <div class="flex items-center justify-between gap-2">
            <div>
              <CardTitle class="text-sm">Transcript</CardTitle>
              <CardDescription class="text-xs">
                Hasil transkripsi meeting terakhir / aktif.
              </CardDescription>
            </div>
            <Button size="icon" variant="ghost" class="h-8 w-8">
              ⋮
            </Button>
          </div>
        </CardHeader>

        <Separator />

        <CardContent class="p-0 flex-1 overflow-hidden">
          <Tabs default-value="transcript" class="h-full flex flex-col">
            <div class="flex items-center justify-between px-5 pt-3 pb-2">
              <TabsList class="h-8">
                <TabsTrigger value="transcript" class="text-xs">
                  Transcript
                </TabsTrigger>
                <TabsTrigger value="summary" class="text-xs">
                  Summary
                </TabsTrigger>
              </TabsList>

              <Button size="sm" variant="outline" class="text-xs rounded-full">
                Download
              </Button>
            </div>

            <!-- TAB: TRANSCRIPT LIST -->
            <TabsContent value="transcript" class="px-5 pb-4 flex-1 overflow-hidden">
              <ScrollArea class="h-full pr-3">
                <div class="space-y-3">
                  <div
                    v-if="segments.length === 0"
                    class="text-sm text-muted-foreground text-center py-10"
                  >
                    Belum ada transcript. Upload file audio dulu di panel atas.
                  </div>

                  <div
                    v-for="seg in segments"
                    :key="seg.id"
                    class="flex gap-3 items-start border-b border-border/60 pb-3 last:border-b-0"
                  >
                    <!-- timestamp kiri -->
                    <div class="w-14 pt-1 text-[11px] text-muted-foreground tabular-nums">
                      {{ seg.start.toFixed(1) }}s
                    </div>

                    <!-- konten utama -->
                    <div class="flex-1 space-y-1">
                      <div class="flex items-center gap-2">
                        <Badge variant="outline" class="text-[11px]">
                          {{ seg.speaker }}
                        </Badge>
                        <span class="text-[11px] text-muted-foreground">
                          {{ seg.start.toFixed(1) }} – {{ seg.end.toFixed(1) }}s
                        </span>
                      </div>
                      <p class="text-sm leading-relaxed">
                        {{ seg.text }}
                      </p>
                    </div>

                    <!-- tombol play (belum di-wire ke audio, tapi siap) -->
                    <Button
                      size="icon"
                      variant="ghost"
                      class="h-7 w-7 shrink-0"
                      type="button"
                      @click="onPlaySegment(seg)"
                    >
                      <Play class="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </ScrollArea>
            </TabsContent>


            <!-- TAB: SUMMARY -->
            <TabsContent value="summary" class="px-5 pb-4 flex-1 overflow-auto">
              <div class="space-y-2 text-sm text-muted-foreground">
                <p class="font-medium text-foreground">
                  Ringkasan singkat:
                </p>
                <p class="leading-relaxed text-foreground">
                  {{ fullText }}
                </p>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>

        <CardFooter
          class="border-t px-5 flex items-center justify-between"
        >
          <p class="text-[11px] text-muted-foreground">
            Terakhir diperbarui: belum ada proses otomatis.
          </p>
          <Button size="sm" variant="outline" class="text-xs rounded-full">
            Refresh
          </Button>
        </CardFooter>
      </Card>

    </section>
  </div>
</template>
