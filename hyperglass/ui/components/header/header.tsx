import { Flex, ScaleFade } from '@chakra-ui/react';
import { motionChakra } from '~/elements';
import { useBooleanValue, useBreakpointValue, useFormInteractive } from '~/hooks';
import { Title } from './title';

const Wrapper = motionChakra('header', {
  baseStyle: { display: 'flex', px: 4, pt: 6, minH: 16, w: 'full', flex: '0 1 auto' },
});

export const Header = (): JSX.Element => {
  const formInteractive = useFormInteractive();

  const titleWidth = useBooleanValue(
    formInteractive,
    { base: '75%', lg: '50%' },
    { base: '75%', lg: '75%' },
  );

  return (
    <Wrapper layout="position">
      <ScaleFade in initialScale={0.5} style={{ width: '100%' }}>
        <Flex
          height="100%"
          maxW={titleWidth}
          // This is here for the logo
          justifyContent="center"
          mx="auto"
        >
          <Title />
        </Flex>
      </ScaleFade>
    </Wrapper>
  );
};
