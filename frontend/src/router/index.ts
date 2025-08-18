import { createRouter, createWebHistory } from "vue-router";
import IntroPage from "@/pages/IntroPage.vue";
import CategoryPage from "@/pages/CategoryPage.vue";
import ResultsPage from "@/pages/ResultsPage.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: IntroPage },
    { path: "/category/:id", component: CategoryPage },
    { path: "/results", component: ResultsPage },
  ],
});

