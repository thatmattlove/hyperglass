import dynamic from 'next/dynamic';
import { forwardRef, useMemo } from 'react';
import { AccordionIcon, Icon, Spinner, Stack, Text, Tooltip, useColorMode } from '@chakra-ui/react';
import { useConfig, useColorValue } from '~/context';
import { useStrf } from '~/hooks';

import type { TResultHeader } from './types';

const Check = dynamic<MeronexIcon>(() => import('@meronex/icons/fa').then(i => i.FaCheckCircle));
const Warning = dynamic<MeronexIcon>(() => import('@meronex/icons/bi').then(i => i.BisError));

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
          <Icon as={Warning} color={warning} mr={4} boxSize={6} />
        </Tooltip>
      ) : (
        <Tooltip hasArrow label={label} placement="top">
          <Icon as={Check} color={defaultStatus} mr={4} boxSize={6} />
        </Tooltip>
      )}
      <Text fontSize="lg">{title}</Text>
      <AccordionIcon ml="auto" />
    </Stack>
  );
});
