<template>
  <section class="cicd-page" aria-labelledby="cicd-title">
    <div class="cicd-heading">
      <div>
        <p class="eyebrow">Local CI/CD Quality</p>
        <h2 id="cicd-title">CI/CD 质量中心</h2>
        <p>从本地 diff 创建 CICDRun，查看 changed files 和 mock risk_analysis 证据。</p>
      </div>
      <a-space>
        <a-tag color="green">local_diff</a-tag>
        <a-tag color="blue">manual / local</a-tag>
      </a-space>
    </div>

    <a-alert v-if="store.errorMessage" type="error" :content="store.errorMessage" show-icon />

    <div class="cicd-layout">
      <a-card class="cicd-panel" :bordered="false">
        <template #title>本地变更输入</template>
        <form class="cicd-form" @submit.prevent="createRun">
          <label>
            <span>Project ID</span>
            <a-input v-model="store.projectId" />
          </label>
          <label>
            <span>Repository ID</span>
            <a-input v-model="store.repositoryId" />
          </label>
          <div class="ref-grid">
            <label>
              <span>Base Ref</span>
              <a-input v-model="store.baseRef" />
            </label>
            <label>
              <span>Head Ref</span>
              <a-input v-model="store.headRef" />
            </label>
          </div>
          <label>
            <span>Unified Diff</span>
            <a-textarea v-model="store.diffText" :auto-size="{ minRows: 8, maxRows: 14 }" />
          </label>
          <a-space wrap>
            <a-button data-test="create-cicd-run" html-type="submit" type="primary" :loading="store.loading">
              创建 CICDRun
            </a-button>
            <a-button data-test="analyze-cicd-run" :disabled="!store.run" :loading="store.loading" @click="analyzeRun">
              生成风险分析
            </a-button>
          </a-space>
        </form>
      </a-card>

      <div class="cicd-detail">
        <a-card class="cicd-panel" :bordered="false">
          <template #title>变更证据</template>
          <template v-if="store.run">
            <div class="status-strip">
              <div>
                <span>Status</span>
                <strong>{{ store.run.status }}</strong>
              </div>
              <div>
                <span>Risk</span>
                <strong>{{ store.run.overall_risk }}</strong>
              </div>
              <div>
                <span>Files</span>
                <strong>{{ store.run.changed_files.length }}</strong>
              </div>
            </div>
            <a-table
              :columns="changedFileColumns"
              :data="store.run.changed_files"
              :pagination="false"
              row-key="id"
              size="small"
            />
          </template>
          <a-empty v-else description="创建后展示 changed files 证据" />
        </a-card>

        <a-card class="cicd-panel" :bordered="false">
          <template #title>风险分析证据</template>
          <template v-if="store.run?.analysis_artifacts.length">
            <a-table
              :columns="artifactColumns"
              :data="store.run.analysis_artifacts"
              :pagination="false"
              row-key="id"
              size="small"
            />
          </template>
          <a-empty v-else description="生成风险分析后展示 risk_analysis artifact" />
        </a-card>

        <a-card class="cicd-panel" :bordered="false">
          <template #title>最近 CI/CD Runs</template>
          <a-table :columns="runColumns" :data="store.runs" :pagination="false" row-key="id" size="small" />
        </a-card>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useCICDStore } from '../../stores/cicd';

const store = useCICDStore();

const changedFileColumns = [
  { title: '路径', dataIndex: 'path' },
  { title: '类型', dataIndex: 'change_type' },
  { title: '角色', dataIndex: 'file_role' },
  { title: '风险', dataIndex: 'risk_level' },
  { title: '原因', dataIndex: 'risk_reasons' },
];

const artifactColumns = [
  { title: '类型', dataIndex: 'artifact_type' },
  { title: '路径', dataIndex: 'file_path' },
  { title: '大小', dataIndex: 'size_bytes' },
];

const runColumns = [
  { title: 'Run', dataIndex: 'id' },
  { title: '状态', dataIndex: 'status' },
  { title: '风险', dataIndex: 'overall_risk' },
  { title: 'Base', dataIndex: 'base_ref' },
  { title: 'Head', dataIndex: 'head_ref' },
];

function createRun() {
  void store.createRun();
}

function analyzeRun() {
  void store.analyzeRun();
}
</script>

<style scoped>
.cicd-page {
  display: grid;
  gap: 18px;
}

.cicd-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.cicd-heading h2,
.cicd-heading p {
  margin: 0;
}

.cicd-heading h2 {
  font-size: 26px;
}

.cicd-heading p:not(.eyebrow) {
  margin-top: 10px;
  max-width: 760px;
  color: #5b6472;
  line-height: 1.7;
}

.cicd-layout {
  display: grid;
  grid-template-columns: minmax(340px, 0.72fr) minmax(0, 1.5fr);
  gap: 16px;
}

.cicd-detail {
  display: grid;
  gap: 16px;
}

.cicd-panel {
  border-radius: 8px;
}

.cicd-form {
  display: grid;
  gap: 14px;
}

.cicd-form label {
  display: grid;
  gap: 7px;
  color: #344054;
  font-weight: 700;
}

.ref-grid,
.status-strip {
  display: grid;
  gap: 10px;
}

.ref-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.status-strip {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-bottom: 14px;
}

.status-strip div {
  min-height: 70px;
  padding: 12px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
}

.status-strip span,
.status-strip strong {
  display: block;
}

.status-strip span {
  color: #64748b;
}

.status-strip strong {
  margin-top: 8px;
  color: #0f172a;
  font-size: 20px;
}

@media (max-width: 980px) {
  .cicd-layout,
  .ref-grid {
    grid-template-columns: 1fr;
  }

  .status-strip {
    grid-template-columns: repeat(2, minmax(120px, 1fr));
  }
}
</style>
