import { apiClient } from './client';

export interface ProjectSettingsProject {
  readonly id: string;
  readonly name: string;
  readonly default_language: string | null;
  readonly default_test_type: string | null;
}

export interface ProjectModule {
  readonly id: string;
  readonly name: string;
  readonly path: string;
  readonly level: number;
  readonly status: string;
}

export interface ProjectRepository {
  readonly id: string;
  readonly name: string;
  readonly local_path: string;
  readonly default_base_branch: string | null;
  readonly language_hint: string | null;
  readonly status: string;
}

export interface ProjectEnvironment {
  readonly id: string;
  readonly name: string;
  readonly variables_json: Record<string, unknown>;
  readonly status: string;
}

export interface ProjectTestCommand {
  readonly id: string;
  readonly name: string;
  readonly command: string;
  readonly working_directory: string;
  readonly command_type: string;
  readonly timeout_seconds: number;
  readonly parse_junit: boolean;
  readonly parse_coverage: boolean;
  readonly status: string;
}

export interface ProjectSettings {
  readonly project: ProjectSettingsProject;
  readonly modules: ProjectModule[];
  readonly repositories: ProjectRepository[];
  readonly environments: ProjectEnvironment[];
  readonly test_commands: ProjectTestCommand[];
  readonly tool_definitions: Record<string, unknown>[];
}

export async function getProjectSettings(projectId: string): Promise<ProjectSettings> {
  return apiClient.getJson<ProjectSettings>(`/projects/${projectId}/settings`);
}
