import { defineStore } from 'pinia';

import {
  createRequirement,
  createRequirementDocument,
  getRequirementReview,
  listRequirementDocuments,
  startRequirementReview,
  type ClarificationAnswer,
  type RequirementDocumentRead,
  type RequirementRead,
  type RequirementReviewRead,
  type RequirementReviewStartRead,
} from '../api/requirements';
import { DEFAULT_PROJECT_ID, saveLatestRequirementDocumentContext, saveLatestRequirementReviewContext } from './workflowContext';

export const useRequirementsStore = defineStore('requirements', {
  state: () => ({
    projectId: DEFAULT_PROJECT_ID,
    requirement: null as RequirementRead | null,
    reviewStart: null as RequirementReviewStartRead | null,
    review: null as RequirementReviewRead | null,
    documents: [] as RequirementDocumentRead[],
    createdDocument: null as RequirementDocumentRead | null,
    loading: false,
    loadingDocument: false,
    errorMessage: '',
  }),
  actions: {
    async reviewRequirement(data: {
      title: string;
      content: string;
      sourceRef: string;
      contextArtifactIds: string[];
      supplementText?: string;
      clarificationAnswers?: ClarificationAnswer[];
    }) {
      this.loading = true;
      this.errorMessage = '';
      this.reviewStart = null;
      this.review = null;
      this.createdDocument = null;
      try {
        const requirement =
          this.requirement?.title === data.title && this.requirement?.content === data.content
            ? this.requirement
            : await createRequirement({
                project_id: this.projectId,
                module_id: null,
                title: data.title,
                content: data.content,
                source_type: 'manual',
                source_ref: data.sourceRef || null,
              });
        this.requirement = requirement;
        this.reviewStart = await startRequirementReview(requirement.id, {
          prompt_version: 'requirement_review:v1',
          skill_version: 'requirement-review-skill:v1',
          use_knowledge: false,
          context_artifact_ids: data.contextArtifactIds,
          supplement_text: data.supplementText || null,
          clarification_answers: data.clarificationAnswers ?? [],
        });
        this.review = await getRequirementReview(requirement.id);
        saveLatestRequirementReviewContext({
          projectId: this.projectId,
          requirementId: requirement.id,
          requirementReviewId: this.review.id,
        });
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '需求评审失败';
      } finally {
        this.loading = false;
      }
    },
    async loadRequirementDocuments() {
      this.errorMessage = '';
      try {
        const documents = await listRequirementDocuments(this.projectId);
        this.documents = documents.items;
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '需求文档加载失败';
      }
    },
    async generateRequirementDocument() {
      if (!this.requirement || !this.review) {
        this.errorMessage = '请先完成需求评审';
        return;
      }
      this.loadingDocument = true;
      this.errorMessage = '';
      try {
        this.createdDocument = await createRequirementDocument(this.requirement.id, {
          requirement_review_id: this.review.id,
          version: 'v1',
          status: this.review.clarification_questions.length > 0 ? 'draft' : 'confirmed',
        });
        saveLatestRequirementDocumentContext({
          projectId: this.projectId,
          requirementId: this.createdDocument.requirement_id,
          requirementReviewId: this.createdDocument.requirement_review_id,
          requirementDocumentArtifactId: this.createdDocument.artifact_id,
          documentNumber: this.createdDocument.document_number,
          downloadUrl: this.createdDocument.download_url,
        });
        await this.loadRequirementDocuments();
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '需求文档生成失败';
      } finally {
        this.loadingDocument = false;
      }
    },
  },
});
