<script setup lang="ts">
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"

import {
  Activity,
  MessageCircle,
  AlertCircle,
  Clock,
  Repeat,
  HelpCircle,
  Target,
  Map,
  Sparkles,
  Search,
} from "lucide-vue-next"

const changedSummary = {
  decisions: 3,
  unresolved: 2,
  recurring: 1,
}

const flowNodes = [
  {
    id: 1,
    label: "Weekly Planning",
    topic: "Budget approval",
    highlight: true,
  },
  {
    id: 2,
    label: "Project Sync",
    topic: "Hiring backend",
  },
  {
    id: 3,
    label: "Risk Review",
    topic: "Vendor issue",
  },
  {
    id: 4,
    label: "Steering Committee",
    topic: "Budget approval",
    highlight: true,
  },
]

const unfinished = [
  {
    topic: "Budget approval",
    meetings: 3,
    note: "Belum ada keputusan final",
    tag: "High impact",
  },
  {
    topic: "Hiring backend engineer",
    meetings: 2,
    note: "Sering dibahas, belum ada owner",
    tag: "No owner",
  },
]

const speakerInsight = {
  mainSpeaker: "Speaker 1",
  ratio: "70%",
  text: "Dalam 5 meeting terakhir, mayoritas keputusan muncul dari 1 pembicara.",
}

const meetingSmell = {
  score: 72,
  level: "Needs attention",
  badges: [
    {
      icon: Clock,
      label: "Too long, low output",
    },
    {
      icon: Repeat,
      label: "Repetitive topics",
    },
    {
      icon: HelpCircle,
      label: "Many questions, no answers",
    },
    {
      icon: Target,
      label: "Some clear decisions",
    },
  ],
}

const knowledgeMap = {
  topics: [
    { label: "Budget", count: 4 },
    { label: "Hiring", count: 3 },
    { label: "Vendor", count: 2 },
    { label: "Roadmap", count: 3 },
  ],
}

// const todaysHighlights = [
//   "Budget approval hampir final, tinggal konfirmasi satu stakeholder.",
//   "Risiko keterlambatan vendor mulai naik dan perlu mitigasi.",
//   "Ada usulan restrukturisasi agenda meeting agar lebih fokus keputusan.",
// ]
</script>

<template>
  <div class="w-full h-full flex flex-col gap-6">
    <!-- HEADER -->
    <section class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-2xl md:text-3xl font-semibold tracking-tight">
          Dashboard
        </h1>
      </div>

      <div class="hidden md:flex items-center gap-2">
        <Button variant="outline" size="sm" class="text-xs">
          Export snapshot
        </Button>
        <Button size="sm" class="text-xs">
          Go to transcript workspace
        </Button>
      </div>
    </section>

    <!-- MAIN GRID -->
    <section
      class="grid gap-4 xl:grid-cols-[minmax(0,1.35fr)_minmax(0,1fr)]"
    >
      <!-- LEFT COLUMN -->
      <div class="space-y-4">
        <!-- 1. WHAT CHANGED SINCE LAST WEEK -->
        <Card>
          <CardHeader class="pb-2 flex flex-row items-start justify-between">
            <div>
              <CardTitle class="text-sm flex items-center gap-2">
                <Activity class="h-4 w-4" />
                What changed since last week?
              </CardTitle>
              <CardDescription class="text-xs mt-1">
                Ringkasan keputusan baru, topik yang macet, dan isu yang
                terus berulang.
              </CardDescription>
            </div>
            <Badge variant="outline" class="text-[11px]">
              Weekly delta
            </Badge>
          </CardHeader>
          <CardContent class="pt-2 grid gap-3 md:grid-cols-3">
            <div>
              <p class="text-4xl font-semibold text-center">
                {{ changedSummary.decisions }}
              </p>
              <p class="text-xs text-muted-foreground mt-1 text-center">
                new decisions this week
              </p>
            </div>
            <div>
              <p class="text-4xl font-semibold text-center">
                {{ changedSummary.unresolved }}
              </p>
              <p class="text-xs text-muted-foreground mt-1 text-center">
                unresolved topics still open
              </p>
            </div>
            <div>
              <p class="text-4xl font-semibold text-center">
                {{ changedSummary.recurring }}
              </p>
              <p class="text-xs text-muted-foreground mt-1 text-center">
                recurring issues detected
              </p>
            </div>
          </CardContent>
          <!-- <CardFooter class="pt-1">
            <p class="text-[11px] text-muted-foreground">
              “There are
              <strong>{{ changedSummary.decisions }} new decisions</strong>,
              <strong>{{ changedSummary.unresolved }} unresolved topics</strong>,
              and
              <strong>{{ changedSummary.recurring }} recurring issue</strong>
              this week.”
            </p>
          </CardFooter> -->
        </Card>

        <!-- 2. MEETING → KNOWLEDGE FLOW -->
        <Card>
          <CardHeader>
            <CardTitle class="text-sm flex items-center gap-2">
              <MessageCircle class="h-4 w-4" />
              Meeting
            </CardTitle>
            <CardDescription class="text-xs">
              Visual timeline bagaimana topik bergerak lintas meeting.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea class="w-full overflow-x-auto">
              <div class="flex items-center gap-8 pb-2 min-w-130">
                <div
                  v-for="node in flowNodes"
                  :key="node.id"
                  class="flex flex-col items-center gap-2"
                >
                  <button
                    type="button"
                    class="relative flex items-center justify-center h-9 px-3 rounded-full border text-xs bg-background hover:bg-muted"
                    :class="{
                      'border-primary text-primary font-medium': node.highlight,
                    }"
                  >
                    {{ node.label }}
                  </button>
                  <p class="text-[11px] text-muted-foreground">
                    {{ node.topic }}
                  </p>
                </div>
              </div>
            </ScrollArea>
            <p class="mt-2 text-[11px] text-muted-foreground">
              Klik node (nanti) untuk melihat potongan transcript, siapa yang
              bicara, dan di meeting mana topik ini muncul lagi.
            </p>
          </CardContent>
        </Card>

        <!-- 3. UNFINISHED CONVERSATIONS -->
        <Card>
          <CardHeader class="pb-2">
            <CardTitle class="text-sm">
              Unfinished conversations
            </CardTitle>
            <CardDescription class="text-xs">
              Topik yang terus muncul di beberapa meeting tapi belum ada
              keputusan jelas.
            </CardDescription>
          </CardHeader>
          <CardContent class="pt-1 space-y-3">
            <div
              v-for="item in unfinished"
              :key="item.topic"
              class="flex items-start justify-between gap-3 border rounded-md px-3 py-2 bg-muted/40"
            >
              <div>
                <p class="text-sm font-medium">
                  {{ item.topic }}
                </p>
                <p class="text-[11px] text-muted-foreground mt-1">
                  Muncul di
                  <strong>{{ item.meetings }} meeting</strong> ·
                  {{ item.note }}
                </p>
              </div>
              <Badge variant="outline" class="text-[11px] shrink-0">
                {{ item.tag }}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- RIGHT COLUMN -->
      <div class="space-y-4">
        <!-- 4. SPEAKER DYNAMICS -->
        <Card>
          <CardHeader>
            <CardTitle>
              Speaker dynamics
            </CardTitle>
          </CardHeader>
          <CardContent class="space-y-3">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs text-muted-foreground">
                  Dominant decision voice
                </p>
                <p class="text-sm font-semibold mt-0.5">
                  {{ speakerInsight.mainSpeaker }}
                </p>
              </div>
              <div class="text-right">
                <p class="text-xs text-muted-foreground">
                  Share of decisions
                </p>
                <p class="text-xl font-semibold">
                  {{ speakerInsight.ratio }}
                </p>
              </div>
            </div>
            <p class="text-[11px] text-muted-foreground leading-relaxed">
              {{ speakerInsight.text }}
            </p>
          </CardContent>
        </Card>

        <!-- 5. MEETING SMELL INDICATOR -->
        <Card>
          <CardHeader>
            <CardTitle class="text-sm flex items-center gap-2">
              <AlertCircle class="h-4 w-4" />
              Meeting indicator
            </CardTitle>
            <!-- <CardDescription class="text-xs">
              Sinyal awal meeting yang terlalu panjang, berulang, atau minim
              outcome.
            </CardDescription> -->
          </CardHeader>
          <CardContent>
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs text-muted-foreground">
                  Overall score
                </p>
                <p class="text-2xl font-semibold">
                  {{ meetingSmell.score }}
                  <span class="text-xs text-muted-foreground">/ 100</span>
                </p>
              </div>
              <Badge variant="outline" class="text-[11px]">
                {{ meetingSmell.level }}
              </Badge>
            </div>
            <Separator class="my-1" />
            <div class="flex flex-wrap gap-2">
              <Badge
                v-for="badge in meetingSmell.badges"
                :key="badge.label"
                variant="outline"
                class="flex items-center gap-1 text-[11px]"
              >
                <component :is="badge.icon" class="h-3 w-3" />
                <span>{{ badge.label }}</span>
              </Badge>
            </div>
          </CardContent>
        </Card>

        <!-- 6. KNOWLEDGE MAP -->
        <Card>
          <CardHeader class="pb-2">
            <CardTitle class="text-sm flex items-center gap-2">
              <Map class="h-4 w-4" />
              Knowledge map (cross-meeting)
            </CardTitle>
            <CardDescription class="text-xs">
              Topik utama dan seberapa sering muncul lintas meeting.
            </CardDescription>
          </CardHeader>
          <CardContent class="pt-2">
            <div class="relative h-32">
              <div
                class="absolute inset-0 flex items-center justify-center opacity-20"
              >
                <div class="h-24 w-24 rounded-full border border-dashed" />
              </div>
              <div class="absolute inset-0 flex items-center justify-center">
                <div
                  v-for="(topic, idx) in knowledgeMap.topics"
                  :key="topic.label"
                  class="absolute"
                  :class="[
                    idx === 0 && 'left-1/2 -translate-x-1/2 -top-1',
                    idx === 1 && 'right-2 top-6',
                    idx === 2 && 'left-3 bottom-4',
                    idx === 3 && 'left-1/2 -translate-x-1/2 bottom-0',
                  ]"
                >
                  <Badge variant="outline" class="text-[11px]">
                    {{ topic.label }} · {{ topic.count }}
                  </Badge>
                </div>
              </div>
            </div>
            <!-- <p class="mt-2 text-[11px] text-muted-foreground">
              Node = topik, angka = berapa meeting yang menyentuh topik
              tersebut. Edge akan divisualisasikan saat data meeting siap.
            </p> -->
          </CardContent>
        </Card>

        <!-- 7. ASK YOUR MEETINGS + 8. ONE THING TODAY -->
        <Card>
          <CardHeader class="pb-2">
            <CardTitle class="text-sm flex items-center gap-2">
              <Search class="h-4 w-4" />
              Ask your meetings
            </CardTitle>
            <CardDescription class="text-xs">
              Ajukan pertanyaan lintas transcript meeting.
            </CardDescription>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="flex items-center gap-2">
              <Input
                placeholder="Contoh: Siapa saja yang menyetujui perubahan budget minggu ini?"
                class="text-xs"
              />
              <Button size="sm" class="text-xs">
                Ask
              </Button>
            </div>
            <!-- <p class="text-[11px] text-muted-foreground">
              Output yang diharapkan: daftar meeting terkait, kutipan transcript
              penting, dan siapa yang menyetujui keputusan.
            </p> -->
            <Separator />
            <div class="flex items-center gap-2">
              <Sparkles class="h-4 w-4 text-yellow-500" />
              <p class="text-xs font-medium">
                If you only read one thing today
              </p>
            </div>
            <!-- <ul class="mt-1 space-y-1 text-[11px] text-muted-foreground">
              <li v-for="(item, idx) in todaysHighlights" :key="idx">
                • {{ item }}
              </li>
            </ul> -->
          </CardContent>
        </Card>
      </div>
    </section>
  </div>
</template>
