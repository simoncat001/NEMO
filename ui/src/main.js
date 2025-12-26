import "./style.css";

const app = document.querySelector("#app");

app.innerHTML = `
  <main class="shell">
    <header>
      <p class="eyebrow">NEMO</p>
      <h1>Frontend workspace</h1>
      <p class="subtitle">
        This UI surface is ready for local development with Vite. Use it to build
        dashboards, onboarding, or any bespoke experiences for your lab.
      </p>
    </header>
    <section class="card">
      <h2>Quick start</h2>
      <ol>
        <li>Install dependencies with <code>npm install</code>.</li>
        <li>Start the dev server with <code>npm run dev</code>.</li>
        <li>Build production assets with <code>npm run build</code>.</li>
      </ol>
    </section>
  </main>
`;
