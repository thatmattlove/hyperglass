import { Heading } from '@chakra-ui/react';
import { useConfig } from '~/context';
import { useBooleanValue, useFormInteractive } from '~/hooks';
import { useTitleSize } from './use-title-size';

export const TitleOnly = (): JSX.Element => {
  const { web } = useConfig();
  const formInteractive = useFormInteractive();
  const margin = useBooleanValue(formInteractive, 0, 2);
  const sizeSm = useTitleSize(web.text.title, '2xl', []);

  return (
    <Heading as="h1" mb={margin} fontSize={{ base: sizeSm, lg: '5xl' }}>
      {web.text.title}
    </Heading>
  );
};
