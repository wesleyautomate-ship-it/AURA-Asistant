import { Platform } from 'react-native';

import NativeComponent from './MarketingView.native';
import WebComponent from './MarketingView.web';

const MarketingView = Platform.OS === 'web' ? WebComponent : NativeComponent;

export default MarketingView;