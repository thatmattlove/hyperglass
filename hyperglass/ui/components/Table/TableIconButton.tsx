import { IconButton } from '@chakra-ui/core';

import type { IconButtonProps } from '@chakra-ui/core';

export const TableIconButton = (props: IconButtonProps) => (
  <IconButton size="sm" borderWidth={1} {...props} aria-label="Table Icon Button" />
);
