<!-- <script setup lang="ts">
import { onMounted, ref } from "vue";
import { Chart, RadarController, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from "chart.js";
import { useSurvey } from "@/stores/useSurvey";
import { getSessionSummary } from "@/api/questionnaire";

Chart.register(RadarController, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

const survey = useSurvey();
const canvasRef = ref<HTMLCanvasElement | null>(null);

onMounted(async () => {
  // const summary = await getSessionSummary(survey.sessionId);
  const summary = await getSessionSummary(survey.sessionId, survey.cityId);

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
</template> -->

<!-- ////////////////////////////////////////////////////////////// -->


<!-- /////////////////////////////////////////////////////////////////////////////// -->

<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
  Chart, RadarController, RadialLinearScale,
  PointElement, LineElement, Filler, Tooltip, Legend
} from "chart.js";
import { getAllCitiesRadar } from "@/api/questionnaire";

Chart.register(RadarController, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

const canvasRef = ref<HTMLCanvasElement | null>(null);
let chart: Chart | null = null;

function colorFor(i: number) {
  // Use comma-separated HSL/HSLA for canvas compatibility
  const hue = Math.round((360 / 12) * i); // stable palette
  return {
    border: `hsl(${hue}, 80%, 40%)`,
    fill:   `hsla(${hue}, 80%, 40%, 0.20)`,
  };
}

function makeShortLabels(fullLabels: string[], maxLen = 28): string[] {
  return fullLabels.map((s) => {
    const raw = String(s);

    // 1) take only the first paragraph (split on blank line), then first line
    const firstPara = raw.split(/\r?\n\r?\n/)[0] ?? raw;
    const firstLine = firstPara.split(/\r?\n/)[0] ?? firstPara;

    // 2) collapse whitespace and trim
    let t = firstLine.replace(/\s+/g, " ").trim();

    // 3) optionally remove trailing parenthetical like "(based on …)"
    t = t.replace(/\s*\(.*?\)\s*$/, "").trim();

    // 4) truncate
    if (t.length > maxLen) t = t.slice(0, maxLen) + "…";
    return t;
  });
}


onMounted(async () => {
  const data = await getAllCitiesRadar();
  const labels = data.categories ?? [];
  const cities = data.cities ?? [];
  const series = data.series ?? [];

  ///////////////////////
  const fullLabels = (data.categories ?? []).map(String);
  console.log("fulllabels",fullLabels);

  // Make compact axis labels (first line, max ~28 chars)
  // const shortLabels = fullLabels.map(s => {
  //   const firstLine = s.split("\n")[0].trim();
  //   return firstLine.length > 28 ? firstLine.slice(0, 28) + "…" : firstLine;
  // });
   const shortLabels = makeShortLabels(fullLabels, 68);
   console.log(shortLabels);
  //////////////////////77

  // Guard: need labels & at least one dataset
  if (!labels.length || !cities.length || !series.length || !canvasRef.value) return;

  // (Optional) quick debug to ensure canvas has non-zero size
  console.log('canvas rect', canvasRef.value.getBoundingClientRect());
  console.log(labels.length, series.map(s => s.length))
console.log("data",data)

  if (chart) chart.destroy();
  chart = new Chart(canvasRef.value, {
    type: "radar",
    data: {
      // labels,
      // labels: ["A","B","C","D","E","F","G"],
      labels: shortLabels,
      datasets: cities.map((city, i) => {
        const { border, fill } = colorFor(i);
        return {
          label: city,
          data: series[i] ?? [],
          // data: [1,2,3,4,3,2,1],
          borderColor: border,
          backgroundColor: fill,
          pointBackgroundColor: border,
          borderWidth: 2,
          pointRadius: 2,
          pointHoverRadius: 4,
          fill: true,
        };
      }),
    },
    // data: {
    //   labels: ["A","B","C","D","E","F","G"],
    //   datasets: [
    //     { label: "Test", data: [1,2,3,4,3,2,1], borderColor: "#0a0", backgroundColor: "rgba(0,170,0,.2)", fill: true }
    //   ]
    // },

    options: {
      responsive: true,
      maintainAspectRatio: false, // we set explicit attrs below
      animation: false,           // avoid layout timing issues during debug
      plugins: {
        legend: { position: "top" },
        tooltip: { enabled: true, 
            callbacks: {
          // show full category label in tooltip
          title: (items) => {
            const idx = items[0]?.dataIndex ?? 0;
            return fullLabels[idx] ?? "";
          },
        },
         },
      },
      scales: {
        r: {
          beginAtZero: true,
          suggestedMin: 0,
          suggestedMax: 5,
          ticks: { stepSize: 1 },
          grid: { circular: true, color: "rgba(0,0,0,0.15)" }, // ensure visible grid
          angleLines: { color: "rgba(0,0,0,0.12)" },
          pointLabels: { font: { size: 12 } },
        //   pointLabels: {
        //   // still use shortLabels, and make the font smaller
        //   callback: (_: any, idx: number) => shortLabels[idx] ?? "",
        //   font: { size: 10 },
        //   color: "#333",
        // },
        },
      },
      elements: { line: { tension: 0.0 } },
      layout: { padding: 10 },
    },
  });
});
</script>

<template>
  <div class="p-6" style="max-width: 980px; margin: 0 auto;">
    <h2 class="text-secondary" style="margin-bottom: .75rem;">Results (All Sessions, by City)</h2>

   
    <div style="position:relative; width:100%; height:480px;">
      <canvas ref="canvasRef" width="980" height="480" style="display:block; width:100%; height:100%;"></canvas>
    </div>
  </div>
</template>



<!-- //////////////////////////////////////////////////////////////////////// -->

