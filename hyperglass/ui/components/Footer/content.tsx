import { Drawer, DrawerBody, DrawerOverlay, DrawerContent } from '@chakra-ui/react';
import { Markdown } from '~/components';

import type { TFooterContent } from './types';

export const FooterContent = (props: TFooterContent) => {
  const { isOpen, onClose, content, side = 'left', ...rest } = props;
  return (
    <Drawer placement="bottom" isOpen={isOpen} onClose={onClose}>
      <DrawerOverlay>
        <DrawerContent
          px={6}
          py={4}
          w="auto"
          borderBottom="1px"
          display="flex"
          maxWidth="100%"
          flexBasis="auto"
          justifyContent={side === 'left' ? 'flex-start' : 'flex-end'}
          {...rest}>
          <DrawerBody textAlign={side}>
            <Markdown content={content} />
          </DrawerBody>
        </DrawerContent>
      </DrawerOverlay>
    </Drawer>
  );
};
