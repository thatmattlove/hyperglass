import { Button, Link } from '@chakra-ui/react';
import { useBreakpointValue } from '~/hooks';

import type { ButtonProps, LinkProps } from '@chakra-ui/react';

type FooterLinkProps = ButtonProps & LinkProps & { title: string };

export const FooterLink = (props: FooterLinkProps): JSX.Element => {
  const { title } = props;
  const btnSize = useBreakpointValue({ base: 'xs', lg: 'sm' });
  return (
    <Button as={Link} isExternal size={btnSize} variant="ghost" aria-label={title} {...props}>
      {title}
    </Button>
  );
};
