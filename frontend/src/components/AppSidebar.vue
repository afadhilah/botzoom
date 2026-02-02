<script setup lang="ts">
import type { SidebarProps } from '@/components/ui/sidebar'

import {
  AudioWaveform,
  BookOpen,
  // Bot,
  Command,
  // Frame,
  // GalleryVerticalEnd,
  // Map,
  // PieChart,
  Settings2,
  // SquareTerminal,
  LayoutDashboard,
  Video,
} from "lucide-vue-next"
import NavMain from '@/components/NavMain.vue'
// import NavProjects from '@/components/NavProjects.vue'
import NavUser from '@/components/NavUser.vue'
import TeamSwitcher from '@/components/TeamSwitcher.vue'

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from '@/components/ui/sidebar'

import plnLogo from '@/assets/PLN-Icon-Plus.png'


const props = withDefaults(defineProps<SidebarProps>(), {
  collapsible: "icon",
})

// This is sample data.
const data = {
  user: {
    name: "Ahmad Fadhilah",
    email: "afadhilah2004@gmail.com",
    avatar: "/avatars/shadcn.jpg",
  },
  teams: [
    {
      name: "PLN Icon Plus",
      logo: plnLogo,
      plan: "Enterprise",
    },
    {
      name: "Team 2",
      logo: AudioWaveform,
      plan: "Startup",
    },
    {
      name: "Team 3",
      logo: Command,
      plan: "Free",
    },
  ],
  navMain: [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: LayoutDashboard,
      isActive: true,
      items: [
        {
          title: "Overview",
          url: "/dashboard",
        },
        {
          title: "Transcript Meeting",
          url: "/transcript",
        },
        {
          title: "Transcript List",
          url: "/transcript-list",
        },
        {
          title: "Test",
          url: "/test",
        }
      ],
    },
    {
      title: "Meetings",
      url: "#",
      icon: Video,
      isActive: true,
      items: [
        {
          title: "Upcoming",
          url: "#",
        },
        {
          title: "Past",
          url: "#",
        },
        {
          title: "Record Meeting",
          url: "#",
        },
      ],
    },
    {
      title: "Documentation",
      url: "#",
      icon: BookOpen,
      items: [
        {
          title: "Introduction",
          url: "#",
        },
        {
          title: "Get Started",
          url: "#",
        },
        {
          title: "Tutorials",
          url: "#",
        },
        {
          title: "Changelog",
          url: "#",
        },
      ],
    },
    {
      title: "Settings",
      url: "#",
      icon: Settings2,
      items: [
        {
          title: "General",
          url: "#",
        },
        {
          title: "Team",
          url: "#",
        },
        {
          title: "Billing",
          url: "#",
        },
        {
          title: "Limits",
          url: "#",
        },
      ],
    },
  ],
}
</script>

<template>
  <Sidebar v-bind="props">
    <SidebarHeader>
      <TeamSwitcher :teams="data.teams" />
    </SidebarHeader>
    <SidebarContent>
      <NavMain :items="data.navMain" />
      <!-- <NavProjects :projects="data.projects" /> -->
    </SidebarContent>
    <SidebarFooter>
      <NavUser :user="data.user" />
    </SidebarFooter>
    <SidebarRail />
  </Sidebar>
</template>
