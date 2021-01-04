import dynamic from 'next/dynamic';
import { Flex, Icon, IconButton } from '@chakra-ui/react';
import { AnimatePresence } from 'framer-motion';
import { AnimatedDiv } from '~/components';
import { useColorValue } from '~/context';
import { useLGState, useOpposingColor } from '~/hooks';

import type { TResetButton } from './types';

const LeftArrow = dynamic<MeronexIcon>(() => import('@meronex/icons/fa').then(i => i.FaAngleLeft));

export const ResetButton: React.FC<TResetButton> = (props: TResetButton) => {
  const { developerMode, resetForm, ...rest } = props;
  const { isSubmitting } = useLGState();
  const bg = useColorValue('primary.500', 'primary.300');
  const color = useOpposingColor(bg);
  return (
    <AnimatePresence>
      {isSubmitting.value && (
        <AnimatedDiv
          bg={bg}
          left={0}
          zIndex={4}
          bottom={24}
          boxSize={12}
          color={color}
          position="fixed"
          animate={{ x: 0 }}
          exit={{ x: '-100%' }}
          borderRightRadius="md"
          initial={{ x: '-100%' }}
          mb={developerMode ? { base: 0, lg: 14 } : undefined}
          transition={{ duration: 0.15, ease: [0.4, 0, 0.2, 1] }}
        >
          <Flex boxSize="100%" justifyContent="center" alignItems="center" {...rest}>
            <IconButton
              variant="unstyled"
              color="current"
              aria-label="Reset"
              onClick={resetForm}
              icon={<Icon as={LeftArrow} boxSize={8} />}
            />
          </Flex>
        </AnimatedDiv>
      )}
    </AnimatePresence>
  );
};
