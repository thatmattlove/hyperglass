import { useEffect, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { Button, chakra, Stack, Text, VStack } from '@chakra-ui/react';
import { useConfig, useColorValue } from '~/context';
import { useStrf, useLGState, useDNSQuery } from '~/hooks';

const RightArrow = chakra(
  dynamic<MeronexIcon>(() => import('@meronex/icons/fa').then(i => i.FaArrowCircleRight)),
);

const LeftArrow = chakra(
  dynamic<MeronexIcon>(() => import('@meronex/icons/fa').then(i => i.FaArrowCircleLeft)),
);

import type { DnsOverHttps } from '~/types';
import type { TResolvedTarget } from './types';

function findAnswer(data: DnsOverHttps.Response | undefined): string {
  let answer = '';
  if (typeof data !== 'undefined') {
    answer = data?.Answer?.filter(answerData => answerData.type === data?.Question[0]?.type)[0]
      ?.data;
  }
  return answer;
}

export const ResolvedTarget: React.FC<TResolvedTarget> = (props: TResolvedTarget) => {
  const { setTarget, errorClose } = props;
  const { web } = useConfig();
  const { displayTarget, isSubmitting, families, queryTarget } = useLGState();

  const color = useColorValue('secondary.500', 'secondary.300');
  const errorColor = useColorValue('red.500', 'red.300');

  const query4 = Array.from(families.value).includes(4);
  const query6 = Array.from(families.value).includes(6);

  const tooltip4 = useStrf(web.text.fqdn_tooltip, { protocol: 'IPv4' });
  const tooltip6 = useStrf(web.text.fqdn_tooltip, { protocol: 'IPv6' });

  const [messageStart, messageEnd] = web.text.fqdn_message.split('{fqdn}');
  const [errorStart, errorEnd] = web.text.fqdn_error.split('{fqdn}');

  const { data: data4, isLoading: isLoading4, isError: isError4, error: error4 } = useDNSQuery(
    displayTarget.value,
    4,
  );

  const { data: data6, isLoading: isLoading6, isError: isError6, error: error6 } = useDNSQuery(
    displayTarget.value,
    6,
  );

  isError4 && console.error(error4);
  isError6 && console.error(error6);

  const answer4 = useMemo(() => findAnswer(data4), [data4]);
  const answer6 = useMemo(() => findAnswer(data6), [data6]);

  function handleOverride(value: string): void {
    setTarget({ field: 'query_target', value });
  }
  function selectTarget(value: string): void {
    queryTarget.set(value);
    isSubmitting.set(true);
  }

  useEffect(() => {
    if (query6 && data6?.Answer) {
      handleOverride(findAnswer(data6));
    } else if (query4 && data4?.Answer && !query6 && !data6?.Answer) {
      handleOverride(findAnswer(data4));
    } else if (query4 && data4?.Answer) {
      handleOverride(findAnswer(data4));
    }
  }, [data4, data6]);

  return (
    <VStack w="100%" spacing={4} justify="center">
      {(answer4 || answer6) && (
        <Text fontSize="sm" textAlign="center">
          {messageStart}
          <Text as="span" fontSize="sm" fontWeight="bold" color={color}>
            {`${displayTarget.value}`.toLowerCase()}
          </Text>
          {messageEnd}
        </Text>
      )}
      <Stack spacing={2}>
        {!isLoading4 && !isError4 && query4 && answer4 && (
          <Button
            size="sm"
            fontSize="xs"
            title={tooltip4}
            fontFamily="mono"
            colorScheme="primary"
            justifyContent="space-between"
            onClick={() => selectTarget(answer4)}
            rightIcon={<RightArrow boxSize="18px" />}
          >
            {answer4}
          </Button>
        )}
        {!isLoading6 && !isError6 && query6 && answer6 && (
          <Button
            size="sm"
            fontSize="xs"
            title={tooltip6}
            fontFamily="mono"
            colorScheme="secondary"
            justifyContent="space-between"
            onClick={() => selectTarget(answer6)}
            rightIcon={<RightArrow boxSize="18px" />}
          >
            {answer6}
          </Button>
        )}
        {!answer4 && !answer6 && (
          <>
            <Text fontSize="sm" textAlign="center" color={errorColor}>
              {errorStart}
              <Text as="span" fontSize="sm" fontWeight="bold">
                {`${displayTarget.value}`.toLowerCase()}
              </Text>
              {errorEnd}
            </Text>
            <Button
              colorScheme="red"
              variant="outline"
              onClick={errorClose}
              leftIcon={<LeftArrow />}
            >
              {web.text.fqdn_error_button}
            </Button>
          </>
        )}
      </Stack>
    </VStack>
  );
};
