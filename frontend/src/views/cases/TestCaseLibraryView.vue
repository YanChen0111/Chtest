<template>
  <section class="test-case-library-page" aria-labelledby="test-case-library-title" data-test="test-case-library-page">
    <div class="test-case-library-heading">
      <div>
        <p class="eyebrow">测试用例库</p>
        <h2 id="test-case-library-title">用例库</h2>
        <p>集中查看已经人工评审入库的用例，保留来源、步骤、预期结果和评审状态，作为后续自动化草稿的输入资产。</p>
      </div>
      <a-space>
        <a-button data-test="open-case-import" type="primary" @click="importVisible = true">导入用例文档</a-button>
        <a-button data-test="export-test-cases" @click="exportTestCases" :disabled="filteredTestCases.length === 0">导出当前结果</a-button>
        <a-tag color="green">已评审用例</a-tag>
        <a-tag color="blue">只读浏览</a-tag>
      </a-space>
    </div>

    <a-alert v-if="store.errorMessage" data-test="test-case-library-error" type="error" :content="store.errorMessage" show-icon />
    <a-alert v-if="store.successMessage" data-test="test-case-library-success" type="success" :content="store.successMessage" show-icon />
    <a-button v-if="store.errorMessage" data-test="retry-test-case-library" size="small" @click="store.loadTestCases()">Retry loading</a-button>

    <div class="library-summary">
      <a-statistic title="已评审用例" :value="store.totalTestCases" />
      <label>
        <span>关键词</span>
        <a-input v-model="keyword" placeholder="按标题或标签筛选当前结果" allow-clear />
      </label>
      <label>
        <span>模块</span>
        <a-input v-model="moduleKeyword" placeholder="输入一级到五级模块" allow-clear />
      </label>
      <label>
        <span>状态</span>
        <a-radio-group v-model="statusFilter" type="button" size="small" class="case-filter-options">
          <a-radio :value="undefined">全部</a-radio>
          <a-radio value="active">启用中</a-radio>
          <a-radio value="archived">已归档</a-radio>
        </a-radio-group>
      </label>
      <label>
        <span>优先级</span>
        <a-radio-group v-model="priorityFilter" type="button" size="small" class="case-filter-options">
          <a-radio :value="undefined">全部</a-radio>
          <a-radio value="P0">P0</a-radio>
          <a-radio value="P1">P1</a-radio>
          <a-radio value="P2">P2</a-radio>
        </a-radio-group>
      </label>
      <label>
        <span>用例类型</span>
        <a-radio-group v-model="testTypeFilter" type="button" size="small" class="case-filter-options">
          <a-radio :value="undefined">全部</a-radio>
          <a-radio value="functional">功能测试</a-radio>
          <a-radio value="ui">界面测试</a-radio>
          <a-radio value="api">接口测试</a-radio>
          <a-radio value="regression">回归测试</a-radio>
        </a-radio-group>
      </label>
      <label>
        <span>来源</span>
        <a-radio-group v-model="sourceFilter" type="button" size="small" class="case-filter-options">
          <a-radio :value="undefined">全部</a-radio>
          <a-radio value="imported">导入</a-radio>
          <a-radio value="generated">AI 生成</a-radio>
          <a-radio value="manual">手动</a-radio>
        </a-radio-group>
      </label>
    </div>

    <a-card class="library-action-strip" :bordered="false">
      <div>
        <strong>用例库操作</strong>
        <span>导入后直接进入库内，可筛选、查看、归档或恢复；AI 生成用例仍需先在用例生成评审页审核。</span>
      </div>
      <a-space>
        <a-tag color="blue">当前 {{ filteredTestCases.length }} 条</a-tag>
        <a-button size="small" @click="store.loadTestCases()">刷新列表</a-button>
      </a-space>
    </a-card>

    <div class="library-layout">
      <a-card class="library-panel case-list-panel" :bordered="false">
        <template #title>用例列表</template>
        <a-spin data-test="test-case-library-loading" :loading="store.loadingGeneration">
          <a-list v-if="filteredTestCases.length > 0" :data="filteredTestCases" :bordered="false">
            <template #item="{ item }">
              <a-list-item
                data-test="recent-test-case-row"
                class="test-case-list-item"
                :class="{ active: item.id === selectedCase?.id }"
                @click="store.selectedTestCaseId = item.id"
              >
                <a-space direction="vertical" size="mini">
                  <strong>{{ item.title }}</strong>
                  <small v-if="caseModulePath(item)" class="case-module-path">{{ caseModulePath(item) }}</small>
                  <a-space wrap>
                    <a-tag color="red">{{ priorityLabel(item.priority) }}</a-tag>
                    <a-tag color="blue">{{ testTypeLabel(item.test_type) }}</a-tag>
                    <a-tag>{{ reviewStatusLabel(item.review_status) }}</a-tag>
                    <a-tag>{{ caseStatusLabel(item.status) }}</a-tag>
                  </a-space>
                  <a-button data-test="resume-test-case" size="mini" @click.stop="store.selectedTestCaseId = item.id">查看详情</a-button>
                </a-space>
              </a-list-item>
            </template>
          </a-list>
          <a-empty v-else-if="!store.loadingGeneration" description="暂无已评审用例" />
        </a-spin>
      </a-card>

      <a-card class="library-panel case-detail-panel" :bordered="false">
        <template #title>用例详情</template>
        <template v-if="selectedCase">
          <a-descriptions :column="2" bordered size="small">
            <a-descriptions-item label="标题">{{ selectedCase.title }}</a-descriptions-item>
            <a-descriptions-item label="状态">{{ caseStatusLabel(selectedCase.status) }}</a-descriptions-item>
            <a-descriptions-item label="优先级">{{ priorityLabel(selectedCase.priority) }}</a-descriptions-item>
            <a-descriptions-item label="类型">{{ testTypeLabel(selectedCase.test_type) }}</a-descriptions-item>
            <a-descriptions-item label="评审状态">{{ reviewStatusLabel(selectedCase.review_status) }}</a-descriptions-item>
            <a-descriptions-item label="来源">{{ sourceTypeLabel(selectedCase.source_type) }}</a-descriptions-item>
            <a-descriptions-item label="模块路径" :span="2">{{ caseModulePath(selectedCase) || '未分类' }}</a-descriptions-item>
            <a-descriptions-item label="来源说明" :span="2">
              {{ selectedCase.source_type === 'imported' ? '导入用例文档' : selectedCase.source_candidate_id ? 'AI 评审候选' : '手动或外部来源' }}
            </a-descriptions-item>
            <a-descriptions-item label="前置条件" :span="2">
              {{ selectedCase.precondition ?? '无' }}
            </a-descriptions-item>
            <a-descriptions-item label="标签" :span="2">{{ listText(selectedCase.tags) }}</a-descriptions-item>
          </a-descriptions>

          <div class="case-evidence-grid">
            <section>
              <h3>步骤</h3>
              <ol>
                <li v-for="step in selectedCase.steps" :key="step">{{ step }}</li>
              </ol>
            </section>
            <section>
              <h3>预期结果</h3>
              <ol>
                <li v-for="result in selectedCase.expected_results" :key="result">{{ result }}</li>
              </ol>
            </section>
          </div>
          <div class="case-detail-actions">
            <a-button
              v-if="selectedCase.status === 'active'"
              data-test="archive-selected-case"
              status="warning"
              :loading="store.loadingGeneration"
              @click="store.setTestCaseStatus(selectedCase.id, 'archived')"
            >
              归档用例
            </a-button>
            <a-button
              v-else
              data-test="restore-selected-case"
              type="primary"
              :loading="store.loadingGeneration"
              @click="store.setTestCaseStatus(selectedCase.id, 'active')"
            >
              恢复使用
            </a-button>
          </div>
        </template>

        <a-empty v-else description="请选择用例" />
      </a-card>
    </div>

    <a-drawer v-model:visible="importVisible" title="导入用例文档" :width="560" unmount-on-close>
      <div class="import-drawer-content">
        <a-alert type="info" show-icon content="支持 JSON、CSV、TXT、Markdown。导入会按标题去重，重复标题自动跳过。" />
        <label class="import-file-field">
          <span>选择文件</span>
          <input data-test="case-import-file" type="file" accept=".xlsx,.xls,.json,.csv,.tsv,.txt,.md,.markdown,text/*,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" @change="handleImportFile" />
        </label>
        <div v-if="importFileName" class="import-file-name">{{ importFileName }}</div>
        <a-textarea v-model="importPreviewText" :auto-size="{ minRows: 8, maxRows: 16 }" readonly placeholder="选择文件后这里会显示待导入条目预览" />
        <a-alert v-if="importItems.length" type="success" show-icon :content="`已解析 ${importItems.length} 条用例，可导入`" />
        <a-empty v-else description="请选择用例文档" />
      </div>
      <template #footer>
        <a-space>
          <a-button @click="importVisible = false">取消</a-button>
          <a-button data-test="confirm-case-import" type="primary" :loading="store.loadingGeneration" :disabled="importItems.length === 0" @click="confirmImport">导入到用例库</a-button>
        </a-space>
      </template>
    </a-drawer>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import * as XLSX from 'xlsx';

import type { TestCaseImportItem } from '../../api/cases';
import { useCasesStore } from '../../stores/cases';

const store = useCasesStore();
const keyword = ref('');
const moduleKeyword = ref('');
const statusFilter = ref<'active' | 'archived' | undefined>();
const priorityFilter = ref<string | undefined>();
const testTypeFilter = ref<string | undefined>();
const sourceFilter = ref<string | undefined>();
const importVisible = ref(false);
const importFileName = ref('');
const importPreviewText = ref('');
const importItems = ref<TestCaseImportItem[]>([]);

const filteredTestCases = computed(() => {
  const value = keyword.value.trim().toLowerCase();
  const moduleValue = moduleKeyword.value.trim().toLowerCase();
  return store.testCases.filter((testCase) => {
    if (statusFilter.value && testCase.status !== statusFilter.value) return false;
    if (priorityFilter.value && testCase.priority !== priorityFilter.value) return false;
    if (testTypeFilter.value && testCase.test_type !== testTypeFilter.value) return false;
    if (sourceFilter.value && testCase.source_type !== sourceFilter.value) return false;
    if (moduleValue && !caseModulePath(testCase).toLowerCase().includes(moduleValue)) return false;
    if (!value) return true;
    return [testCase.title, testCase.priority, testCase.test_type, testCase.review_status, ...testCase.tags]
      .join(' ')
      .toLowerCase()
      .includes(value);
  });
});

function caseModulePath(testCase: { input_data: Record<string, unknown> }): string {
  const metadata = testCase.input_data?.__chtest_case_format as Record<string, unknown> | undefined;
  const levels = Array.isArray(metadata?.module_levels) ? metadata.module_levels : [];
  return levels.map(String).map((item) => item.trim()).filter(Boolean).join(' / ');
}

const selectedCase = computed(() => {
  if (filteredTestCases.value.some((testCase) => testCase.id === store.selectedTestCaseId)) {
    return store.selectedTestCase;
  }
  return filteredTestCases.value[0] ?? null;
});

function listText(items: string[]): string {
  return items.length > 0 ? items.join(', ') : '无';
}

function priorityLabel(priority: string): string {
  const labels: Record<string, string> = {
    p0: 'P0',
    p1: 'P1',
    p2: 'P2',
    high: '高',
    medium: '中',
    low: '低',
  };
  return labels[priority] ?? priority;
}

function testTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    functional: '功能',
    ui: '界面',
    api: '接口',
    regression: '回归',
  };
  return labels[type] ?? type;
}

function reviewStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    approved: '已通过',
    approved_after_edit: '编辑后通过',
    rejected: '已拒绝',
    needs_optimization: '需要优化',
  };
  return labels[status] ?? status;
}

function caseStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    active: '启用',
    archived: '已归档',
    draft: '草稿',
  };
  return labels[status] ?? status;
}

function sourceTypeLabel(sourceType: string): string {
  const labels: Record<string, string> = {
    generated: 'AI 生成',
    manual: '手动',
    imported: '导入',
  };
  return labels[sourceType] ?? sourceType;
}

function normalizeImportItem(value: Record<string, unknown>): TestCaseImportItem | null {
  const title = String(value.title ?? value.name ?? value['用例名称'] ?? '').trim();
  if (!title) return null;
  const listValue = (candidate: unknown): string[] => {
    if (Array.isArray(candidate)) return candidate.map(String).filter(Boolean);
    if (typeof candidate === 'string') return candidate.split(/\r?\n|[;；]/).map((item) => item.trim()).filter(Boolean);
    return [];
  };
  const inputData = value.input_data && typeof value.input_data === 'object' && !Array.isArray(value.input_data)
    ? value.input_data as Record<string, unknown>
    : {};
  return {
    title,
    priority: String(value.priority ?? value['优先级'] ?? 'P2'),
    test_type: String(value.test_type ?? value.type ?? value['用例类型'] ?? 'functional'),
    precondition: value.precondition || value['前置条件'] ? String(value.precondition ?? value['前置条件']) : null,
    steps: listValue(value.steps ?? value.step ?? value['步骤描述']),
    expected_results: listValue(value.expected_results ?? value.expected ?? value.expected_result ?? value['预期结果']),
    input_data: {
      ...inputData,
      __chtest_case_format: {
        case_id: String(value.case_id ?? value['编号'] ?? '').trim() || undefined,
        module_levels: [1, 2, 3, 4, 5].map((level) => String(value[`module_${level}`] ?? value[`${['一', '二', '三', '四', '五'][level - 1]}级模块`] ?? '').trim()),
        created_at: String(value.created_at ?? value['创建时间'] ?? '').trim() || undefined,
        updated_at: String(value.updated_at ?? value['更新时间'] ?? '').trim() || undefined,
        notes: String(value.notes ?? value['备注'] ?? '').trim() || undefined,
        maintainer: String(value.maintainer ?? value['维护人'] ?? '').trim() || undefined,
      },
    },
    tags: listValue(value.tags),
  };
}

function parseDelimited(text: string, delimiter: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let cell = '';
  let quoted = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    if (char === '"') {
      if (quoted && text[index + 1] === '"') { cell += '"'; index += 1; }
      else quoted = !quoted;
    } else if (char === delimiter && !quoted) {
      row.push(cell.trim()); cell = '';
    } else if ((char === '\n' || char === '\r') && !quoted) {
      if (char === '\r' && text[index + 1] === '\n') index += 1;
      row.push(cell.trim()); cell = '';
      if (row.some((item) => item !== '')) rows.push(row);
      row = [];
    } else cell += char;
  }
  row.push(cell.trim());
  if (row.some((item) => item !== '')) rows.push(row);
  return rows;
}

function parseImportDocument(text: string, extension: string): TestCaseImportItem[] {
  if (extension === 'json') {
    const parsed = JSON.parse(text) as unknown;
    const values = Array.isArray(parsed)
      ? parsed
      : parsed && typeof parsed === 'object' && Array.isArray((parsed as { items?: unknown[] }).items)
        ? (parsed as { items: unknown[] }).items
        : [];
    return values
      .map((item) => (item && typeof item === 'object' ? normalizeImportItem(item as Record<string, unknown>) : null))
      .filter((item): item is TestCaseImportItem => Boolean(item));
  }
  if (extension === 'csv' || extension === 'tsv' || extension === 'txt') {
    const firstLine = text.split(/\r?\n/, 1)[0] ?? '';
    const delimiter = extension === 'csv' && !firstLine.includes('\t') ? ',' : '\t';
    const rows = parseDelimited(text, delimiter);
    if (rows.length < 2) return [];
    const aliases: Record<string, string> = {
      '一级模块': 'module_1', '二级模块': 'module_2', '三级模块': 'module_3', '四级模块': 'module_4', '五级模块': 'module_5',
      '用例名称': 'title', '优先级': 'priority', '用例类型': 'test_type', '创建时间': 'created_at', '更新时间': 'updated_at',
      '前置条件': 'precondition', '步骤描述': 'steps', '预期结果': 'expected_results', '备注': 'notes', '维护人': 'maintainer', '编号': 'case_id',
    };
    const headers = rows[0].map((header) => header.replace(/^\uFEFF/, '').trim());
    if (!headers[0] || headers[0].trim() === '') headers[0] = '编号';
    return rows.slice(1)
      .map((values) => normalizeImportItem(Object.fromEntries(values.map((value, index) => [aliases[headers[index]] ?? headers[index], value]))))
      .filter((item): item is TestCaseImportItem => Boolean(item));
  }
  const sections = text.split(/\n(?=#{1,3}\s)/).map((section) => section.trim()).filter(Boolean);
  return sections
    .map((section) => {
      const lines = section.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
      const title = lines[0]?.replace(/^#{1,3}\s*/, '') ?? '';
      return normalizeImportItem({
        title,
        steps: lines.slice(1).filter((line) => /^[-*\d.]/.test(line)).map((line) => line.replace(/^[-*\d.\s]+/, '')),
        expected_results: ['导入后请根据实际结果补充'],
      });
    })
    .filter((item): item is TestCaseImportItem => Boolean(item));
}

function parseXlsxDocument(buffer: ArrayBuffer): TestCaseImportItem[] {
  const workbook = XLSX.read(buffer, { type: 'array', cellDates: true });
  const sheet = workbook.Sheets[workbook.SheetNames[0]];
  if (!sheet) return [];
  const rows = XLSX.utils.sheet_to_json<unknown[]>(sheet, { header: 1, defval: '', raw: false });
  if (rows.length < 2) return [];
  const headers = (rows[0] ?? []).map((header) => String(header).replace(/^\uFEFF/, '').trim());
  if (!headers[0]) headers[0] = '编号';
  if (!headers.some((header) => ['用例名称', 'title', 'name'].includes(header))) {
    throw new Error('未找到“用例名称”列，请选择测试用例格式的 XLSX 文件。');
  }
  const aliases: Record<string, string> = {
    '一级模块': 'module_1', '二级模块': 'module_2', '三级模块': 'module_3', '四级模块': 'module_4', '五级模块': 'module_5',
    '用例名称': 'title', '优先级': 'priority', '用例类型': 'test_type', '创建时间': 'created_at', '更新时间': 'updated_at',
    '前置条件': 'precondition', '步骤描述': 'steps', '预期结果': 'expected_results', '备注': 'notes', '维护人': 'maintainer', '编号': 'case_id',
  };
  return rows.slice(1)
    .map((values) => normalizeImportItem(Object.fromEntries(values.map((value, index) => [aliases[headers[index]] ?? headers[index], String(value ?? '')]))))
    .filter((item): item is TestCaseImportItem => Boolean(item));
}

async function handleImportFile(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  importFileName.value = file.name;
  try {
    const extension = file.name.toLowerCase().split('.').pop() ?? 'txt';
    importItems.value = extension === 'xlsx' || extension === 'xls'
      ? parseXlsxDocument(await file.arrayBuffer())
      : parseImportDocument(await file.text(), extension);
    importPreviewText.value = importItems.value.map((item, index) => `${index + 1}. ${item.title}`).join('\n');
  } catch (error) {
    importItems.value = [];
    importPreviewText.value = error instanceof Error ? `文件解析失败：${error.message}` : '文件解析失败';
  }
}

async function confirmImport() {
  const batches: TestCaseImportItem[][] = [];
  for (let index = 0; index < importItems.value.length; index += 400) {
    batches.push(importItems.value.slice(index, index + 400));
  }
  let importedCount = 0;
  let skippedCount = 0;
  for (const batch of batches) {
    const result = await store.importCases(batch);
    if (!result) return;
    importedCount += result.imported_count;
    skippedCount += result.skipped_count;
  }
  store.successMessage = `已导入 ${importedCount} 条用例${skippedCount ? `，跳过 ${skippedCount} 条重复标题` : ''}`;
  if (importedCount || skippedCount) {
    importVisible.value = false;
    importItems.value = [];
    importPreviewText.value = '';
    importFileName.value = '';
    const input = document.querySelector('[data-test="case-import-file"]') as HTMLInputElement | null;
    if (input) input.value = '';
  }
}

function exportTestCases() {
  const headers = ['编号', '一级模块', '二级模块', '三级模块', '四级模块', '五级模块', '用例名称', '优先级', '用例类型', '创建时间', '更新时间', '前置条件', '步骤描述', '预期结果', '备注', '维护人'];
  const escapeCell = (value: unknown) => {
    const text = Array.isArray(value) ? value.map((item, index) => `#${index + 1}.${item}`).join('\n') : String(value ?? '');
    return /[\t\n\r"]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
  };
  const rows = filteredTestCases.value.map((item) => {
    const metadata = (item.input_data?.__chtest_case_format ?? {}) as Record<string, unknown>;
    const levels = Array.isArray(metadata.module_levels) ? metadata.module_levels : [];
    return [metadata.case_id, ...[0, 1, 2, 3, 4].map((index) => levels[index]), item.title, item.priority, item.test_type, metadata.created_at, metadata.updated_at, item.precondition, item.steps, item.expected_results, metadata.notes, metadata.maintainer].map(escapeCell).join('\t');
  });
  const blob = new Blob([[headers.join('\t'), ...rows].join('\r\n')], { type: 'text/tab-separated-values;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'chtest-test-cases.tsv';
  link.click();
  URL.revokeObjectURL(url);
}

onMounted(() => {
  void store.loadTestCases();
});
</script>

<style scoped>
.test-case-library-page {
  display: grid;
  gap: 18px;
}

.case-filter-options {
  display: flex;
  flex-wrap: wrap;
  max-width: 100%;
}

.test-case-library-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.test-case-library-heading h2,
.test-case-library-heading p {
  margin: 0;
}

.test-case-library-heading h2 {
  font-size: 26px;
}

.test-case-library-heading p:not(.eyebrow) {
  margin-top: 10px;
  max-width: 780px;
  color: #5b6472;
  line-height: 1.7;
}

.library-summary {
  display: grid;
  grid-template-columns: minmax(180px, 240px) minmax(260px, 420px) minmax(160px, 220px);
  gap: 16px;
  align-items: end;
}

.library-action-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border: 1px solid #dbe6f3;
  background: #f8fbff;
}

.library-action-strip > div:first-child {
  display: grid;
  gap: 4px;
}

.library-action-strip span {
  color: #667085;
  font-size: 12px;
}

.library-summary label {
  display: grid;
  gap: 7px;
  color: #344054;
  font-weight: 700;
}

.library-layout {
  display: grid;
  grid-template-columns: minmax(340px, 0.85fr) minmax(0, 1.35fr);
  gap: 16px;
  align-items: start;
}

.library-panel {
  border-radius: 8px;
}

.case-list-panel {
  position: sticky;
  top: 16px;
  max-height: calc(100vh - 220px);
  overflow: hidden;
}

.case-list-panel :deep(.arco-card-body) {
  max-height: calc(100vh - 280px);
  overflow-y: auto;
}

.test-case-list-item {
  cursor: pointer;
  border-radius: 8px;
}

.test-case-list-item.active {
  background: #eff6ff;
}

.case-module-path {
  color: #667085;
  line-height: 1.5;
  overflow-wrap: anywhere;
}

.case-evidence-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 18px;
}

.case-evidence-grid section {
  padding: 14px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
}

.case-evidence-grid h3 {
  margin: 0 0 10px;
  font-size: 16px;
}

.case-evidence-grid ol {
  display: grid;
  gap: 8px;
  margin: 0;
  padding-left: 18px;
}

.case-detail-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

.import-drawer-content {
  display: grid;
  gap: 14px;
}

.import-file-field {
  display: grid;
  gap: 8px;
  color: #344054;
  font-weight: 700;
}

.import-file-name {
  padding: 8px 10px;
  border: 1px solid #dbe6f3;
  border-radius: 6px;
  color: #475467;
  background: #f8fafc;
  font-size: 12px;
}

@media (max-width: 980px) {
  .library-summary,
  .library-layout,
  .case-evidence-grid {
    grid-template-columns: 1fr;
  }

  .case-list-panel {
    position: static;
    max-height: none;
  }

  .case-list-panel :deep(.arco-card-body) {
    max-height: none;
  }

  .library-action-strip {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
