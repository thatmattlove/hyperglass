import { Heading } from '@chakra-ui/react';
import { useConfig, useBreakpointValue } from '~/context';
import { useTitleSize } from './useTitleSize';

export const SubtitleOnly: React.FC = () => {
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
