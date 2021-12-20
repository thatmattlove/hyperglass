import { useMobile } from '~/hooks';
import { DesktopPrompt } from './desktop';
import { MobilePrompt } from './mobile';

import type { PromptProps } from './types';

export const Prompt = (props: PromptProps): JSX.Element => {
  const isMobile = useMobile();

  return isMobile ? <MobilePrompt {...props} /> : <DesktopPrompt {...props} />;
};
