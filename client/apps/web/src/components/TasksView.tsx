import React, { useState, useMemo } from 'react';
import ViewHeader from './ViewHeader';
import { Task, Priority } from '../types';
import TaskItem from './TaskItem';

const TaskModal: React.FC<{
    isOpen: boolean;
    onClose: () => void;
    onSave: (task: Omit<Task, 'id' | 'isCompleted'> & { id?: number }) => void;
    taskToEdit?: Task | null;
}> = ({ isOpen, onClose, onSave, taskToEdit }) => {
    const [title, setTitle] = useState('');
    const [dueDate, setDueDate] = useState('');
    const [priority, setPriority] = useState<Priority>('Medium');

    React.useEffect(() => {
        if (isOpen) {
            if (taskToEdit) {
                setTitle(taskToEdit.title);
                setDueDate(taskToEdit.dueDate);
                setPriority(taskToEdit.priority);
            } else {
                setTitle('');
                setDueDate(new Date().toISOString().split('T')[0]); // Default to today for new tasks
                setPriority('Medium');
            }
        }
    }, [isOpen, taskToEdit]);

    if (!isOpen) return null;

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!title.trim()) return;
        onSave({ id: taskToEdit?.id, title, dueDate, priority });
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
                                <label htmlFor="dueDate" className="text-sm font-medium text-gray-700">Due Date</label>
                                <input type="date" id="dueDate" value={dueDate} onChange={(e) => setDueDate(e.target.value)} className="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" required />
                            </div>
                             <div>
                                <label htmlFor="priority" className="text-sm font-medium text-gray-700">Priority</label>
                                <select id="priority" value={priority} onChange={(e) => setPriority(e.target.value as Priority)} className="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                                    <option>Low</option>
                                    <option>Medium</option>
                                    <option>High</option>
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


const TasksView: React.FC<{ tasks: Task[], setTasks: React.Dispatch<React.SetStateAction<Task[]>> }> = ({ tasks, setTasks }) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [taskToEdit, setTaskToEdit] = useState<Task | null>(null);

    const handleToggleComplete = (id: number) => {
        setTasks(tasks.map(task => task.id === id ? { ...task, isCompleted: !task.isCompleted } : task));
    };

    const handleDelete = (id: number) => {
        setTasks(tasks.filter(task => task.id !== id));
    };
    
    const handleEdit = (task: Task) => {
        setTaskToEdit(task);
        setIsModalOpen(true);
    };

    const handleAddNew = () => {
        setTaskToEdit(null);
        setIsModalOpen(true);
    };

    const handleSaveTask = (taskData: Omit<Task, 'isCompleted'>) => {
        if (taskData.id) { // Editing existing task
            setTasks(tasks.map(t => t.id === taskData.id ? { ...t, ...taskData } : t));
        } else { // Creating new task
            const newTask: Task = {
                ...taskData,
                id: Date.now(),
                isCompleted: false,
                dueDate: taskData.dueDate || new Date().toISOString().split('T')[0],
            };
            setTasks([newTask, ...tasks]);
        }
    };

    const sortedTasks = useMemo(() => {
        return [...tasks].sort((a, b) => {
            if (a.isCompleted !== b.isCompleted) {
                return a.isCompleted ? 1 : -1;
            }
            return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
        });
    }, [tasks]);

    const incompleteTasks = sortedTasks.filter(t => !t.isCompleted);
    const completedTasks = sortedTasks.filter(t => t.isCompleted);

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
                onClose={() => setIsModalOpen(false)}
                onSave={handleSaveTask}
                taskToEdit={taskToEdit}
            />
        </div>
    );
};

export default TasksView;