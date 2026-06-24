import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    redirect: "/login"
  },

  {
    path: "/login",
    component: () => import("../views/Login.vue")
  },

  {
    path: "/register",
    component: () => import("../views/Register.vue")
  },

  {
    path: "/dashboard",
    component: () => import("../views/Dashboard.vue"),
    meta: { requiresAuth: true }
  },

  {
    path: "/chat",
    component: () => import("../views/Chat.vue"),
    meta: { requiresAuth: true }
  },

  {
    path: "/knowledge",
    component: () => import("../views/Knowledge.vue"),
    meta: { requiresAuth: true }
  },

  {
    path: "/chunks",
    component: () => import("../views/Chunk.vue"),
    meta: { requiresAuth: true }
  },

  {
    path: "/config",
    component: () => import("../views/Config.vue"),
    meta: { requiresAuth: true }
  },

  {
    path: "/system",
    component: () => import("../views/System.vue"),
    meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {

  const token =
    localStorage.getItem("token");

  if (
    to.meta.requiresAuth &&
    !token
  ) {
    next("/login");
  } else {
    next();
  }
});

export default router;