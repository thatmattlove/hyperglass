import { useMemo, useState } from 'react';
import { Image, Skeleton } from '@chakra-ui/react';
import { useColorValue, useConfig, useColorMode } from '~/context';

import type { TLogo } from './types';

/**
 * Custom hook to handle loading the user's logo, errors loading the logo, and color mode changes.
 */
function useLogo(): [string, () => void] {
  const { web } = useConfig();
  const { dark_format, light_format } = web.logo;
  const { colorMode } = useColorMode();

  const src = useColorValue(`/images/dark${dark_format}`, `/images/light${light_format}`);

  // Use the hyperglass logo if the user's logo can't be loaded for whatever reason.
  const fallbackSrc = useColorValue(
    'https://res.cloudinary.com/hyperglass/image/upload/v1593916013/logo-dark.svg',
    'https://res.cloudinary.com/hyperglass/image/upload/v1593916013/logo-light.svg',
  );

  const [fallback, setSource] = useState<string | null>(null);

  /**
   * If the user image cannot be loaded, log an error to the console and set the fallback image.
   */
  function setFallback() {
    console.warn(`Error loading image from '${src}'`);
    setSource(fallbackSrc);
  }

  // Only return the fallback image if it's been set.
  return useMemo(() => [fallback ?? src, setFallback], [colorMode]);
}

export const Logo: React.FC<TLogo> = (props: TLogo) => {
  const { web } = useConfig();
  const { width } = web.logo;

  const skeletonA = useColorValue('whiteSolid.100', 'blackSolid.800');
  const skeletonB = useColorValue('light.500', 'dark.500');

  const [source, setFallback] = useLogo();

  return (
    <Image
      src={source}
      alt={web.text.title}
      onError={setFallback}
      width={width ?? 'auto'}
      css={{
        userDrag: 'none',
        userSelect: 'none',
        msUserSelect: 'none',
        MozUserSelect: 'none',
        WebkitUserDrag: 'none',
        WebkitUserSelect: 'none',
      }}
      fallback={
        <Skeleton
          isLoaded={false}
          borderRadius="md"
          endColor={skeletonB}
          startColor={skeletonA}
          width={{ base: 64, lg: 80 }}
          height={{ base: 12, lg: 16 }}
        />
      }
      {...props}
    />
  );
};
