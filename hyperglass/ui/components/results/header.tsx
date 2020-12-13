import { forwardRef, useMemo } from 'react';
import { AccordionIcon, Box, Spinner, Stack, Text, Tooltip } from '@chakra-ui/react';
import { BisError as Warning } from '@meronex/icons/bi';
import { FaCheckCircle as Check } from '@meronex/icons/fa';
import { useConfig, useColorValue } from '~/context';
import { useStrf } from '~/hooks';

import type { TResultHeader } from './types';

const runtimeText = (runtime: number, text: string): string => {
  let unit = 'seconds';
  if (runtime === 1) {
    unit = 'second';
  }
  return `${text} ${unit}`;
};

export const ResultHeader = forwardRef<HTMLDivElement, TResultHeader>((props, ref) => {
  const { title, loading, error, errorMsg, errorLevel, runtime } = props;

  const status = useColorValue('primary.500', 'primary.300');
  const warning = useColorValue(`${errorLevel}.500`, `${errorLevel}.300`);
  const defaultStatus = useColorValue('success.500', 'success.300');

  const { web } = useConfig();
  const text = useStrf(web.text.complete_time, { seconds: runtime }, [runtime]);
  const label = useMemo(() => runtimeText(runtime, text), [runtime]);

  return (
    <Stack ref={ref} isInline alignItems="center" w="100%">
      {loading ? (
        <Spinner size="sm" mr={4} color={status} />
      ) : error ? (
        <Tooltip hasArrow label={errorMsg} placement="top">
          <Box as={Warning} color={warning} mr={4} boxSize={6} />
        </Tooltip>
      ) : (
        <Tooltip hasArrow label={label} placement="top">
          <Box as={Check} color={defaultStatus} mr={4} boxSize={6} />
        </Tooltip>
      )}
      <Text fontSize="lg">{title}</Text>
      <AccordionIcon ml="auto" />
    </Stack>
  );
});
