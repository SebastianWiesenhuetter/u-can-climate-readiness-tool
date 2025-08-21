// import { http } from "./http";
// import type { Question, GroupedCategory, CategorySummary, Meta } from "@/types";

// export const getMeta = () => http.get<Meta>("/meta");
// export const getCategories = () => http.get<CategorySummary[]>("/categories");
// export const getGrouped = () => http.get<GroupedCategory[]>("/questions/grouped");
// export const getByCategory = (categoryId: number) =>
//   http.get<GroupedCategory>(`/questions/by-category/${categoryId}`);

// export const ensureSession = (sessionId: string, respondent?: string) =>
//   http.post<{ ok: true; session_id: string }>("/sessions", {
//     session_id: sessionId,
//     respondent_ref: respondent,
//   });

// export const submitAnswer = (sessionId: string, questionId: number, value: number) =>
//   http.post("/answers", { session_id: sessionId, question_id: questionId, value });

// export const submitBulk = (
//   sessionId: string,
//   items: { question_id: number; value: number }[],
//   respondent?: string
// ) =>
//   http.post<{ ok: true; count: number }>("/answers/bulk", {
//     session_id: sessionId,
//     respondent_ref: respondent,
//     answers: items.map(a => ({ ...a, session_id: sessionId })),
//   });

// export const getSessionSummary = (sessionId: string) =>
//   http.get<{ session_id: string; per_category: { category_id: number; category_name: string; avg_value: number; count: number }[] }>(
//     `/sessions/${sessionId}/summary`
//   );

///////////////////////////7

import { http } from "./http";
import type { Question, GroupedCategory, CategorySummary, Meta } from "@/types";

export const getMeta = () => http.get<Meta>("/meta");
export const getCategories = () => http.get<CategorySummary[]>("/categories");
export const getGrouped = () => http.get<GroupedCategory[]>("/questions/grouped");
export const getByCategory = (categoryId: number) =>
  http.get<GroupedCategory>(`/questions/by-category/${categoryId}`);


// export const ensureSession = (sessionId: string, respondent?: string, city_id?: string) =>
//   http.post<{ ok: true; session_id: string }>("/sessions", {
//     session_id: sessionId,
//     respondent_ref: respondent,
//     city_id, // <- include this
//   });

export type EnsureSessionResp = {
  ok: boolean;
  session_id: string;
  city_id: string;
};

export async function ensureSession(
  sessionId: string,
  respondent?: string,
  cityId?: string
) {
  return http.post<EnsureSessionResp>("/sessions", {
    session_id: sessionId,
    respondent_ref: respondent ?? null,
    city_id: cityId ?? null,
  });
}



/**  now sends city_id */
export const submitAnswer = (
  sessionId: string,
  questionId: number,
  value: number,
  cityId: string
) =>
  http.post("/answers", {
    session_id: sessionId,
    city_id: cityId,
    question_id: questionId,
    value,
  });

/**  now accepts cityId and sends it (top-level + per-item for schema compatibility) */
export const submitBulk = (
  sessionId: string,
  cityId: string,
  items: { question_id: number; value: number }[],
  respondent?: string
) =>
  http.post<{ ok: true; count: number }>("/answers/bulk", {
    session_id: sessionId,
    city_id: cityId,
    respondent_ref: respondent,
    answers: items.map(a => ({
      ...a,
      session_id: sessionId,
      city_id: cityId,
    })),
  });

/**  now requires cityId in query string */
export const getSessionSummary = (sessionId: string, cityId: string) =>
  http.get<{
    session_id: string;
    per_category: {
      category_id: number;
      category_name: string;
      avg_value: number;
      count: number;
    }[];
  }>(`/sessions/${encodeURIComponent(sessionId)}/summary?city=${encodeURIComponent(cityId)}`);


  export const getAllCitiesRadar = () =>
  http.get<{
    categories: string[];
    cities: string[];
    series: number[][];
  }>("/analytics/radar-all-cities");

