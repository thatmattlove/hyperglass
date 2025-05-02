import { Heading } from '@chakra-ui/react';
import { useConfig } from '~/context';
import { useBreakpointValue } from '~/hooks';
import { useTitleSize } from './use-title-size';

export const SubtitleOnly = (): JSX.Element => {
  const { web } = useConfig();
  const sizeSm = useTitleSize(web.text.subtitle, 'sm');
  const fontSize = useBreakpointValue({ base: sizeSm, lg: 'xl' });

  return (
    <Heading
      as="h3"
      fontWeight="normal"
      fontSize={fontSize}
      whiteSpace="break-spaces"
      textAlign={{ base: 'left', xl: 'center' }}
    >
      {web.text.subtitle}
    </Heading>
  );
};
