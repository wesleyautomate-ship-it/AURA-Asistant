
import { apiGet, apiPost } from "./api";
import type { PackageDefinition } from '../utils/packageOrchestration';

export type RunStatus = 'queued' | 'running' | 'completed' | 'failed';
export type StepStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface WorkflowStepRun {
  id: string;
  title: string;
  status: StepStatus;
  logs: string[];
}

export interface WorkflowRun {
  id: string;
  packageId: string;
  packageName: string;
  status: RunStatus;
  startedAt: string;
  completedAt?: string;
  steps: WorkflowStepRun[];
  context?: Record<string, any>;
}

export function listRuns(): Promise<WorkflowRun[]> {
  return apiGet<WorkflowRun[]>("/api/v1/workflows/runs");
}

export function getRun(id: string): Promise<WorkflowRun | undefined> {
  return apiGet<WorkflowRun | undefined>(`/api/v1/workflows/runs/${id}`);
}

export async function startRun(pkg: PackageDefinition, context?: Record<string, any>): Promise<WorkflowRun> {
  return apiPost<WorkflowRun>("/api/v1/workflows/runs", { pkg, context });
}
