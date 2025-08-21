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





