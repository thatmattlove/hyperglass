import type { UseDisclosureReturn } from '@chakra-ui/react';

type PromptPropsBase = React.PropsWithChildren<
  Omit<Partial<UseDisclosureReturn>, 'isOpen' | 'onClose'> &
    Pick<UseDisclosureReturn, 'isOpen' | 'onClose'>
>;

export interface PromptProps extends PromptPropsBase {
  trigger?: JSX.Element;
}
