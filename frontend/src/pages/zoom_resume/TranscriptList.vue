<script lang="ts">
export const iframeHeight = "800px"
export const description = "A dashboard with sidebar, data table, and analytics cards."
</script>

<script setup lang="ts">
import { onMounted, onUnmounted, computed, ref } from 'vue'
import { useTranscriptStore } from '@/features/zoom_resume/store'
import type { Transcript } from '@/features/zoom_resume/types'

import DataTable from "@/components/DataTable.vue"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Play, Download } from "lucide-vue-next"
import { transcriptApi } from '@/features/zoom_resume/api'

const transcriptStore = useTranscriptStore()


// ===== STATE =====
const isDialogOpen = ref(false)
const selectedTranscript = ref<Transcript | null>(null)
const latestZoomTranscript = ref<Transcript | null>(null)
const isDeleteDialogOpen = ref(false)
const transcriptToDelete = ref<Transcript | null>(null)
const isDeleting = ref(false)

// polling holder
let pollInterval: number | null = null

// ===== FETCH LATEST ZOOM TRANSCRIPT =====
async function loadLatestZoomTranscript() {
  try {
    const res = await transcriptApi.fetchLatestZoomTranscript()
    latestZoomTranscript.value = res
  } catch (err) {
    console.error('Failed to load latest zoom transcript', err)
  }
}

// ===== STATUS MAP =====
const statusMap: Record<string, string> = {
  PENDING: 'Pending',
  PROCESSING: 'In Process',
  DONE: 'Done',
  FAILED: 'Failed'
}

// ===== TABLE DATA =====
const data = computed(() => {
  return transcriptStore.transcripts.map(t => {
    const createdDate = new Date(t.created_at)
    const formattedDate = createdDate.toLocaleDateString('id-ID', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })

    return {
      id: t.id,
      header: `Transcript #${t.id}`,
      type: t.language || 'Auto detect',
      status: statusMap[t.status] || t.status,
      target: formattedDate,
      limit: t.segments?.length.toString() || '0',
      reviewer: t.error_message || '-',
      onHeaderClick: () => handleRowClick({ id: t.id }),
      onDelete: () => confirmDelete(t)
    }
  })
})

// ===== CLICK HANDLER =====
function handleRowClick(row: any) {
  const transcript = transcriptStore.transcripts.find(t => t.id === row.id)
  if (transcript) {
    selectedTranscript.value = transcript
    isDialogOpen.value = true
  }
}

// ===== DELETE HANDLER =====
function confirmDelete(transcript: Transcript) {
  transcriptToDelete.value = transcript
  isDeleteDialogOpen.value = true
}

async function handleDelete() {
  if (!transcriptToDelete.value) return
  
  isDeleting.value = true
  try {
    await transcriptApi.deleteTranscript(transcriptToDelete.value.id)
    
    // Remove from store
    await transcriptStore.loadTranscriptList()
    
    // Close dialogs
    isDeleteDialogOpen.value = false
    isDialogOpen.value = false
    
    console.log(`Deleted transcript #${transcriptToDelete.value.id}`)
  } catch (err) {
    console.error('Failed to delete transcript:', err)
    alert('Failed to delete transcript. Please try again.')
  } finally {
    isDeleting.value = false
    transcriptToDelete.value = null
  }
}

// ===== HELPERS =====
function formatTimestamp(seconds: number): string {
  return `${seconds.toFixed(1)}s`
}

function formatTimeRange(start: number, end: number): string {
  return `${start.toFixed(1)} – ${end.toFixed(1)}s`
}

// ===== LIFECYCLE =====
onMounted(() => {
  transcriptStore.loadTranscriptList()
  loadLatestZoomTranscript()

  pollInterval = setInterval(() => {
    transcriptStore.transcripts
      .filter(t => t.status === 'PENDING' || t.status === 'PROCESSING')
      .forEach(t => transcriptStore.refreshTranscriptStatus(t.id))

    loadLatestZoomTranscript()
  }, 5000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<template>
  <SidebarProvider
    :style="{
      '--sidebar-width': 'calc(var(--spacing) * 72)',
      '--header-height': 'calc(var(--spacing) * 12)'
    }"
  >
    <SidebarInset>
      <div class="flex flex-1 flex-col">
        <div class="@container/main flex flex-1 flex-col gap-2">
          <div class="flex flex-col gap-4 py-4 md:gap-6 md:py-6">

            <!-- LATEST ZOOM TRANSCRIPT CARD -->
            <div v-if="latestZoomTranscript" class="p-4 border rounded-lg mb-4">
              <p class="text-sm text-muted-foreground mb-1">
                Latest Zoom Transcript:
              </p>

              <Button
                variant="outline"
                @click="() => {
                  selectedTranscript = latestZoomTranscript
                  isDialogOpen = true
                }"
              >
                Open Latest Zoom Transcript (ID: {{ latestZoomTranscript.id }})
              </Button>
            </div>

            <DataTable :data="data" />
          </div>
        </div>
      </div>
    </SidebarInset>
  </SidebarProvider>

  <!-- TRANSCRIPT DETAIL DIALOG -->
  <Dialog v-model:open="isDialogOpen">
    <DialogContent class="max-w-4xl max-h-[90vh] p-8">
      <DialogHeader>
        <DialogTitle>Transcript Detail</DialogTitle>
        <DialogDescription>
          Detail hasil transkripsi meeting yang dipilih.
        </DialogDescription>
      </DialogHeader>

      <div v-if="selectedTranscript" class="space-y-4">

        <!-- META -->
        <div class="grid grid-cols-3 gap-4 text-sm">
          <div>
            <p class="text-muted-foreground text-xs">Total Segments</p>
            <p class="font-medium">
              {{ selectedTranscript.segments?.length || 0 }}
            </p>
          </div>

          <div>
            <p class="text-muted-foreground text-xs">Language</p>
            <p class="font-medium">
              {{ selectedTranscript.language || 'Auto detect' }}
            </p>
          </div>

          <div>
            <p class="text-muted-foreground text-xs">Status</p>
            <Badge :variant="selectedTranscript.status === 'DONE' ? 'default' : 'secondary'">
              {{ statusMap[selectedTranscript.status] || selectedTranscript.status }}
            </Badge>
          </div>
        </div>

        <Separator />

        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold">Transcript</h2>

          <Button @click="loadLatestZoomTranscript">
            Load Latest Zoom Transcript
          </Button>
        </div>

        <!-- TABS -->
        <Tabs default-value="transcript" class="w-full">
          <TabsList class="grid w-full grid-cols-2">
            <TabsTrigger value="transcript">Transcript</TabsTrigger>
            <TabsTrigger value="summary">Summary</TabsTrigger>
          </TabsList>

          <!-- TRANSCRIPT -->
          <TabsContent value="transcript" class="mt-4">
            <ScrollArea class="h-[400px] pr-4">
              <div
                v-if="!selectedTranscript.segments || selectedTranscript.segments.length === 0"
                class="text-center text-muted-foreground py-10"
              >
                No transcript segments available.
              </div>

              <div v-else class="space-y-3 px-2">
                <div
                  v-for="seg in selectedTranscript.segments"
                  :key="seg.id"
                  class="flex gap-3 items-start border-b border-border/60 pb-3 last:border-b-0"
                >
                  <div class="w-14 pt-1 text-xs text-muted-foreground tabular-nums">
                    {{ formatTimestamp(seg.start) }}
                  </div>

                  <div class="flex-1 space-y-1">
                    <div class="flex items-center gap-2">
                      <Badge variant="outline" class="text-xs">
                        {{ seg.speaker }}
                      </Badge>
                      <span class="text-xs text-muted-foreground">
                        {{ formatTimeRange(seg.start, seg.end) }}
                      </span>
                    </div>

                    <p class="text-sm leading-relaxed">
                      {{ seg.text }}
                    </p>
                  </div>

                  <Button size="icon" variant="ghost" class="h-7 w-7 shrink-0">
                    <Play class="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </ScrollArea>
          </TabsContent>

          <!-- SUMMARY -->
          <TabsContent value="summary" class="mt-4">
            <ScrollArea class="h-[400px] pr-4">
              <div class="space-y-2 text-sm">
                <p class="font-medium">Full Text Summary:</p>
                <p class="leading-relaxed text-muted-foreground">
                  {{ selectedTranscript.full_text || 'No summary available.' }}
                </p>
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="isDialogOpen = false">
          Close
        </Button>
        <Button variant="default">
          <Download class="h-4 w-4 mr-2" />
          Download
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>

  <!-- DELETE CONFIRMATION DIALOG -->
  <Dialog v-model:open="isDeleteDialogOpen">
    <DialogContent class="max-w-md">
      <DialogHeader>
        <DialogTitle>Delete Transcript?</DialogTitle>
        <DialogDescription>
          Are you sure you want to delete this transcript? This action cannot be undone.
          All associated files will be permanently deleted.
        </DialogDescription>
      </DialogHeader>

      <div v-if="transcriptToDelete" class="space-y-2 text-sm">
        <p><strong>Transcript ID:</strong> #{{ transcriptToDelete.id }}</p>
        <p><strong>Language:</strong> {{ transcriptToDelete.language || 'Auto detect' }}</p>
        <p><strong>Segments:</strong> {{ transcriptToDelete.segments?.length || 0 }}</p>
      </div>

      <DialogFooter>
        <Button 
          variant="outline" 
          @click="isDeleteDialogOpen = false"
          :disabled="isDeleting"
        >
          Cancel
        </Button>
        <Button 
          variant="destructive" 
          @click="handleDelete"
          :disabled="isDeleting"
        >
          {{ isDeleting ? 'Deleting...' : 'Delete' }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
