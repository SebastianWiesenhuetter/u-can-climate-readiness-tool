<script setup lang="ts">
import { computed } from "vue";
import type { Question } from "@/types";

const props = defineProps<{ question: Question; modelValue?: number }>();
const emit = defineEmits<{"update:modelValue":[number]}>();

// Build the options from DB; fall back to numeric 0..5 (or min..max)
const options = computed(() => {
  if (props.question?.option_labels?.length) return props.question.option_labels;
  const min = props.question?.scale_min ?? 0;
  const max = props.question?.scale_max ?? 5;
  return Array.from({ length: max - min + 1 }, (_, i) => {
    const value = min + i;
    return { value, label: String(value) };
  });
});

const gridStyle = computed(() => ({
  display: "grid",
  gridTemplateColumns: `repeat(${options.value.length}, minmax(0,1fr))`,
  gap: "40px",
}));
</script>

<template>
  <div class="qb">
    <!-- title row -->
    <p class="qb-title">
      <span v-if="question.sub_name" class="qb-sub">{{ question.sub_name }}</span>
      <span class="qb-text">— {{ question.question_text }}</span>
    </p>

    <!-- row A: rectangular boxes with numbers -->
    <div :style="gridStyle" role="radiogroup" aria-label="Scale">
      <!-- <label
        v-for="opt in options"
        :key="opt.value"
        class="qb-box"
        :class="{ selected: modelValue === opt.value }"
        :aria-checked="modelValue === opt.value"
        role="radio"
        tabindex="0"
        @keydown.enter.prevent="emit('update:modelValue', opt.value)"
        @keydown.space.prevent="emit('update:modelValue', opt.value)"
      >
        <input
          class="visually-hidden"
          type="radio"
          :name="`q-${question.id}`"
          :value="opt.value"
          :checked="modelValue === opt.value"
          @change="emit('update:modelValue', opt.value)"
        />
        <span class="qb-num">{{ opt.value }}</span>
      </label> -->
      <!-- template (inside the top row of boxes) -->
    <label
      v-for="opt in options"
      :key="opt.value"
      class="qb-box"
      :class="{ selected: modelValue === opt.value }"
      role="radio"
      :aria-checked="modelValue === opt.value"
      tabindex="0"
      @click="emit('update:modelValue', opt.value)"            
      @keydown.enter.prevent="emit('update:modelValue', opt.value)"
      @keydown.space.prevent="emit('update:modelValue', opt.value)"

    >
      <input
        class="sr-only"                                       
        type="radio"
        :name="`q-${question.id}`"
        :value="opt.value"
        :checked="modelValue === opt.value"
        @change="emit('update:modelValue', opt.value)"        
      />
      <span class="qb-num">{{ opt.value }}</span>
    </label>

    </div>

    <!-- row B: labels under each box -->
    <div :style="gridStyle" class="qb-labels">
      <div v-for="opt in options" :key="`lbl-${opt.value}`" class="qb-label">
        {{ opt.label }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.qb { margin-bottom: 1.25rem; padding-left: 2rem; padding-right: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e5e7eb; }
.qb-title { font-weight: 600; margin-bottom: .75rem; line-height: 1.4; }
.qb-sub { color: #475569; margin-right: .5rem; }
.qb-text {}

/* boxes row */
.qb-box {
  user-select: none;
  cursor: pointer;
  border: 1px solid #cbd5e1;            /* slate-300 */
  background: #eef2ff;                   /* indigo-50 */
  border-radius: 8px;
  min-height: 56px;
  display: flex; align-items: center; justify-content: center;
  transition: transform .05s ease, filter .15s ease, background .15s ease, border-color .15s ease;
}
.qb-box:hover { filter: brightness(0.98); }
.qb-box:active { transform: translateY(1px); }
.qb-box.selected {
  background: #3679C3;                   /* U_CAN blue */
  border-color: #3679C3;
  color: white;
}

/* the big number inside box */
.qb-num { font-weight: 700; font-size: 1.25rem; line-height: 1; }

/* labels row */
.qb-labels { margin-top: .35rem; }
.qb-label { font-size: .9rem; text-align: center; color: #334155; }

/* hide native radio but keep accessible */
/* .visually-hidden {
  position: absolute; opacity: 0; width: 0; height: 0; pointer-events: none;
} */
</style>


