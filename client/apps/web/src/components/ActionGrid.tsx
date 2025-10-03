import React from 'react';
import ActionButton from './ActionButton';
import { ACTION_ITEMS } from '../constants';
import { ActionItem } from '../types';

interface ActionGridProps {
    // Currently doesn't need props, but ready for future expansion
}

const ActionGrid: React.FC<ActionGridProps> = () => {
    return (
        <div className="mb-8">
            <h2 className="text-sm font-semibold text-gray-500 mb-3">Choose Your Team</h2>
            <div className="grid grid-cols-2 gap-3">
                {ACTION_ITEMS.map(item => (
                    <ActionButton key={item.id} item={item as ActionItem} onClick={() => { /* Navigation logic handled by parent */ }} />
                ))}
            </div>
        </div>
    );
};

export default ActionGrid;