import { IconButton } from '@chakra-ui/react';

import type { TTableIconButton } from './types';

export const TableIconButton: React.FC<TTableIconButton> = (props: TTableIconButton) => (
  <IconButton size="sm" borderWidth={1} {...props} aria-label="Table Icon Button" />
);
