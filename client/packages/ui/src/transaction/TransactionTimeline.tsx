import type { ComponentType } from 'react';
import { Platform } from 'react-native';

import NativeComponent from './TransactionTimeline.native';
import WebComponent, { type TransactionTimelineProps } from './TransactionTimeline.web';

const TransactionTimeline = (Platform.OS === 'web' ? WebComponent : NativeComponent) as ComponentType<TransactionTimelineProps>;

export type { TransactionTimelineProps };
export default TransactionTimeline;