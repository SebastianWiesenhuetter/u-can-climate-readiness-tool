<!-- <script setup lang="ts">
import { onMounted, ref } from "vue";
import { getMeta, getCategories } from "@/api/questionnaire";
import { useSurvey } from "@/stores/useSurvey";
import { ensureSession } from "@/api/questionnaire";
import { useRouter } from "vue-router";


const meta = ref<{title?:string|null;subtitle?:string|null}>({});
const cats = ref<{category_id:number;category_name:string;question_count:number}[]>([]);
const survey = useSurvey();

// const route = useRoute();
const router = useRouter();

onMounted(async () => {
  survey.initSession();
  await ensureSession(survey.sessionId);
  meta.value = await getMeta();
  cats.value = await getCategories();
  survey.setCategories(cats.value.map(c => c.category_id));
});
// function start() {
//   // navigate to first category
//   window.location.href = `/category/${survey.currentCategoryId()}`;
// }
function start() {
  const firstCat = survey.currentCategoryId();
  if (!firstCat) { alert("No categories found."); return; }
  // go to first question (qi=0) of the first category
  //window.location.href = `/survey/${firstCat}/0`;
  router.push(`/survey/${firstCat}/0`)

}
</script>


<template>
  <div>
    <div class="bleed">
      <img
        src="/u_can_background07.jpg"
        alt="Intro Banner"
        class="intro-banner"
      />
    </div>

    <div class="intro-container">
      <h1 class="text-main">{{ meta.title ?? 'Questionnaire' }}</h1>
      <p class="text-tertiary">{{ meta.subtitle }}</p>
      <button class="btn-primary" @click="start">Start</button>
    </div>
  </div>
</template> -->


<!-- //////////////////////////////////////////////////////////////7 -->
<!-- <script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { getMeta, getCategories, ensureSession } from "@/api/questionnaire";
import { useSurvey } from "@/stores/useSurvey";
import { CITIES } from "@/constants/cities";

const router = useRouter();
const survey = useSurvey();

const meta = ref<{ title?: string | null; subtitle?: string | null }>({});
const cats = ref<{ category_id: number; category_name: string; question_count: number }[]>([]);
const selectedCity = ref<string>(survey.cityId || ""); // reflect persisted value if present

onMounted(async () => {
  survey.initSession();
  await ensureSession(survey.sessionId);

  meta.value = await getMeta();
  const c = await getCategories();
  cats.value = c;
  survey.setCategories(c.map(x => x.category_id));
});

function chooseCity(id: string) {
  selectedCity.value = id;
  start();
}

function start() {
  if (!selectedCity.value) {
    alert("Please choose a city first.");
    return;
  }
  survey.setCity(selectedCity.value);
  survey.resetForNewCity();

  const firstCat = survey.currentCategoryId();
  if (!firstCat) { alert("No categories found."); return; }
  router.push(`/survey/${firstCat}/0`);
}
</script>

<template>
  <div>

    <div class="bleed">
      <img src="/u_can_background07.jpg" alt="Intro Banner" class="intro-banner" />
    </div>

    <div class="intro-container">
      <h1 class="text-main">{{ meta.title ?? "Questionnaire" }}</h1>
      <p class="text-tertiary">{{ meta.subtitle }}</p>

      <h2 class="text-secondary" style="margin-top: 1rem;">Choose a city to start</h2>

      <div class="city-grid" role="group" aria-label="Choose city for this questionnaire">
        <button
          v-for="c in CITIES"
          :key="c.id"
          type="button"
          class="city-card"
          :class="{ 'city-card--active': selectedCity === c.id }"
          @click="chooseCity(c.id)"
        >
          {{ c.label }}
        </button>
      </div>

    </div>
  </div>
</template> -->

<!-- ///////////////////////////////////////////////////////////// -->
 <script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { getMeta, getCategories, ensureSession } from "@/api/questionnaire";
import { useSurvey } from "@/stores/useSurvey";
import { CITIES } from "@/constants/cities";

const router = useRouter();
const survey = useSurvey();

const meta = ref<{ title?: string | null; subtitle?: string | null }>({});
const cats = ref<{ category_id: number; category_name: string; question_count: number }[]>([]);
const selectedCity = ref<string>(survey.cityId || ""); // reflect persisted value if present

onMounted(async () => {
  // Do NOT init a session here anymore; we’ll create a fresh one per city pick.
  meta.value = await getMeta();
  const c = await getCategories();
  cats.value = c;
  survey.setCategories(c.map(x => x.category_id));
  // If a city was persisted from a previous visit, highlight it
  selectedCity.value = survey.cityId || "";
});

async function chooseCity(id: string) {
  selectedCity.value = id;

  // 1) Start a brand-new logical run for this city (fresh UUID + clear answers)
  survey.startNewCity(id);

  // 2) Ensure the session exists server-side (with city_id)
  // NOTE: Your ensureSession should accept (sessionId, respondent?, cityId?)
  // If your current signature is different, adjust the args accordingly.
  // await ensureSession(survey.sessionId, survey.respondent, survey.cityId); // old way of doing it without pinia store WELL WORKING!!!
  // await survey.ensureAndSyncSession(); // persist it server-side, sync city if backend modifies it
  try {
    await survey.ensureAndSyncSession();
  } catch (e:any) {
    console.error(e);
    alert("Couldn't prepare your session. Please try again.");
    return;
  }


  // 3) Go to the first question of the first category
  const firstCat = survey.currentCategoryId();
  if (!firstCat) { alert("No categories found."); return; }
  router.push(`/survey/${firstCat}/0`);
}
</script>

<template>
  <div>
    <!-- Full-width banner -->
    <div class="bleed">
      <img src="/u_can_background07.jpg" alt="Intro Banner" class="intro-banner" />
    </div>

    <div class="intro-container">
      <h1 class="text-main">{{ meta.title ?? "Questionnaire" }}</h1>
      <p class="text-tertiary">{{ meta.subtitle }}</p>

      <h2 class="text-secondary" style="margin-top: 1rem;">Choose a city to start</h2>

      <!-- 2×3 grid of cities -->
      <div class="city-grid" role="group" aria-label="Choose city for this questionnaire">
        <button
          v-for="c in CITIES"
          :key="c.id"
          type="button"
          class="city-card"
          :class="{ 'city-card--active': selectedCity === c.id }"
          @click="chooseCity(c.id)"
        >
          {{ c.label }}
        </button>
      </div>
    </div>
  </div>
</template>
