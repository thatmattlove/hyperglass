import { useMemo } from 'react';
import { AccordionIcon, Box, Spinner, HStack, Text, Tooltip } from '@chakra-ui/react';
import { DynamicIcon } from '~/components';
import { useConfig, useColorValue } from '~/context';
import { useOpposingColor, useStrf } from '~/hooks';

import type { TResultHeader } from './types';

const runtimeText = (runtime: number, text: string): string => {
  let unit = 'seconds';
  if (runtime === 1) {
    unit = 'second';
  }
  return `${text} ${unit}`;
};

export const ResultHeader: React.FC<TResultHeader> = (props: TResultHeader) => {
  const { title, loading, isError, errorMsg, errorLevel, runtime } = props;

  const status = useColorValue('primary.500', 'primary.300');
  const warning = useColorValue(`${errorLevel}.500`, `${errorLevel}.300`);
  const defaultStatus = useColorValue('success.500', 'success.300');

  const { web } = useConfig();
  const strF = useStrf();
  const text = strF(web.text.completeTime, { seconds: runtime });
  const label = useMemo(() => runtimeText(runtime, text), [runtime, text]);

  const color = useOpposingColor(isError ? warning : defaultStatus);

  return (
    <HStack alignItems="center" w="100%">
      <Tooltip
        hasArrow
        placement="top"
        isDisabled={loading}
        label={isError ? errorMsg : label}
        bg={isError ? warning : defaultStatus}
        color={color}
      >
        <Box boxSize={6}>
          {loading ? (
            <Spinner size="sm" mr={4} color={status} />
          ) : (
            <DynamicIcon
              icon={isError ? { bi: 'BisError' } : { fa: 'FaCheckCircle' }}
              color={isError ? warning : defaultStatus}
              mr={4}
              boxSize="100%"
            />
          )}
        </Box>
      </Tooltip>

      <Text fontSize="lg">{title}</Text>
      <AccordionIcon ml="auto" />
    </HStack>
  );
};
