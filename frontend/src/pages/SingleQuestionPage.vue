<script setup lang="ts">
import { onMounted, ref, watch, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getByCategory } from "@/api/questionnaire";
import { submitAnswer, getCategories } from "@/api/questionnaire";
import { useSurvey } from "@/stores/useSurvey";
import QuestionBlock from "@/components/QuestionBlock.vue";
import type { GroupedCategory, Question } from "@/types";


const route = useRoute();
const router = useRouter();
const survey = useSurvey();

const cid = computed(() => Number(route.params.cid)); // category id
const qi  = computed(() => Number(route.params.qi));  // index in that category (0-based)

const totalQuestions = ref(0);
const currentIndexGlobal = ref(0); // 0-based across all questions
const progressPercent = computed(() => {
  if (!totalQuestions.value) return 0;
  return Math.round(((currentIndexGlobal.value + 1) / totalQuestions.value) * 100);
});


const group = ref<GroupedCategory | null>(null);
const q     = ref<Question | null>(null);
const loading = ref(true);
const error   = ref<string | null>(null);

async function ensureCategories() {
  if (!survey.categories.length) {
    const cats = await getCategories();
    survey.setCategories(cats.map(c => c.category_id));
  }
}


async function computeProgress() {
  // Ensure categories are present
  await ensureCategories();

  // Load all category question counts (minimal calls: reuse current group if it matches)
  let counts: { id: number; count: number }[] = [];
  for (const id of survey.categories) {
    if (group.value && id === cid.value) {
      counts.push({ id, count: group.value.questions.length });
    } else {
      const g = await getByCategory(id);
      counts.push({ id, count: g.questions.length });
    }
  }
  totalQuestions.value = counts.reduce((a, b) => a + b.count, 0);

  // Compute index offset before current category
  const before = counts
    .slice(0, counts.findIndex(c => c.id === cid.value))
    .reduce((a, b) => a + b.count, 0);

  currentIndexGlobal.value = before + qi.value; // 0-based
}


async function load() {
  loading.value = true; error.value = null; q.value = null; group.value = null;
  try {
    await ensureCategories();
    const g = await getByCategory(cid.value);
    group.value = g;
    if (qi.value < 0 || qi.value >= g.questions.length) {
      throw new Error("Invalid question index");
    }
    q.value = g.questions[qi.value];
  } catch (e:any) {
    error.value = e?.message || "Failed to load";
  } finally {
    loading.value = false;
    await computeProgress();
  }
}

onMounted(async () => {
  if (!survey.sessionId) survey.initSession();
  await load();
});

watch(() => [route.params.cid, route.params.qi], load);

function setAnswer(val:number) {
  if (!q.value) return;
  survey.setAnswer(q.value.id, val);
}

async function next() {
  if (!q.value) return;
  const val = survey.answers[q.value.id];
  if (val === undefined) { alert("Please select an answer."); return; }

  // Save this single answer
  await submitAnswer(survey.sessionId, q.value.id, val);

  // Compute next question (within category), else next category’s first question, else results
  const ids = survey.categories;
  const idxCat = ids.indexOf(cid.value);

  if (group.value && qi.value < group.value.questions.length - 1) {
    router.push(`/survey/${cid.value}/${qi.value + 1}`);
    return;
  }

  const nextCat = idxCat >= 0 && idxCat < ids.length - 1 ? ids[idxCat + 1] : null;
  if (nextCat) router.push(`/survey/${nextCat}/0`);
  else router.push("/results");
}

function prev() {
  const ids = survey.categories;
  const idxCat = ids.indexOf(cid.value);

  // previous in same category
  if (qi.value > 0) { router.push(`/survey/${cid.value}/${qi.value - 1}`); return; }

  // go to previous category's last question
  const prevCat = idxCat > 0 ? ids[idxCat - 1] : null;
  if (!prevCat) { router.back(); return; }

  // need last index of previous category
  getByCategory(prevCat).then(g => {
    const last = Math.max(0, g.questions.length - 1);
    router.push(`/survey/${prevCat}/${last}`);
  });
}
</script>

<template>
  <div class="p-6 max-w-3xl mx-auto">
    <div v-if="loading">Loading…</div>
    <div v-else-if="error" class="text-red-600">Error: {{ error }}</div>

    <div v-else-if="q && group">
      <h2 class="text-secondary font-bold mb-4" style="margin-left: 2rem;">{{ group.category_name }}</h2>

      <QuestionBlock
        :question="q"
        :modelValue="survey.answers[q.id]"
        @update:modelValue="setAnswer"
      />

      <div class="mt-6 flex justify-between">
        <button class="px-4 py-2 rounded border" @click="prev">Back</button>
        <button class="px-4 py-2 rounded bg-blue-600 text-white" @click="next">Next</button>
      </div>

      <!-- Progress bar (overall, across all questions) -->
      <!-- <div class="mt-6">
        <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            class="h-full"
            :style="{
              width: progressPercent + '%',
              background: '#3679C3',
              transition: 'width .25s ease'
            }"
          />
        </div>
        <div class="mt-2 text-normal" style="opacity:.8;">
          {{ currentIndexGlobal + 1 }} / {{ totalQuestions }}
        </div>
      </div> -->
      <div class="tw-mt-6">
        <div class="tw-h-2 tw-bg-gray-200 tw-rounded-full tw-overflow-hidden">
          <div
            class="tw-h-full tw-bg-brandBlue tw-transition-[width] tw-duration-200 tw-ease-linear"
            :style="{ width: progressPercent + '%' }"
          />
        </div>
        <div class="tw-mt-2 text-normal" style="opacity:.8;">
          {{ currentIndexGlobal + 1 }} / {{ totalQuestions }}
        </div>
      </div>



      <div class="mt-3 text-normal" style="opacity:.75">
        Question {{ qi + 1 }} of {{ group.questions.length }}
      </div>
    </div>
    <div v-else>
      <p>No question found.</p>
    </div>
  </div>
</template>
