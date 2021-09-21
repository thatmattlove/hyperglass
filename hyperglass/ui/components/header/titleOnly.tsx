import { Heading } from '@chakra-ui/react';
import { useConfig } from '~/context';
import { useBooleanValue, useFormState } from '~/hooks';
import { useTitleSize } from './useTitleSize';

export const TitleOnly: React.FC = () => {
  const { web } = useConfig();
  const status = useFormState(s => s.status);
  const margin = useBooleanValue(status === 'results', 0, 2);
  const sizeSm = useTitleSize(web.text.title, '2xl', []);

  return (
    <Heading as="h1" mb={margin} fontSize={{ base: sizeSm, lg: '5xl' }}>
      {web.text.title}
    </Heading>
  );
};
