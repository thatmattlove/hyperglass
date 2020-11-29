import { Button } from '@chakra-ui/react';
import { AnimatedDiv } from '~/components';

import type { TFooterButton } from './types';

export const FooterButton = (props: TFooterButton) => {
  const { side, href, ...rest } = props;

  let buttonProps = Object();
  if (typeof href !== 'undefined') {
    buttonProps = { href, as: 'a', target: '_blank', rel: 'noopener noreferrer' };
  }

  return (
    <AnimatedDiv
      p={0}
      w="auto"
      d="flex"
      flexGrow={0}
      float={side}
      flexShrink={0}
      maxWidth="100%"
      flexBasis="auto"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}>
      <Button size="xs" variant="ghost" {...buttonProps} {...rest} />
    </AnimatedDiv>
  );
};
