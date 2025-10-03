import { Platform } from 'react-native';

import NativeComponent from './StrategyView.native';
import WebComponent from './StrategyView.web';

const StrategyView = Platform.OS === 'web' ? WebComponent : NativeComponent;

export default StrategyView;