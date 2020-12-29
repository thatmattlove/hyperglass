import dynamic from 'next/dynamic';
import { Box, Flex, Icon, IconButton, Slide } from '@chakra-ui/react';
import { useColorValue } from '~/context';
import { useLGState, useOpposingColor } from '~/hooks';

import type { TResetButton } from './types';

const LeftArrow = dynamic<MeronexIcon>(() => import('@meronex/icons/fa').then(i => i.FaAngleLeft));

export const ResetButton = (props: TResetButton) => {
  const { developerMode, resetForm, ...rest } = props;
  const { isSubmitting } = useLGState();
  const bg = useColorValue('primary.500', 'primary.300');
  const color = useOpposingColor(bg);
  return (
    <Slide direction="left" in={isSubmitting.value} unmountOnExit style={{ width: 'auto' }}>
      <Box
        bg={bg}
        left={0}
        zIndex={4}
        bottom={24}
        boxSize={12}
        color={color}
        position="fixed"
        borderRightRadius="md"
        mb={developerMode ? 14 : undefined}>
        <Flex boxSize="100%" justifyContent="center" alignItems="center" {...rest}>
          <IconButton
            color="current"
            variant="ghost"
            aria-label="Reset"
            onClick={resetForm}
            icon={<Icon as={LeftArrow} boxSize={8} />}
          />
        </Flex>
      </Box>
    </Slide>
  );
};
