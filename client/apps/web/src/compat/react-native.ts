import * as ReactNativeWeb from 'react-native-web';

type TurboModule = unknown;

type TurboModuleRegistryType = {
  get: (name: string) => TurboModule | undefined;
  getEnforcing: (name: string) => TurboModule;
  hasEnforcing: (name: string) => boolean;
};

const TurboModuleRegistry: TurboModuleRegistryType = {
  get: () => undefined,
  getEnforcing: (name: string) => {
    throw new Error(`TurboModuleRegistry: '${name}' is not available on the web platform.`);
  },
  hasEnforcing: () => false,
};

const ReactNativeWebDefault = {
  ...ReactNativeWeb,
  TurboModuleRegistry,
};

export { TurboModuleRegistry };
export * from 'react-native-web';

export default ReactNativeWebDefault;