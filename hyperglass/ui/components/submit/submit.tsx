import { forwardRef } from 'react';
import {
  Modal,
  Popover,
  ModalBody,
  IconButton,
  PopoverBody,
  ModalOverlay,
  ModalContent,
  PopoverArrow,
  PopoverTrigger,
  PopoverContent,
  ModalCloseButton,
  PopoverCloseButton,
} from '@chakra-ui/react';
import { FiSearch } from '@meronex/icons/fi';
import { useFormContext } from 'react-hook-form';
import { If, ResolvedTarget } from '~/components';
import { useMobile, useColorValue } from '~/context';
import { useLGState, useLGMethods } from '~/hooks';

import type { IconButtonProps } from '@chakra-ui/react';
import type { TSubmitButton, TRSubmitButton } from './types';

const _SubmitIcon: React.ForwardRefRenderFunction<
  HTMLButtonElement,
  Omit<IconButtonProps, 'aria-label'>
> = (props: Omit<IconButtonProps, 'aria-label'>, ref) => {
  const { isLoading, ...rest } = props;
  return (
    <IconButton
      ref={ref}
      size="lg"
      width={16}
      type="submit"
      icon={<FiSearch />}
      title="Submit Query"
      colorScheme="primary"
      isLoading={isLoading}
      aria-label="Submit Query"
      {...rest}
    />
  );
};
const SubmitIcon = forwardRef<HTMLButtonElement, Omit<IconButtonProps, 'aria-label'>>(_SubmitIcon);

/**
 * Mobile Submit Button
 */
const MSubmitButton: React.FC<TRSubmitButton> = (props: TRSubmitButton) => {
  const { children, isOpen, onClose, onChange } = props;
  const bg = useColorValue('white', 'gray.900');
  return (
    <>
      {children}
      <Modal
        size="xs"
        isCentered
        isOpen={isOpen}
        onClose={onClose}
        closeOnEsc={false}
        closeOnOverlayClick={false}
        motionPreset="slideInBottom"
      >
        <ModalOverlay />
        <ModalContent bg={bg}>
          <ModalCloseButton />
          <ModalBody px={4} py={10}>
            {isOpen && <ResolvedTarget setTarget={onChange} errorClose={onClose} />}
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};

/**
 * Desktop Submit Button
 */
const DSubmitButton: React.FC<TRSubmitButton> = (props: TRSubmitButton) => {
  const { children, isOpen, onClose, onChange } = props;
  const bg = useColorValue('white', 'gray.900');
  return (
    <Popover isOpen={isOpen} onClose={onClose} closeOnBlur={false}>
      <PopoverTrigger>{children}</PopoverTrigger>
      <PopoverContent bg={bg}>
        <PopoverArrow bg={bg} />
        <PopoverCloseButton />
        <PopoverBody p={6}>
          {isOpen && <ResolvedTarget setTarget={onChange} errorClose={onClose} />}
        </PopoverBody>
      </PopoverContent>
    </Popover>
  );
};

export const SubmitButton: React.FC<TSubmitButton> = (props: TSubmitButton) => {
  const { handleChange } = props;
  const isMobile = useMobile();
  const { resolvedIsOpen, btnLoading } = useLGState();
  const { resolvedClose, resetForm } = useLGMethods();

  const { reset } = useFormContext();

  function handleClose(): void {
    reset();
    resetForm();
    resolvedClose();
  }

  return (
    <>
      <If c={isMobile}>
        <MSubmitButton isOpen={resolvedIsOpen.value} onClose={handleClose} onChange={handleChange}>
          <SubmitIcon isLoading={btnLoading.value} />
        </MSubmitButton>
      </If>
      <If c={!isMobile}>
        <DSubmitButton isOpen={resolvedIsOpen.value} onClose={handleClose} onChange={handleChange}>
          <SubmitIcon isLoading={btnLoading.value} />
        </DSubmitButton>
      </If>
    </>
  );
};
