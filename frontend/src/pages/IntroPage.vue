<script setup lang="ts">
import { onMounted, ref } from "vue";
import { getMeta, getCategories } from "@/api/questionnaire";
import { useSurvey } from "@/stores/useSurvey";
import { ensureSession } from "@/api/questionnaire";
import { useRoute, useRouter } from "vue-router";


const meta = ref<{title?:string|null;subtitle?:string|null}>({});
const cats = ref<{category_id:number;category_name:string;question_count:number}[]>([]);
const survey = useSurvey();

const route = useRoute();
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

<!-- <template>
  <div class="p-6 max-w-3xl mx-auto">
    
    <h1 class="text-main font-bold mb-2">{{ meta.title ?? 'Questionnaire' }}</h1>
    
    <p class="text-tertiary mb-6">{{ meta.subtitle }}</p>
    <button class="px-4 py-2 rounded bg-blue-600 text-white" @click="start">Start</button>
  </div>
</template> -->

<!-- old headlines -->
<!-- <h1 class="text-3xl font-bold mb-2">{{ meta.title ?? 'Questionnaire' }}</h1> -->
<!-- <p class="text-gray-600 mb-6">{{ meta.subtitle }}</p> -->


<!-- style="display:block; width:100%; height:450px; object-fit:cover;" -->

<template>
  <div>
    <!-- Full-width banner that ignores main padding -->
    <div class="bleed">
      <img
        src="/u_can_background03.jpg"
        alt="Intro Banner"
        style="display:block; width:100%; height:auto; object-fit:cover;"
      />
    </div>

    <div class="p-6 max-w-3xl mx-auto" style="margin-left: 2rem;">
      <h1 class="text-main font-bold mb-2">{{ meta.title ?? 'Questionnaire' }}</h1>
      <p class="text-tertiary mb-6">{{ meta.subtitle }}</p>
      <button class="px-4 py-2 rounded bg-blue-600 text-white" @click="start">Start</button>
    </div>
  </div>
</template>


