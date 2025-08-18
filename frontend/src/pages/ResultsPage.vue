<script setup lang="ts">
import { onMounted, ref } from "vue";
import { Chart, RadarController, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from "chart.js";
import { useSurvey } from "@/stores/useSurvey";
import { getSessionSummary } from "@/api/questionnaire";

Chart.register(RadarController, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

const survey = useSurvey();
const canvasRef = ref<HTMLCanvasElement | null>(null);

onMounted(async () => {
  const summary = await getSessionSummary(survey.sessionId);
  const labels = summary.per_category.map((c:any) => c.category_name);
  const data = summary.per_category.map((c:any) => c.avg_value);

  if (canvasRef.value) {
    new Chart(canvasRef.value, {
      type: "radar",
      data: {
        labels,
        datasets: [{ label: "Readiness", data }]
      },
      options: { responsive: true, scales: { r: { min: 0, max: 5 } } }
    });
  }
});
</script>

<template>
  <div class="p-6 max-w-3xl mx-auto">
    <h2 class="text-2xl font-bold mb-4">Results</h2>
    <canvas ref="canvasRef"></canvas>
  </div>
</template>
