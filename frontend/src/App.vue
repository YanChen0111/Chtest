<template>
  <main class="workbench">
    <section class="hero" aria-labelledby="page-title">
      <p class="eyebrow">Chtest</p>
      <h1 id="page-title">AI 测试工作台</h1>
      <p class="summary">围绕需求评审、用例生成和自动化执行，沉淀可追溯的测试证据。</p>
    </section>

    <section class="quick-start" aria-label="核心入口">
      <article class="panel">
        <span class="panel-index">01</span>
        <h2>需求评审</h2>
        <p>粘贴需求，生成六维评分、澄清问题、风险项和测试设计建议。</p>
      </article>

      <article class="panel">
        <span class="panel-index">02</span>
        <h2>用例生成评审</h2>
        <p>把 AI 候选用例放进人工评审流程，确认后再进入用例库。</p>
      </article>

      <article class="panel">
        <span class="panel-index">03</span>
        <h2>执行证据</h2>
        <p>让测试运行、工件、报告和 AI 任务记录形成可复查的证据链。</p>
      </article>
    </section>
  </main>
</template>

<style scoped>
.workbench {
  min-height: 100vh;
  padding: 48px;
  color: #1f2937;
  background: #f5f7fb;
}

.hero {
  max-width: 760px;
  margin-bottom: 32px;
}

.eyebrow {
  margin: 0 0 12px;
  color: #2563eb;
  font-size: 14px;
  font-weight: 700;
}

h1 {
  margin: 0;
  font-size: 40px;
  line-height: 1.2;
}

.summary {
  max-width: 620px;
  margin: 16px 0 0;
  color: #4b5563;
  font-size: 16px;
  line-height: 1.7;
}

.quick-start {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.panel {
  min-height: 168px;
  padding: 22px;
  border: 1px solid #d8dee9;
  border-radius: 8px;
  background: #ffffff;
}

.panel-index {
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
}

h2 {
  margin: 18px 0 10px;
  font-size: 20px;
}

.panel p {
  margin: 0;
  color: #5b6472;
  line-height: 1.65;
}

@media (max-width: 820px) {
  .workbench {
    padding: 28px 20px;
  }

  .quick-start {
    grid-template-columns: 1fr;
  }

  h1 {
    font-size: 30px;
  }
}
</style>
