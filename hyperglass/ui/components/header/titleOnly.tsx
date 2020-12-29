import { Heading } from '@chakra-ui/react';
import { useConfig } from '~/context';
import { useBooleanValue } from '~/hooks';
import { useHeaderCtx } from './context';
import { useTitleSize } from './useTitleSize';

export const TitleOnly = () => {
  const { showSubtitle } = useHeaderCtx();
  const { web } = useConfig();

  const margin = useBooleanValue(showSubtitle, 2, 0);
  const sizeSm = useTitleSize(web.text.title, '2xl', []);

  return (
    <Heading as="h1" mb={margin} fontSize={{ base: sizeSm, lg: '5xl' }}>
      {web.text.title}
    </Heading>
  );
};
