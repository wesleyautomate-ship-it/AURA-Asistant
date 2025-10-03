import type { ComponentType } from 'react';
import { Platform } from 'react-native';

import NativeComponent from './TransactionTemplates.native';
import WebComponent, { type TransactionTemplatesProps } from './TransactionTemplates.web';

const TransactionTemplates = (Platform.OS === 'web' ? WebComponent : NativeComponent) as ComponentType<TransactionTemplatesProps>;

export type { TransactionTemplatesProps };
export default TransactionTemplates;