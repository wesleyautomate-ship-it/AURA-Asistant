import type { ComponentType } from 'react';
import { Platform } from 'react-native';

import NativeComponent from './DocumentManager.native';
import WebComponent, { type DocumentManagerProps } from './DocumentManager.web';

const DocumentManager = (Platform.OS === 'web' ? WebComponent : NativeComponent) as ComponentType<DocumentManagerProps>;

export type { DocumentManagerProps };
export default DocumentManager;