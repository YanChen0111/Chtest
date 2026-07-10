export const DEFAULT_PROJECT_ID = '00000000-0000-0000-0000-000000000101';
export const DEFAULT_REQUIREMENT_ID = '00000000-0000-0000-0000-000000000401';
export const DEFAULT_REVIEW_ID = '00000000-0000-0000-0000-000000000601';

const LATEST_REQUIREMENT_REVIEW_KEY = 'chtest.latestRequirementReview';
const LATEST_REQUIREMENT_DOCUMENT_KEY = 'chtest.latestRequirementDocument';
const LATEST_APPROVED_TEST_CASE_KEY = 'chtest.latestApprovedTestCase';

export interface LatestRequirementReviewContext {
  readonly projectId: string;
  readonly requirementId: string;
  readonly requirementReviewId: string;
}

export interface LatestRequirementDocumentContext extends LatestRequirementReviewContext {
  readonly requirementDocumentArtifactId: string;
  readonly documentNumber: string;
  readonly downloadUrl: string;
}

export interface LatestApprovedTestCaseContext {
  readonly projectId: string;
  readonly testCaseId: string;
  readonly sourceCandidateId?: string | null;
  readonly reviewStatus?: string | null;
}

export function saveLatestRequirementReviewContext(context: LatestRequirementReviewContext): void {
  if (!hasLocalStorage()) {
    return;
  }
  window.localStorage.setItem(LATEST_REQUIREMENT_REVIEW_KEY, JSON.stringify(context));
}

export function saveLatestRequirementDocumentContext(context: LatestRequirementDocumentContext): void {
  if (!hasLocalStorage()) {
    return;
  }
  window.localStorage.setItem(LATEST_REQUIREMENT_DOCUMENT_KEY, JSON.stringify(context));
}

export function saveLatestApprovedTestCaseContext(context: LatestApprovedTestCaseContext): void {
  if (!hasLocalStorage()) {
    return;
  }
  window.localStorage.setItem(LATEST_APPROVED_TEST_CASE_KEY, JSON.stringify(context));
}

export function getLatestRequirementReviewContext(): LatestRequirementReviewContext | null {
  if (!hasLocalStorage()) {
    return null;
  }
  const rawValue = window.localStorage.getItem(LATEST_REQUIREMENT_REVIEW_KEY);
  if (!rawValue) {
    return null;
  }
  try {
    const parsed = JSON.parse(rawValue) as unknown;
    if (!isContext(parsed)) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

export function getLatestRequirementDocumentContext(): LatestRequirementDocumentContext | null {
  if (!hasLocalStorage()) {
    return null;
  }
  const rawValue = window.localStorage.getItem(LATEST_REQUIREMENT_DOCUMENT_KEY);
  if (!rawValue) {
    return null;
  }
  try {
    const parsed = JSON.parse(rawValue) as unknown;
    if (!isDocumentContext(parsed)) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

export function getLatestApprovedTestCaseContext(): LatestApprovedTestCaseContext | null {
  if (!hasLocalStorage()) {
    return null;
  }
  const rawValue = window.localStorage.getItem(LATEST_APPROVED_TEST_CASE_KEY);
  if (!rawValue) {
    return null;
  }
  try {
    const parsed = JSON.parse(rawValue) as unknown;
    if (!isApprovedTestCaseContext(parsed)) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

function isContext(value: unknown): value is LatestRequirementReviewContext {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    return false;
  }
  const record = value as unknown as Record<string, unknown>;
  return (
    typeof record.projectId === 'string' &&
    typeof record.requirementId === 'string' &&
    typeof record.requirementReviewId === 'string'
  );
}

function isDocumentContext(value: unknown): value is LatestRequirementDocumentContext {
  if (!isContext(value)) {
    return false;
  }
  const record = value as unknown as Record<string, unknown>;
  return (
    typeof record.requirementDocumentArtifactId === 'string' &&
    typeof record.documentNumber === 'string' &&
    typeof record.downloadUrl === 'string'
  );
}

function isApprovedTestCaseContext(value: unknown): value is LatestApprovedTestCaseContext {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    return false;
  }
  const record = value as unknown as Record<string, unknown>;
  return typeof record.projectId === 'string' && typeof record.testCaseId === 'string';
}

function hasLocalStorage(): boolean {
  return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';
}
