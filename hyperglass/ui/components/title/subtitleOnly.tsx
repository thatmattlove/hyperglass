import { Heading } from '@chakra-ui/react';
import { useConfig } from '~/context';

import type { TSubtitleOnly } from './types';

export const SubtitleOnly = (props: TSubtitleOnly) => {
  const { web } = useConfig();
  return (
    <Heading
      as="h3"
      whiteSpace="break-spaces"
      fontSize={{ base: 'md', lg: 'xl' }}
      textAlign={{ base: 'left', xl: 'center' }}
      {...props}>
      {web.text.subtitle}
    </Heading>
  );
};
