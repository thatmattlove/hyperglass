import { Button, Flex, FlexProps } from '@chakra-ui/core';
import { withAnimation } from '~/components';

const AnimatedFlex = withAnimation<FlexProps>(Flex);

export const FooterButton = (props: IFooterButton) => {
  const { side, href, ...rest } = props;

  let buttonProps = Object();
  if (typeof href !== 'undefined') {
    buttonProps = { href, as: 'a', target: '_blank', rel: 'noopener noreferrer' };
  }

  return (
    <AnimatedFlex
      p={0}
      w="auto"
      flexGrow={0}
      float={side}
      flexShrink={0}
      maxWidth="100%"
      flexBasis="auto"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}>
      <Button size="xs" variant="ghost" {...buttonProps} {...rest} />
    </AnimatedFlex>
  );
};
