<!-- ORIGINAL WELL WORKING NON TAILWIND SETUP -->

<script setup lang="ts"></script>

<template>
  <div class="app-root">
    <header
      style="
        padding: 0.75rem 3rem;
        display: flex;
        align-items: center;   
        gap: 0.75rem;
      "
    >
      <img
        src="/LOGO-FON-FINAL.png"
        alt="U_CAN Logo"
        style="width: 98px; height: 55px; object-fit: contain; display:block;"
      />

   
      <div
        style="
          margin-left: 2.25rem;      
          transform: translateY(8px);
          font-family: 'Nunito Sans', sans-serif; 
          color: #003399;
        "
      >
        <strong style="font-size: 1rem; line-height: 1.2;">
          U_CAN Climate Readiness Tool
        </strong>
      </div>
    </header>

    <main style="padding: 1rem">
      <RouterView />
    </main>
  </div>
</template>



<!-- SECOND NOW WELL - WORKING TAILWIND SETUP -->
<!-- <template>
  <div class="tw-min-h-screen tw-flex tw-flex-col tw-bg-[rgb(248,247,243)]">
    <header class="tw-w-full tw-flex tw-items-center tw-gap-3 tw-py-3 tw-px-12">
      <img
        src="/LOGO-FON-FINAL.png"
        alt="U_CAN Logo"
        class="tw-w-[98px] tw-h-[55px] tw-object-contain tw-block"
      />
     
      <div class="tw-ml-9 tw-relative tw-translate-y-[8px] tw-font-nunito tw-text-brandTertiary">
        <strong class="tw-text-base tw-leading-tight">
          U_CAN Climate Readiness Tool
        </strong>
      </div>
    </header>

   
    <main class="tw-flex-1 tw-w-full tw-px-4 tw-py-4">
      <RouterView />
    </main>

  </div>
</template> -->



