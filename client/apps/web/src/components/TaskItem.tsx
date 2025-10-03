import React from 'react';
import { Task } from '../types';

interface TaskItemProps {
    task: Task;
    onToggleComplete: (id: number) => void;
    onDelete: (id: number) => void;
    onEdit: (task: Task) => void;
}

const PriorityIndicator: React.FC<{ priority: Task['priority'] }> = ({ priority }) => {
    const colorMap = {
        High: 'bg-red-500',
        Medium: 'bg-yellow-500',
        Low: 'bg-green-500',
    };
    return <span className={`w-3 h-3 rounded-full ${colorMap[priority]}`} aria-label={`${priority} priority`}></span>;
};

const TaskItem: React.FC<TaskItemProps> = ({ task, onToggleComplete, onDelete, onEdit }) => {
    const isOverdue = !task.isCompleted && new Date(task.dueDate) < new Date(new Date().toDateString());

    const formattedDate = new Date(task.dueDate).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        timeZone: 'UTC', // Ensure date is not affected by client timezone
    });

    return (
        <div className="flex items-center p-3 bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow group">
            <button onClick={() => onToggleComplete(task.id)} className="mr-3 flex-shrink-0" aria-label={`Mark task ${task.isCompleted ? 'incomplete' : 'complete'}`}>
                <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors ${task.isCompleted ? 'bg-blue-600 border-blue-600' : 'border-gray-300'}`}>
                    {task.isCompleted && <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg>}
                </div>
            </button>
            <div className="flex-grow min-w-0">
                <p className={`text-sm text-gray-800 truncate ${task.isCompleted ? 'line-through text-gray-400' : ''}`}>
                    {task.title}
                </p>
                <div className="flex items-center space-x-4 mt-1">
                    <div className={`flex items-center space-x-1.5 text-xs font-medium ${isOverdue ? 'text-red-600' : 'text-gray-500'}`}>
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                        </svg>
                        <span>{formattedDate}</span>
                    </div>
                    <PriorityIndicator priority={task.priority} />
                </div>
            </div>
            <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button onClick={() => onEdit(task)} className="p-2 text-gray-500 hover:text-blue-600 rounded-full hover:bg-gray-100" aria-label="Edit task">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L16.732 3.732z" />
                    </svg>
                </button>
                 <button onClick={() => onDelete(task.id)} className="p-2 text-gray-500 hover:text-red-600 rounded-full hover:bg-gray-100" aria-label="Delete task">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                </button>
            </div>
        </div>
    );
};

export default TaskItem;
