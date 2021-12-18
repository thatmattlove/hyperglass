import { Button, Link, useBreakpointValue } from '@chakra-ui/react';

import type { TFooterLink } from './types';

export const FooterLink = (props: TFooterLink): JSX.Element => {
  const { title } = props;
  const btnSize = useBreakpointValue({ base: 'xs', lg: 'sm' });
  return (
    <Button as={Link} isExternal size={btnSize} variant="ghost" aria-label={title} {...props}>
      {title}
    </Button>
  );
};
