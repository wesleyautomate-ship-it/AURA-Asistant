import { apiGet, apiPost, apiPatch, apiDelete } from './api';

// Task-related types
export type TaskStatus = 'open' | 'in_progress' | 'completed' | 'archived';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  due_date?: string; // ISO date string
  order_index: number;
  property_id?: string;
  client_id?: string;
  created_by: string;
  assigned_to: string[];
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
  is_overdue: boolean;
}

export interface TaskCreateData {
  title: string;
  description?: string;
  due_date?: string; // ISO date string
  priority?: TaskPriority;
  property_id?: string;
  client_id?: string;
  assigned_to?: string[];
}

export interface TaskUpdateData {
  title?: string;
  description?: string;
  due_date?: string; // ISO date string
  priority?: TaskPriority;
  status?: TaskStatus;
  property_id?: string;
  client_id?: string;
}

export interface TaskFilters {
  status?: TaskStatus;
  priority?: TaskPriority;
  assigned_to?: string;
  property_id?: string;
  client_id?: string;
  q?: string; // Search query
  sort?: string;
  order?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface TaskReorderData {
  task_orders: Array<{
    id: string;
    order_index: number;
  }>;
}

/**
 * Task Service for managing tasks via API
 */
export class TaskService {
  private controller?: AbortController;

  /**
   * Abort any ongoing request
   */
  private abortPrevious(): void {
    if (this.controller) {
      this.controller.abort();
    }
    this.controller = new AbortController();
  }

  /**
   * List tasks with filtering and pagination
   */
  async listTasks(filters: TaskFilters = {}): Promise<TaskListResponse> {
    this.abortPrevious();
    
    const params = new URLSearchParams();
    
    if (filters.status) params.append('status', filters.status);
    if (filters.priority) params.append('priority', filters.priority);
    if (filters.assigned_to) params.append('assigned_to', filters.assigned_to);
    if (filters.property_id) params.append('property_id', filters.property_id);
    if (filters.client_id) params.append('client_id', filters.client_id);
    if (filters.q) params.append('q', filters.q);
    if (filters.sort) params.append('sort', filters.sort);
    if (filters.order) params.append('order', filters.order);
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.page_size) params.append('page_size', filters.page_size.toString());
    
    const query = params.toString();
    const url = query ? `/api/v1/tasks/dev?${query}` : '/api/v1/tasks/dev';
    
    return apiGet<TaskListResponse>(url, {
      signal: this.controller.signal,
    });
  }

  /**
   * Get a specific task by ID
   */
  async getTask(taskId: string): Promise<Task> {
    return apiGet<Task>(`/api/v1/tasks/${taskId}`);
  }

  /**
   * Create a new task
   */
  async createTask(taskData: TaskCreateData): Promise<Task> {
    return apiPost<Task>('/api/v1/tasks', taskData);
  }

  /**
   * Update an existing task
   */
  async updateTask(taskId: string, taskData: TaskUpdateData): Promise<Task> {
    return apiPatch<Task>(`/api/v1/tasks/${taskId}`, taskData);
  }

  /**
   * Toggle task completion status
   */
  async toggleComplete(taskId: string): Promise<Task> {
    return apiPatch<Task>(`/api/v1/tasks/${taskId}/complete`);
  }

  /**
   * Delete a task (soft delete)
   */
  async deleteTask(taskId: string): Promise<{ message: string }> {
    return apiDelete<{ message: string }>(`/api/v1/tasks/${taskId}`);
  }

  /**
   * Reorder tasks by updating their order indices
   */
  async reorderTasks(reorderData: TaskReorderData): Promise<{ message: string }> {
    return apiPost<{ message: string }>('/api/v1/tasks/reorder', reorderData);
  }

  /**
   * Assign a task to a user
   */
  async assignTask(taskId: string, userId: string): Promise<{ message: string }> {
    return apiPost<{ message: string }>(`/api/v1/tasks/${taskId}/assign`, {
      user_id: userId,
    });
  }

  /**
   * Unassign a task from a user
   */
  async unassignTask(taskId: string, userId: string): Promise<{ message: string }> {
    return apiDelete<{ message: string }>(`/api/v1/tasks/${taskId}/assign/${userId}`);
  }

  /**
   * Get tasks with built-in retry logic and error handling
   */
  async getTasksWithRetry(filters: TaskFilters = {}, maxRetries = 3): Promise<TaskListResponse> {
    let lastError: Error;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await this.listTasks(filters);
      } catch (error) {
        lastError = error as Error;
        if (attempt === maxRetries) break;
        
        // Exponential backoff
        const delay = Math.pow(2, attempt - 1) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    
    throw lastError!;
  }

  /**
   * Batch update multiple tasks
   */
  async batchUpdateTasks(updates: Array<{ id: string; data: TaskUpdateData }>): Promise<Task[]> {
    const promises = updates.map(({ id, data }) => this.updateTask(id, data));
    return Promise.all(promises);
  }

  /**
   * Get overdue tasks
   */
  async getOverdueTasks(): Promise<Task[]> {
    const response = await this.listTasks({
      sort: 'due_date',
      order: 'asc',
      page_size: 100, // Get more overdue tasks
    });
    
    return response.tasks.filter(task => task.is_overdue);
  }

  /**
   * Get tasks due today
   */
  async getTasksDueToday(): Promise<Task[]> {
    const today = new Date().toISOString().split('T')[0];
    const response = await this.listTasks({
      sort: 'due_date',
      order: 'asc',
      page_size: 100,
    });
    
    return response.tasks.filter(task => task.due_date === today);
  }

  /**
   * Get tasks by status with counts
   */
  async getTasksByStatus(): Promise<Record<TaskStatus, Task[]>> {
    const [open, inProgress, completed, archived] = await Promise.all([
      this.listTasks({ status: 'open', page_size: 100 }),
      this.listTasks({ status: 'in_progress', page_size: 100 }),
      this.listTasks({ status: 'completed', page_size: 100 }),
      this.listTasks({ status: 'archived', page_size: 100 }),
    ]);
    
    return {
      open: open.tasks,
      in_progress: inProgress.tasks,
      completed: completed.tasks,
      archived: archived.tasks,
    };
  }

  /**
   * Search tasks by title or description
   */
  async searchTasks(query: string): Promise<Task[]> {
    if (!query.trim()) {
      return [];
    }
    
    const response = await this.listTasks({
      q: query.trim(),
      page_size: 50,
    });
    
    return response.tasks;
  }
}

// Export a singleton instance
export const taskService = new TaskService();