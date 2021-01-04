import { useMemo, useState } from 'react';
import { useToken } from '@chakra-ui/react';
import { useMobile } from '~/context';

// Mobile:
// xs: 32
// sm: 28
// md: 24
// lg: 20
// xl: 16
// 2xl: 14
// 3xl: 12
// 4xl: 10
// 5xl: 7
type Sizes = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl';

export function useTitleSize(title: string, defaultSize: Sizes, deps: unknown[] = []): string {
  const [size, setSize] = useState<Sizes>(defaultSize);
  const realSize = useToken('fontSizes', size) as string;
  const isMobile = useMobile();
  function getSize(l: number): void {
    switch (true) {
      case l > 32:
        setSize('xs');
        break;
      case l <= 32 && l > 28:
        setSize('xs');
        break;
      case l <= 28 && l > 24:
        setSize('sm');
        break;
      case l <= 24 && l > 20:
        setSize('md');
        break;
      case l <= 20 && l > 16:
        setSize('lg');
        break;
      case l <= 16 && l > 14:
        setSize('xl');
        break;
      case l <= 14 && l > 12:
        setSize('2xl');
        break;
      case l <= 12 && l > 10:
        setSize('3xl');
        break;
      case l <= 10 && l > 7:
        setSize('4xl');
        break;
      case l <= 7:
        setSize('5xl');
        break;
    }
  }
  return useMemo(() => {
    getSize(title.length);
    return realSize;
  }, [title, isMobile, ...deps]);
}
