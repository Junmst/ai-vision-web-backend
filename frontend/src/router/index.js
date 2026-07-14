import { createRouter, createWebHistory } from "vue-router";
import AuthPage from "../pages/AuthPage.vue";
import WorkbenchPage from "../pages/WorkbenchPage.vue";
import HistoryPage from "../pages/HistoryPage.vue";
import AIConfigPage from "../pages/AIConfigPage.vue";
import { getToken } from "../stores/authStore";

const routes = [
  { path: "/", redirect: "/workbench" },
  { path: "/auth", name: "auth", component: AuthPage },
  { path: "/workbench", name: "workbench", component: WorkbenchPage, meta: { auth: true } },
  { path: "/history", name: "history", component: HistoryPage, meta: { auth: true } },
  { path: "/ai-configs", name: "aiConfigs", component: AIConfigPage, meta: { auth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 路由守卫：未登录时统一跳转到登录页
router.beforeEach((to) => {
  if (to.meta.auth && !getToken()) {
    return { path: "/auth" };
  }
  return true;
});

export default router;
