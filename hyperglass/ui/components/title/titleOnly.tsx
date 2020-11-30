import { Heading } from '@chakra-ui/react';
import { useConfig } from '~/context';
import { useBooleanValue } from '~/hooks';

import type { TTitleOnly } from './types';

export const TitleOnly = (props: TTitleOnly) => {
  const { showSubtitle, ...rest } = props;
  const { web } = useConfig();
  const fontSize = useBooleanValue(showSubtitle, { base: '2xl', lg: '5xl' }, '2xl');
  const margin = useBooleanValue(showSubtitle, 2, 0);
  return (
    <Heading as="h1" mb={margin} fontSize={fontSize} {...rest}>
      {web.text.title}
    </Heading>
  );
};
