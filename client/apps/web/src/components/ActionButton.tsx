import React from 'react';
import { ActionItem } from '../types';

interface ActionButtonProps {
    item: ActionItem;
    onClick: () => void;
}

const ActionButton: React.FC<ActionButtonProps> = ({ item, onClick }) => {
    // Redesigned to match mockups with circular icons
    return (
        <button
            onClick={onClick}
            className="flex flex-col items-center justify-start text-center space-y-2 group"
            aria-label={item.title}
        >
            <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-all group-hover:scale-105 shadow-sm ${item.color}`}>
                {/* Scale icon slightly for better visual balance */}
                <div className="transform scale-110">
                    {item.icon}
                </div>
            </div>
            <h3 className="font-semibold text-xs text-gray-800 tracking-tight">{item.title}</h3>
        </button>
    );
};

export default ActionButton;