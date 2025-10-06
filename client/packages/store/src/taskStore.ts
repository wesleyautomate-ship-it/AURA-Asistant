import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { 
  Task, 
  TaskCreateData, 
  TaskUpdateData, 
  TaskFilters, 
  TaskListResponse,
  TaskReorderData,
  TaskStatus,
  TaskPriority,
  taskService 
} from '@propertypro/services';

export type FetchStatus = 'idle' | 'loading' | 'success' | 'error';

export interface TaskStore {
  // State
  tasks: Record<string, Task>; // Normalized by id
  taskIds: string[]; // Ordered array of task IDs
  filters: TaskFilters;
  sort: {
    field: string;
    order: 'asc' | 'desc';
  };
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
  
  // UI State
  selectedTaskId: string | null;
  isModalOpen: boolean;
  modalMode: 'create' | 'edit' | 'view' | null;
  isReordering: boolean;
  
  // Loading States
  fetchStatus: FetchStatus;
  createStatus: FetchStatus;
  updateStatus: FetchStatus;
  deleteStatus: FetchStatus;
  reorderStatus: FetchStatus;
  
  // Error States
  error: string | null;
  
  // Realtime
  isRealtimeConnected: boolean;
  lastSyncAt: Date | null;

  // Selectors
  getTaskById: (id: string) => Task | undefined;
  getTasksByStatus: (status: TaskStatus) => Task[];
  getTasksByPriority: (priority: TaskPriority) => Task[];
  getOverdueTasks: () => Task[];
  getTasksDueToday: () => Task[];
  getFilteredTasks: () => Task[];
  
  // Actions
  init: () => void;
  setFilters: (filters: Partial<TaskFilters>) => void;
  setSort: (field: string, order?: 'asc' | 'desc') => void;
  setPagination: (page: number, pageSize?: number) => void;
  
  // CRUD Actions
  fetchTasks: (filters?: TaskFilters) => Promise<void>;
  createTask: (data: TaskCreateData) => Promise<Task | null>;
  updateTask: (id: string, data: TaskUpdateData) => Promise<Task | null>;
  toggleComplete: (id: string) => Promise<Task | null>;
  deleteTask: (id: string) => Promise<boolean>;
  reorderTasks: (reorderData: TaskReorderData) => Promise<boolean>;
  
  // Assignment Actions
  assignTask: (taskId: string, userId: string) => Promise<boolean>;
  unassignTask: (taskId: string, userId: string) => Promise<boolean>;
  
  // UI Actions
  selectTask: (id: string | null) => void;
  openModal: (mode: 'create' | 'edit' | 'view', taskId?: string) => void;
  closeModal: () => void;
  
  // Utility Actions
  clearError: () => void;
  reset: () => void;
  
  // Optimistic Updates
  optimisticUpdate: (id: string, data: Partial<Task>) => void;
  rollbackOptimisticUpdate: (id: string, originalTask: Task) => void;
}

const initialState = {
  tasks: {},
  taskIds: [],
  filters: {},
  sort: {
    field: 'order_index',
    order: 'asc' as const,
  },
  pagination: {
    page: 1,
    pageSize: 50,
    total: 0,
    hasNext: false,
    hasPrev: false,
  },
  selectedTaskId: null,
  isModalOpen: false,
  modalMode: null,
  isReordering: false,
  fetchStatus: 'idle' as FetchStatus,
  createStatus: 'idle' as FetchStatus,
  updateStatus: 'idle' as FetchStatus,
  deleteStatus: 'idle' as FetchStatus,
  reorderStatus: 'idle' as FetchStatus,
  error: null,
  isRealtimeConnected: false,
  lastSyncAt: null,
};

export const useTaskStore = create<TaskStore>()(
  subscribeWithSelector((set, get) => ({
    ...initialState,

    // Selectors
    getTaskById: (id: string) => get().tasks[id],
    
    getTasksByStatus: (status: TaskStatus) => {
      const { tasks, taskIds } = get();
      return taskIds
        .map(id => tasks[id])
        .filter(task => task && task.status === status);
    },
    
    getTasksByPriority: (priority: TaskPriority) => {
      const { tasks, taskIds } = get();
      return taskIds
        .map(id => tasks[id])
        .filter(task => task && task.priority === priority);
    },
    
    getOverdueTasks: () => {
      const { tasks, taskIds } = get();
      return taskIds
        .map(id => tasks[id])
        .filter(task => task && task.is_overdue);
    },
    
    getTasksDueToday: () => {
      const today = new Date().toISOString().split('T')[0];
      const { tasks, taskIds } = get();
      return taskIds
        .map(id => tasks[id])
        .filter(task => task && task.due_date === today);
    },
    
    getFilteredTasks: () => {
      const { tasks, taskIds, filters } = get();
      let filteredTasks = taskIds.map(id => tasks[id]).filter(Boolean);

      // Apply status filter
      if (filters.status) {
        filteredTasks = filteredTasks.filter(task => task.status === filters.status);
      }

      // Apply priority filter
      if (filters.priority) {
        filteredTasks = filteredTasks.filter(task => task.priority === filters.priority);
      }

      // Apply search filter
      if (filters.q) {
        const query = filters.q.toLowerCase();
        filteredTasks = filteredTasks.filter(task =>
          task.title.toLowerCase().includes(query) ||
          (task.description && task.description.toLowerCase().includes(query))
        );
      }

      return filteredTasks;
    },

    // Actions
    init: () => {
      set({ ...initialState });
    },

    setFilters: (newFilters: Partial<TaskFilters>) => {
      set(state => ({
        filters: { ...state.filters, ...newFilters },
        pagination: { ...state.pagination, page: 1 }, // Reset to first page
      }));
    },

    setSort: (field: string, order?: 'asc' | 'desc') => {
      set(state => ({
        sort: {
          field,
          order: order || (state.sort.field === field && state.sort.order === 'asc' ? 'desc' : 'asc'),
        },
        pagination: { ...state.pagination, page: 1 }, // Reset to first page
      }));
    },

    setPagination: (page: number, pageSize?: number) => {
      set(state => ({
        pagination: {
          ...state.pagination,
          page,
          pageSize: pageSize || state.pagination.pageSize,
        },
      }));
    },

    fetchTasks: async (filters?: TaskFilters) => {
      set({ fetchStatus: 'loading', error: null });
      
      try {
        const { filters: currentFilters, sort, pagination } = get();
        const requestFilters = {
          ...currentFilters,
          ...filters,
          sort: sort.field,
          order: sort.order,
          page: pagination.page,
          page_size: pagination.pageSize,
        };

        const response = await taskService.listTasks(requestFilters);
        
        // Normalize tasks by ID
        const tasks: Record<string, Task> = {};
        const taskIds: string[] = [];
        
        response.tasks.forEach(task => {
          tasks[task.id] = task;
          taskIds.push(task.id);
        });

        set({
          tasks,
          taskIds,
          pagination: {
            page: response.page,
            pageSize: response.page_size,
            total: response.total,
            hasNext: response.has_next,
            hasPrev: response.has_prev,
          },
          fetchStatus: 'success',
          lastSyncAt: new Date(),
        });
      } catch (error) {
        set({ 
          fetchStatus: 'error', 
          error: error instanceof Error ? error.message : 'Failed to fetch tasks'
        });
      }
    },

    createTask: async (data: TaskCreateData) => {
      set({ createStatus: 'loading', error: null });
      
      try {
        const newTask = await taskService.createTask(data);
        
        set(state => ({
          tasks: { ...state.tasks, [newTask.id]: newTask },
          taskIds: [newTask.id, ...state.taskIds],
          createStatus: 'success',
        }));
        
        return newTask;
      } catch (error) {
        set({ 
          createStatus: 'error', 
          error: error instanceof Error ? error.message : 'Failed to create task'
        });
        return null;
      }
    },

    updateTask: async (id: string, data: TaskUpdateData) => {
      const originalTask = get().tasks[id];
      if (!originalTask) return null;

      // Optimistic update
      set(state => ({
        updateStatus: 'loading',
        error: null,
        tasks: {
          ...state.tasks,
          [id]: { ...originalTask, ...data, updated_at: new Date().toISOString() }
        }
      }));

      try {
        const updatedTask = await taskService.updateTask(id, data);
        
        set(state => ({
          tasks: { ...state.tasks, [id]: updatedTask },
          updateStatus: 'success',
        }));
        
        return updatedTask;
      } catch (error) {
        // Rollback optimistic update
        set(state => ({
          tasks: { ...state.tasks, [id]: originalTask },
          updateStatus: 'error',
          error: error instanceof Error ? error.message : 'Failed to update task'
        }));
        return null;
      }
    },

    toggleComplete: async (id: string) => {
      const originalTask = get().tasks[id];
      if (!originalTask) return null;

      // Optimistic update
      const newStatus = originalTask.status === 'completed' ? 'open' : 'completed';
      set(state => ({
        updateStatus: 'loading',
        error: null,
        tasks: {
          ...state.tasks,
          [id]: { 
            ...originalTask, 
            status: newStatus,
            updated_at: new Date().toISOString()
          }
        }
      }));

      try {
        const updatedTask = await taskService.toggleComplete(id);
        
        set(state => ({
          tasks: { ...state.tasks, [id]: updatedTask },
          updateStatus: 'success',
        }));
        
        return updatedTask;
      } catch (error) {
        // Rollback optimistic update
        set(state => ({
          tasks: { ...state.tasks, [id]: originalTask },
          updateStatus: 'error',
          error: error instanceof Error ? error.message : 'Failed to toggle task completion'
        }));
        return null;
      }
    },

    deleteTask: async (id: string) => {
      const originalTask = get().tasks[id];
      if (!originalTask) return false;

      // Optimistic delete
      set(state => ({
        deleteStatus: 'loading',
        error: null,
        tasks: Object.fromEntries(
          Object.entries(state.tasks).filter(([taskId]) => taskId !== id)
        ),
        taskIds: state.taskIds.filter(taskId => taskId !== id),
      }));

      try {
        await taskService.deleteTask(id);
        set({ deleteStatus: 'success' });
        return true;
      } catch (error) {
        // Rollback optimistic delete
        set(state => ({
          tasks: { ...state.tasks, [id]: originalTask },
          taskIds: [...state.taskIds, id],
          deleteStatus: 'error',
          error: error instanceof Error ? error.message : 'Failed to delete task'
        }));
        return false;
      }
    },

    reorderTasks: async (reorderData: TaskReorderData) => {
      const originalTasks = get().tasks;
      const originalTaskIds = get().taskIds;

      // Optimistic reorder
      const newTaskIds = [...originalTaskIds];
      const newTasks = { ...originalTasks };
      
      reorderData.task_orders.forEach(({ id, order_index }) => {
        if (newTasks[id]) {
          newTasks[id] = { ...newTasks[id], order_index };
        }
      });
      
      // Sort by new order
      newTaskIds.sort((a, b) => 
        (newTasks[a]?.order_index || 0) - (newTasks[b]?.order_index || 0)
      );

      set({
        reorderStatus: 'loading',
        error: null,
        tasks: newTasks,
        taskIds: newTaskIds,
        isReordering: true,
      });

      try {
        await taskService.reorderTasks(reorderData);
        set({ 
          reorderStatus: 'success',
          isReordering: false,
        });
        return true;
      } catch (error) {
        // Rollback optimistic reorder
        set({
          tasks: originalTasks,
          taskIds: originalTaskIds,
          reorderStatus: 'error',
          isReordering: false,
          error: error instanceof Error ? error.message : 'Failed to reorder tasks'
        });
        return false;
      }
    },

    assignTask: async (taskId: string, userId: string) => {
      try {
        await taskService.assignTask(taskId, userId);
        
        // Update the task with the new assignment
        set(state => {
          const task = state.tasks[taskId];
          if (task && !task.assigned_to.includes(userId)) {
            return {
              tasks: {
                ...state.tasks,
                [taskId]: {
                  ...task,
                  assigned_to: [...task.assigned_to, userId],
                  updated_at: new Date().toISOString()
                }
              }
            };
          }
          return state;
        });
        
        return true;
      } catch (error) {
        set({ error: error instanceof Error ? error.message : 'Failed to assign task' });
        return false;
      }
    },

    unassignTask: async (taskId: string, userId: string) => {
      try {
        await taskService.unassignTask(taskId, userId);
        
        // Update the task with the removed assignment
        set(state => {
          const task = state.tasks[taskId];
          if (task) {
            return {
              tasks: {
                ...state.tasks,
                [taskId]: {
                  ...task,
                  assigned_to: task.assigned_to.filter(id => id !== userId),
                  updated_at: new Date().toISOString()
                }
              }
            };
          }
          return state;
        });
        
        return true;
      } catch (error) {
        set({ error: error instanceof Error ? error.message : 'Failed to unassign task' });
        return false;
      }
    },

    // UI Actions
    selectTask: (id: string | null) => {
      set({ selectedTaskId: id });
    },

    openModal: (mode: 'create' | 'edit' | 'view', taskId?: string) => {
      set({ 
        isModalOpen: true, 
        modalMode: mode, 
        selectedTaskId: taskId || null 
      });
    },

    closeModal: () => {
      set({ 
        isModalOpen: false, 
        modalMode: null, 
        selectedTaskId: null 
      });
    },

    // Utility Actions
    clearError: () => {
      set({ error: null });
    },

    reset: () => {
      set({ ...initialState });
    },

    // Optimistic Updates
    optimisticUpdate: (id: string, data: Partial<Task>) => {
      set(state => ({
        tasks: {
          ...state.tasks,
          [id]: { ...state.tasks[id], ...data } as Task
        }
      }));
    },

    rollbackOptimisticUpdate: (id: string, originalTask: Task) => {
      set(state => ({
        tasks: { ...state.tasks, [id]: originalTask }
      }));
    },
  }))
);

// Selectors for easier access
export const selectTasks = (state: TaskStore) => state.taskIds.map(id => state.tasks[id]).filter(Boolean);
export const selectTasksLoading = (state: TaskStore) => state.fetchStatus === 'loading';
export const selectTasksError = (state: TaskStore) => state.error;
export const selectSelectedTask = (state: TaskStore) => 
  state.selectedTaskId ? state.tasks[state.selectedTaskId] : null;
export const selectIsModalOpen = (state: TaskStore) => state.isModalOpen;
export const selectModalMode = (state: TaskStore) => state.modalMode;