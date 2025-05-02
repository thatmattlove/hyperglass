import { IconButton } from '@chakra-ui/react';

import type { IconButtonProps } from '@chakra-ui/react';

type TTableIconButton = Omit<IconButtonProps, 'aria-label'>;

export const TableIconButton = (props: TTableIconButton): JSX.Element => (
  <IconButton size="sm" borderWidth={1} {...props} aria-label="Table Icon Button" />
);
