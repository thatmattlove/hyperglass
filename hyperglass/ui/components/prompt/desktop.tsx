import {
  Popover,
  PopoverBody,
  PopoverArrow,
  PopoverTrigger,
  PopoverContent,
  PopoverCloseButton,
} from '@chakra-ui/react';
import { useColorValue } from '~/hooks';

import type { PromptProps } from './types';

export const DesktopPrompt = (props: PromptProps): JSX.Element => {
  const { trigger, children, ...disclosure } = props;
  const bg = useColorValue('white', 'gray.900');

  return (
    <Popover closeOnBlur={false} {...disclosure}>
      <PopoverTrigger>{trigger}</PopoverTrigger>
      <PopoverContent bg={bg}>
        <PopoverArrow bg={bg} />
        <PopoverCloseButton />
        <PopoverBody p={6}>{children}</PopoverBody>
      </PopoverContent>
    </Popover>
  );
};
