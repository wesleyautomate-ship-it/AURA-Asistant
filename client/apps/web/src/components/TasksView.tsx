import React, { useState, useMemo, useEffect } from 'react';
import ViewHeader from './ViewHeader';
import { Priority } from '../types';
import TaskItem from './TaskItem';
import {
  useTaskStore,
  selectTasks,
  selectTasksLoading,
  selectTasksError,
  selectIsModalOpen,
  selectModalMode
} from '@propertypro/store';
import { Task, TaskCreateData, TaskUpdateData, TaskPriority } from '@propertypro/services';

const TaskModal: React.FC<{
    isOpen: boolean;
    onClose: () => void;
    onSave: (task: TaskCreateData | (TaskUpdateData & { id: string })) => void;
    taskToEdit?: Task | null;
}> = ({ isOpen, onClose, onSave, taskToEdit }) => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [dueDate, setDueDate] = useState('');
    const [priority, setPriority] = useState<TaskPriority>('medium');

    React.useEffect(() => {
        if (isOpen) {
            if (taskToEdit) {
                setTitle(taskToEdit.title);
                setDescription(taskToEdit.description || '');
                setDueDate(taskToEdit.due_date || '');
                setPriority(taskToEdit.priority);
            } else {
                setTitle('');
                setDescription('');
                setDueDate(new Date().toISOString().split('T')[0]); // Default to today for new tasks
                setPriority('medium');
            }
        }
    }, [isOpen, taskToEdit]);

    if (!isOpen) return null;

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!title.trim()) return;
        
        const taskData = {
            title: title.trim(),
            description: description.trim() || undefined,
            due_date: dueDate || undefined,
            priority
        };
        
        if (taskToEdit) {
            onSave({ ...taskData, id: taskToEdit.id });
        } else {
            onSave(taskData);
        }
        
        onClose();
    };

    return (
        <div className="absolute inset-0 bg-black/40 z-50 flex items-center justify-center p-4" onClick={onClose}>
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-md" onClick={(e) => e.stopPropagation()}>
                <form onSubmit={handleSubmit}>
                    <div className="p-6">
                        <h2 className="text-lg font-bold text-gray-800 mb-4">{taskToEdit ? 'Edit Task' : 'Add New Task'}</h2>
                        <div className="space-y-4">
                            <div>
                                <label htmlFor="title" className="text-sm font-medium text-gray-700">Title</label>
                                <input type="text" id="title" value={title} onChange={(e) => setTitle(e.target.value)} className="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" required />
                            </div>
                            <div>
                                <label htmlFor="description" className="text-sm font-medium text-gray-700">Description</label>
                                <textarea id="description" value={description} onChange={(e) => setDescription(e.target.value)} className="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" rows={3} placeholder="Optional task description"></textarea>
                            </div>
                             <div>
                                <label htmlFor="dueDate" className="text-sm font-medium text-gray-700">Due Date</label>
                                <input type="date" id="dueDate" value={dueDate} onChange={(e) => setDueDate(e.target.value)} className="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" />
                            </div>
                             <div>
                                <label htmlFor="priority" className="text-sm font-medium text-gray-700">Priority</label>
                                <select id="priority" value={priority} onChange={(e) => setPriority(e.target.value as TaskPriority)} className="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high">High</option>
                                    <option value="urgent">Urgent</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div className="bg-gray-50 px-6 py-3 flex justify-end space-x-3 rounded-b-2xl">
                        <button type="button" onClick={onClose} className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">Cancel</button>
                        <button type="submit" className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700">{taskToEdit ? 'Save Changes' : 'Add Task'}</button>
                    </div>
                </form>
            </div>
        </div>
    );
};


const TasksView: React.FC = () => {
    const tasks = useTaskStore(selectTasks);
    const isLoading = useTaskStore(selectTasksLoading);
    const error = useTaskStore(selectTasksError);
    const isModalOpen = useTaskStore(selectIsModalOpen);
    const modalMode = useTaskStore(selectModalMode);
    
    const {
        fetchTasks,
        createTask,
        updateTask,
        toggleComplete,
        deleteTask,
        openModal,
        closeModal,
        selectTask,
        getTaskById
    } = useTaskStore();
    
    const [taskToEdit, setTaskToEdit] = useState<Task | null>(null);
    
    // Fetch tasks on component mount
    useEffect(() => {
        // Try to fetch tasks, but don't fail if backend is unavailable
        fetchTasks().catch((error) => {
            console.warn('Backend unavailable, using offline mode:', error);
            // Add some demo tasks for testing UI
            if (tasks.length === 0) {
                // You can manually add some demo tasks here if needed
            }
        });
    }, [fetchTasks, tasks.length]);

    const handleToggleComplete = (id: string) => {
        toggleComplete(id);
    };

    const handleDelete = (id: string) => {
        if (confirm('Are you sure you want to delete this task?')) {
            deleteTask(id);
        }
    };
    
    const handleEdit = (task: Task) => {
        setTaskToEdit(task);
        openModal('edit', task.id);
    };

    const handleAddNew = () => {
        setTaskToEdit(null);
        openModal('create');
    };

    const handleSaveTask = async (taskData: TaskCreateData | (TaskUpdateData & { id: string })) => {
        try {
            if ('id' in taskData) {
                // Editing existing task
                await updateTask(taskData.id, taskData);
            } else {
                // Creating new task
                await createTask(taskData);
            }
        } catch (error) {
            console.error('Failed to save task:', error);
            // Error handling is done in the store
        }
    };

    const sortedTasks = useMemo(() => {
        return [...tasks].sort((a, b) => {
            // Sort by completion status first
            if (a.status === 'completed' && b.status !== 'completed') return 1;
            if (a.status !== 'completed' && b.status === 'completed') return -1;
            
            // Then by due date
            if (a.due_date && b.due_date) {
                return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
            }
            if (a.due_date && !b.due_date) return -1;
            if (!a.due_date && b.due_date) return 1;
            
            // Finally by order index
            return a.order_index - b.order_index;
        });
    }, [tasks]);

    const incompleteTasks = sortedTasks.filter(t => t.status !== 'completed');
    const completedTasks = sortedTasks.filter(t => t.status === 'completed');

    // Show loading state
    if (isLoading && tasks.length === 0) {
        return (
            <div className="flex flex-col h-full bg-gray-50">
                <ViewHeader title="My Tasks" />
                <main className="flex-1 overflow-y-auto p-4 md:p-6 pb-28">
                    <div className="text-center py-16">
                        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
                        <p className="text-gray-500">Loading tasks...</p>
                    </div>
                </main>
            </div>
        );
    }

    // Show error state
    if (error) {
        return (
            <div className="flex flex-col h-full bg-gray-50">
                <ViewHeader title="My Tasks" />
                <main className="flex-1 overflow-y-auto p-4 md:p-6 pb-28">
                    <div className="text-center py-16">
                        <div className="inline-block p-4 bg-red-100 rounded-full mb-4">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.996-.833-2.732 0L3.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
                            </svg>
                        </div>
                        <h3 className="text-lg font-bold text-gray-800 mb-2">Failed to load tasks</h3>
                        <p className="text-gray-500 mb-4">{error}</p>
                        <button 
                            onClick={() => fetchTasks()}
                            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                        >
                            Try Again
                        </button>
                    </div>
                </main>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-gray-50">
            <ViewHeader title="My Tasks" actions={
                <button onClick={handleAddNew} className="flex items-center space-x-2 px-3 py-1.5 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors">
                     <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                    <span>New Task</span>
                </button>
            }/>
             <main className="flex-1 overflow-y-auto p-4 md:p-6 pb-28">
                <div className="space-y-3">
                    {incompleteTasks.length > 0 && incompleteTasks.map(task => (
                        <TaskItem key={task.id} task={task} onToggleComplete={handleToggleComplete} onDelete={handleDelete} onEdit={handleEdit}/>
                    ))}

                    {completedTasks.length > 0 && (
                        <div>
                            <h3 className="text-sm font-semibold text-gray-500 mt-6 mb-2 pl-2">Completed</h3>
                             {completedTasks.map(task => (
                                <TaskItem key={task.id} task={task} onToggleComplete={handleToggleComplete} onDelete={handleDelete} onEdit={handleEdit} />
                            ))}
                        </div>
                    )}

                    {tasks.length === 0 && (
                        <div className="text-center py-16">
                             <div className="inline-block p-4 bg-gray-100 rounded-full mb-4">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                            </div>
                            <h3 className="text-lg font-bold text-gray-800">All caught up!</h3>
                            <p className="text-gray-500 mt-1">You have no pending tasks.</p>
                        </div>
                    )}
                </div>
            </main>
            <TaskModal 
                isOpen={isModalOpen} 
                onClose={closeModal}
                onSave={handleSaveTask}
                taskToEdit={taskToEdit}
            />
        </div>
    );
};

export default TasksView;