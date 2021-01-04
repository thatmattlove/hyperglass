import { Heading } from '@chakra-ui/react';
import { useConfig } from '~/context';
import { useBooleanValue, useLGState } from '~/hooks';
import { useTitleSize } from './useTitleSize';

export const TitleOnly: React.FC = () => {
  const { web } = useConfig();
  const { isSubmitting } = useLGState();

  const margin = useBooleanValue(isSubmitting.value, 0, 2);
  const sizeSm = useTitleSize(web.text.title, '2xl', []);

  return (
    <Heading as="h1" mb={margin} fontSize={{ base: sizeSm, lg: '5xl' }}>
      {web.text.title}
    </Heading>
  );
};
