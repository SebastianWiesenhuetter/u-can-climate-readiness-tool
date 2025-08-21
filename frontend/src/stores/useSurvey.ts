// src/stores/useSurvey.ts
// import { defineStore } from "pinia";
// import { v4 as uuidv4 } from "uuid";

// type AnswersMap = Record<number, number>;

// export const useSurvey = defineStore("survey", {
//   state: () => ({
//     sessionId: localStorage.getItem("ucan_session") || "",
//     respondent: "",
//     answers: {} as AnswersMap,
//     cityId: (localStorage.getItem("u_can_city") || "") as string, // persisted city
//     categories: [] as number[],
//     currentIndex: 0,
//   }),
//   actions: {
//     initSession() {
//       if (!this.sessionId) {
//         this.sessionId = uuidv4();
//         localStorage.setItem("ucan_session", this.sessionId);
//       }
//     },
//     setAnswer(qid: number, value: number) { this.answers[qid] = value; },
//     setCategories(ids: number[]) {
//       // set once or when different
//       if (!this.categories.length || JSON.stringify(this.categories) !== JSON.stringify(ids)) {
//         this.categories = ids;
//         this.currentIndex = 0;
//       }
//     },
//     setCity(cityId: string) {
//       this.cityId = cityId;
//       localStorage.setItem("u_can_city", cityId);
//     },
//     setCurrentByCategoryId(id: number) {
//       const idx = this.categories.indexOf(id);
//       if (idx >= 0) this.currentIndex = idx;
//     },
//     next() { if (this.currentIndex < this.categories.length - 1) this.currentIndex++; },
//     prev() { if (this.currentIndex > 0) this.currentIndex--; },
//     resetForNewCity() {
//       this.answers = {};
//       // keep sessionId if you like, or generate a new one per city:
//       // this.sessionId = crypto.randomUUID();
//     },
//     currentCategoryId(): number | undefined { return this.categories[this.currentIndex]; },
//   },
// });


////////////////////////////////////////////////////////////////////////7

// import { defineStore } from "pinia";
// import { v4 as uuidv4 } from "uuid";

// type AnswersMap = Record<number, number>;

// const LS_KEYS = {
//   session: "ucan_session",
//   city: "ucan_city",
// } as const;

// export const useSurvey = defineStore("survey", {
//   state: () => ({
//     sessionId: localStorage.getItem(LS_KEYS.session) || "",
//     respondent: "",
//     answers: {} as AnswersMap,
//     cityId: (localStorage.getItem(LS_KEYS.city) || "") as string,
//     categories: [] as number[],
//     currentIndex: 0,
//   }),
//   actions: {
//     initSession() {
//       if (!this.sessionId) {
//         this.sessionId = uuidv4();
//         localStorage.setItem(LS_KEYS.session, this.sessionId);
//       }
//     },
//     setAnswer(qid: number, value: number) {
//       this.answers[qid] = value;
//     },
//     setCategories(ids: number[]) {
//       if (!ids?.length) return;

//       const currentCat = this.categories[this.currentIndex];
//       this.categories = ids.slice();

//       // keep same category if still present; else reset to first
//       const keepIdx = currentCat != null ? this.categories.indexOf(currentCat) : -1;
//       this.currentIndex = keepIdx >= 0 ? keepIdx : 0;
//     },
//     setCity(cityId: string) {
//       this.cityId = cityId;
//       localStorage.setItem(LS_KEYS.city, cityId);
//     },
//     setCurrentByCategoryId(id: number) {
//       const idx = this.categories.indexOf(id);
//       if (idx >= 0) this.currentIndex = idx;
//     },
//     next() {
//       if (this.currentIndex < this.categories.length - 1) this.currentIndex++;
//     },
//     prev() {
//       if (this.currentIndex > 0) this.currentIndex--;
//     },
//     resetForNewCity() {
//       this.answers = {};
//       // If you want a new logical run per city:
//       // this.sessionId = uuidv4();
//       // localStorage.setItem(LS_KEYS.session, this.sessionId);
//       this.currentIndex = 0;
//     },
//     currentCategoryId(): number | undefined {
//       return this.categories[this.currentIndex];
//     },
//   },
// });

///////////////////////////////////////////////////////////////////////////7
import { defineStore } from "pinia";
import { v4 as uuidv4 } from "uuid";
import { ensureSession } from "@/api/questionnaire";


type AnswersMap = Record<number, number>;

const LS_KEYS = {
  session: "ucan_session",
  city: "ucan_city",
} as const;

export const useSurvey = defineStore("survey", {
  state: () => ({
    sessionId: localStorage.getItem(LS_KEYS.session) || "",
    respondent: "",
    answers: {} as AnswersMap,
    cityId: (localStorage.getItem(LS_KEYS.city) || "") as string,
    categories: [] as number[],
    currentIndex: 0,
  }),
  actions: {
    initSession() {
      if (!this.sessionId) {
        this.sessionId = uuidv4();
        localStorage.setItem(LS_KEYS.session, this.sessionId);
      }
    },

    /** Start a brand-new run for the selected city */
    startNewCity(cityId: string) {
      // new logical session
      this.sessionId = uuidv4();
      localStorage.setItem(LS_KEYS.session, this.sessionId);

      // set chosen city
      this.cityId = cityId;
      localStorage.setItem(LS_KEYS.city, cityId);

      // clear previous answers & reset navigation
      this.answers = {};
      this.currentIndex = 0;
    },

    setAnswer(qid: number, value: number) {
      this.answers[qid] = value;
    },

    setCategories(ids: number[]) {
      if (!ids?.length) return;

      const currentCat = this.categories[this.currentIndex];
      this.categories = ids.slice();

      // keep same category if still present; else reset to first
      const keepIdx = currentCat != null ? this.categories.indexOf(currentCat) : -1;
      this.currentIndex = keepIdx >= 0 ? keepIdx : 0;
    },

    setCity(cityId: string) {
      this.cityId = cityId;
      localStorage.setItem(LS_KEYS.city, cityId);
    },

    setCurrentByCategoryId(id: number) {
      const idx = this.categories.indexOf(id);
      if (idx >= 0) this.currentIndex = idx;
    },

    next() {
      if (this.currentIndex < this.categories.length - 1) this.currentIndex++;
    },

    prev() {
      if (this.currentIndex > 0) this.currentIndex--;
    },

    resetForNewCity() {
      this.answers = {};
      this.currentIndex = 0;
      // Note: use startNewCity(cityId) if you want a NEW session id too.
    },

    currentCategoryId(): number | undefined {
      return this.categories[this.currentIndex];
    },


    /** Ensure session exists on server and sync returned city_id (if any). */
    async ensureAndSyncSession(respondent?: string) {
      // If there’s no session yet, create one first.
      if (!this.sessionId) {
        this.sessionId = uuidv4();
        localStorage.setItem(LS_KEYS.session, this.sessionId);
      }

      const resp = await ensureSession(this.sessionId, respondent, this.cityId || undefined);

      // If server returns a city_id (e.g., created server-side) keep store + localStorage aligned
      if (resp.city_id && resp.city_id !== this.cityId) {
        this.cityId = resp.city_id;
        localStorage.setItem(LS_KEYS.city, resp.city_id);
      }
    },

  },
});
