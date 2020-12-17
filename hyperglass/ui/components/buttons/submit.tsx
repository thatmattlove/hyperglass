import {
  IconButton,
  Popover,
  PopoverTrigger,
  PopoverArrow,
  PopoverCloseButton,
  PopoverBody,
  PopoverContent,
} from '@chakra-ui/react';
import { FiSearch } from '@meronex/icons/fi';
import { ResolvedTarget } from '~/components';
import { useLGState } from '~/hooks';

import type { TSubmitButton } from './types';

export const SubmitButton = (props: TSubmitButton) => {
  const { children, handleChange, ...rest } = props;
  const { btnLoading, resolvedIsOpen, resolvedClose } = useLGState();

  function handleClose(): void {
    btnLoading.set(false);
    resolvedClose();
  }

  return (
    <>
      <Popover isOpen={resolvedIsOpen.value} onClose={handleClose} closeOnBlur={false}>
        <PopoverTrigger>
          <IconButton
            size="lg"
            width={16}
            type="submit"
            icon={<FiSearch />}
            title="Submit Query"
            aria-label="Submit Query"
            colorScheme="primary"
            isLoading={btnLoading.value}
            {...rest}
          />
        </PopoverTrigger>
        <PopoverContent>
          <PopoverArrow />
          <PopoverCloseButton />
          <PopoverBody p={6}>
            {resolvedIsOpen.value && <ResolvedTarget setTarget={handleChange} />}
          </PopoverBody>
        </PopoverContent>
      </Popover>
    </>
  );
};
