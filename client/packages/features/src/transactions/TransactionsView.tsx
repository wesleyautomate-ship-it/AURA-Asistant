import { Platform } from 'react-native';

import NativeComponent from './TransactionsView.native';
import WebComponent from './TransactionsView.web';

const TransactionsView = Platform.OS === 'web' ? WebComponent : NativeComponent;

export default TransactionsView;