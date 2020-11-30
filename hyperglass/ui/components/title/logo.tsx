import { Image } from '@chakra-ui/react';
import { useColorValue, useConfig } from '~/context';

import type { TLogo } from './types';

export const Logo = (props: TLogo) => {
  const { web } = useConfig();
  const { width, dark_format, light_format } = web.logo;

  const src = useColorValue(`/images/dark${dark_format}`, `/images/light${light_format}`);
  const fallbackSrc = useColorValue(
    'https://res.cloudinary.com/hyperglass/image/upload/v1593916013/logo-dark.svg',
    'https://res.cloudinary.com/hyperglass/image/upload/v1593916013/logo-light.svg',
  );

  return (
    <Image
      css={{
        userDrag: 'none',
        userSelect: 'none',
        msUserSelect: 'none',
        MozUserSelect: 'none',
        WebkitUserDrag: 'none',
        WebkitUserSelect: 'none',
      }}
      fallbackSrc={fallbackSrc}
      width={width ?? 'auto'}
      alt={web.text.title}
      src={src}
      {...props}
    />
  );
};
