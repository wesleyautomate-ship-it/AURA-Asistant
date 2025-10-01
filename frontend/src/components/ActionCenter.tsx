import React from 'react';
import ActionButton from './ActionButton';
import { ACTION_ITEMS } from '../constants';
import type { ActionItem, ActionId } from '../types';

interface ActionCenterProps {
    onActionClick: (id: ActionId) => void;
}

const ActionCenter: React.FC<ActionCenterProps> = ({ onActionClick }) => {
    return (
        <div>
            <h2 className="text-base font-bold text-gray-900 mb-4">What can PropertyPro AI do for you?</h2>
            <div className="grid grid-cols-3 gap-x-4 gap-y-6">
                {ACTION_ITEMS.map(item => (
                    <ActionButton key={item.id} item={item as ActionItem} onClick={() => onActionClick(item.id)} />
                ))}
            </div>
        </div>
    );
};

export default ActionCenter;