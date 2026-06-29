import { defineStore } from 'pinia';

import {
  createRequirement,
  getRequirementReview,
  startRequirementReview,
  type RequirementRead,
  type RequirementReviewRead,
  type RequirementReviewStartRead,
} from '../api/requirements';

const DEFAULT_PROJECT_ID = '00000000-0000-0000-0000-000000000101';

export const useRequirementsStore = defineStore('requirements', {
  state: () => ({
    projectId: DEFAULT_PROJECT_ID,
    requirement: null as RequirementRead | null,
    reviewStart: null as RequirementReviewStartRead | null,
    review: null as RequirementReviewRead | null,
    loading: false,
    errorMessage: '',
  }),
  actions: {
    async reviewRequirement(data: { title: string; content: string; sourceRef: string; contextArtifactIds: string[] }) {
      this.loading = true;
      this.errorMessage = '';
      this.requirement = null;
      this.reviewStart = null;
      this.review = null;
      try {
        const requirement = await createRequirement({
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
          model_provider: 'mock',
          model_name: 'mock-requirement-review',
          use_knowledge: false,
          context_artifact_ids: data.contextArtifactIds,
        });
        this.review = await getRequirementReview(requirement.id);
      } catch (error) {
        this.errorMessage = error instanceof Error ? error.message : '需求评审失败';
      } finally {
        this.loading = false;
      }
    },
  },
});
