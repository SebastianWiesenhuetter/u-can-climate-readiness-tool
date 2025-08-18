// import { defineStore } from "pinia";
// import { v4 as uuidv4 } from "uuid";

// export const useSurvey = defineStore("survey", {
//   state: () => ({
//     sessionId: localStorage.getItem("ucan_session") || "",
//     respondent: "",
//     answers: {} as Record<number, number>, // questionId -> value
//     categories: [] as number[],           // ordering of category IDs
//     currentIndex: 0,
//   }),
//   actions: {
//     initSession() {
//       if (!this.sessionId) {
//         this.sessionId = uuidv4();
//         localStorage.setItem("ucan_session", this.sessionId);
//       }
//     },
//     setAnswer(qid: number, value: number) {
//       this.answers[qid] = value;
//     },
//     setCategories(ids: number[]) { this.categories = ids; },
//     next() { if (this.currentIndex < this.categories.length - 1) this.currentIndex++; },
//     prev() { if (this.currentIndex > 0) this.currentIndex--; },
//     currentCategoryId(): number { return this.categories[this.currentIndex]; },
//   },
// });

// src/stores/useSurvey.ts
import { defineStore } from "pinia";
import { v4 as uuidv4 } from "uuid";

export const useSurvey = defineStore("survey", {
  state: () => ({
    sessionId: localStorage.getItem("ucan_session") || "",
    respondent: "",
    answers: {} as Record<number, number>,
    categories: [] as number[],
    currentIndex: 0,
  }),
  actions: {
    initSession() {
      if (!this.sessionId) {
        this.sessionId = uuidv4();
        localStorage.setItem("ucan_session", this.sessionId);
      }
    },
    setAnswer(qid: number, value: number) { this.answers[qid] = value; },
    setCategories(ids: number[]) {
      // set once or when different
      if (!this.categories.length || JSON.stringify(this.categories) !== JSON.stringify(ids)) {
        this.categories = ids;
        this.currentIndex = 0;
      }
    },
    setCurrentByCategoryId(id: number) {
      const idx = this.categories.indexOf(id);
      if (idx >= 0) this.currentIndex = idx;
    },
    next() { if (this.currentIndex < this.categories.length - 1) this.currentIndex++; },
    prev() { if (this.currentIndex > 0) this.currentIndex--; },
    currentCategoryId(): number | undefined { return this.categories[this.currentIndex]; },
  },
});
