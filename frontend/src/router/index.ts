import { createRouter, createWebHistory } from "vue-router"
import type { RouteRecordRaw } from "vue-router"
import { useAuthStore } from "@/features/auth/store"
import DashboardPage from "@/pages/dashboard/OverviewPage.vue"
// import testpage from "@/pages/dashboard/test.vue"
import TranscriptMeeting from "@/pages/zoom_resume/TranscriptMeeting.vue"
import LoginPage from "@/pages/auth/LoginPage.vue"
import SignupPage from "@/pages/auth/SignupPage.vue"
import OTPPage from "@/pages/auth/OtpPage.vue"
import Sidebar from "@/pages/dashboard/Sidebar.vue"
import TranscriptList from "@/pages/zoom_resume/TranscriptList.vue"
import NotFound from "@/pages/error/NotFound.vue"
import testpage from "@/pages/zoom_resume/test.vue"

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    component: Sidebar,
    meta: { requiresAuth: true },
    children: [
      { path: "", redirect: "/dashboard" },
      { path: "dashboard", name: "dashboard", component: DashboardPage },
      { path: "transcript", name: "transcript", component: TranscriptMeeting, meta: { breadcrumb: "Transcript Meeting" } },
      { path: "transcript-list", name: "transcript-list", component: TranscriptList, meta: { breadcrumb: "History Transcript" } },
      { path: "test", name: "test", component: testpage },
    ]
  },
  {
    path: "/auth",
    meta: { requiresGuest: true },
    children: [
      { path: "", redirect: "/auth/login" },
      { path: "login", name: "login", component: LoginPage },
      { path: "signup", name: "signup", component: SignupPage },
      { path: "verify-otp", name: "verify-otp", component: OTPPage },
    ]
  },
  // { path: "/testpage", name: "testpage", component: testpage },
  // error pages
  { path: "/:pathMatch(.*)*", name: "NotFound", component: NotFound },

]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Initialize auth on first navigation
  if (!authStore.user && !from.name) {
    await authStore.initializeAuth()
  }

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)

  if (requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (requiresGuest && authStore.isAuthenticated) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})