<script setup lang="ts">
import { onMounted, ref, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getByCategory, submitBulk, getCategories } from "@/api/questionnaire";
import { useSurvey } from "@/stores/useSurvey";
import QuestionBlock from "@/components/QuestionBlock.vue";
import type { GroupedCategory } from "@/types";

const route = useRoute();
const router = useRouter();
const survey = useSurvey();

const category = ref<GroupedCategory | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);

const categoryId = computed(() => Number(route.params.id));

async function ensureCategories() {
  if (!survey.categories.length) {
    const cats = await getCategories();
    survey.setCategories(cats.map((c) => c.category_id));
  }
}

async function loadData(id: number) {
  loading.value = true;
  error.value = null;
  category.value = null;
  try {
    await ensureCategories();
    category.value = await getByCategory(id);
  } catch (e: any) {
    error.value = e?.message || "Failed to load category";
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  if (!survey.sessionId) survey.initSession();
  await loadData(categoryId.value);
});

// If you navigate via router.push to a new category, this will re-fetch:
watch(() => route.params.id, async (newId) => {
  const idNum = Number(newId);
  if (!Number.isFinite(idNum)) return;
  await loadData(idNum);
});

function setAnswer(qid: number, val: number) {
  survey.setAnswer(qid, val);
}

async function next() {
  if (!category.value) return;

  // require all answered
  const unanswered = category.value.questions.filter((q) => survey.answers[q.id] === undefined);
  if (unanswered.length) {
    alert("Please answer all questions on this page.");
    return;
  }

  // save this page
  const items = category.value.questions.map((q) => ({ question_id: q.id, value: survey.answers[q.id] }));
  // await submitBulk(survey.sessionId, items);
  await submitBulk(survey.sessionId, survey.cityId, items);


  // compute nextId from URL param + store.categories (no reliance on store index)
  const ids = survey.categories;
  const idx = ids.indexOf(categoryId.value);
  const nextId = idx >= 0 && idx < ids.length - 1 ? ids[idx + 1] : null;

  if (!nextId) {
    router.push("/results");
  } else {
    router.push(`/category/${nextId}`);
  }
}

function prev() {
  const ids = survey.categories;
  const idx = ids.indexOf(categoryId.value);
  const prevId = idx > 0 ? ids[idx - 1] : null;
  if (prevId) router.push(`/category/${prevId}`);
  else router.back();
}
</script>

<template>
  <div class="p-6 max-w-3xl mx-auto">
    <div v-if="loading">Loading…</div>
    <div v-else-if="error" class="text-red-600">Error: {{ error }}</div>

    <div v-else-if="category">
      <!-- <h2 class="text-2xl font-bold mb-4">{{ category.category_name }}</h2> -->
      <h2 class="text-secondary font-bold mb-4" style="margin-left: 2rem;">{{ category.category_name }}</h2>

      <QuestionBlock
        v-for="q in category.questions"
        :key="q.id"
        :question="q"
        :modelValue="survey.answers[q.id]"
        @update:modelValue="(val) => setAnswer(q.id, val)"
      />

      <div class="mt-6 flex justify-between">
        <button class="px-4 py-2 rounded border" @click="prev">Back</button>
        <button class="px-4 py-2 rounded bg-blue-600 text-white" @click="next">Next</button>
      </div>
    </div>

    <div v-else>
      <p>No questions found for this category.</p>
    </div>
  </div>
</template>
