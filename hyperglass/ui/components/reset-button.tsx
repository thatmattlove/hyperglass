import { Flex, IconButton } from '@chakra-ui/react';
import { AnimatePresence } from 'framer-motion';
import { AnimatedDiv, DynamicIcon } from '~/elements';
import { useColorValue, useOpposingColor, useFormState } from '~/hooks';

import type { FlexProps } from '@chakra-ui/react';

interface ResetButtonProps extends FlexProps {
  developerMode: boolean;
  resetForm(): void;
}

export const ResetButton = (props: ResetButtonProps): JSX.Element => {
  const { developerMode, resetForm, ...rest } = props;
  const status = useFormState(s => s.status);
  const bg = useColorValue('primary.500', 'primary.300');
  const color = useOpposingColor(bg);
  return (
    <AnimatePresence>
      {status === 'results' && (
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
              lineHeight={0}
              color="current"
              variant="unstyled"
              aria-label="Reset"
              onClick={resetForm}
              icon={<DynamicIcon icon={{ fa: 'FaAngleLeft' }} boxSize={8} />}
            />
          </Flex>
        </AnimatedDiv>
      )}
    </AnimatePresence>
  );
};
