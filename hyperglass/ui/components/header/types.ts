import { FlexProps } from '@chakra-ui/react';

import { IConfig } from '~/types';

export interface THeader extends FlexProps {
  resetForm(): void;
}

export type TTitleMode = IConfig['web']['text']['title_mode'];
