import React from 'react';
import { useNavigation } from '@react-navigation/native';

import { TransactionsView } from '@propertypro/features';

const TransactionsScreen: React.FC = () => {
  const navigation = useNavigation();

  return <TransactionsView onBack={() => (navigation as any)?.goBack?.()} />;
};

export default TransactionsScreen;