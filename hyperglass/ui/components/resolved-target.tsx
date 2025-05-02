import { useMemo } from 'react';
import { Button, Stack, Text, VStack } from '@chakra-ui/react';
import { useConfig } from '~/context';
import { DynamicIcon } from '~/elements';
import { useStrf, useColorValue, useDNSQuery, useFormState } from '~/hooks';

import type { DnsOverHttps } from '~/types';

interface ResolvedTargetProps {
  errorClose(): void;
}

function findAnswer(data: DnsOverHttps.Response | undefined): string {
  let answer = '';
  if (typeof data !== 'undefined') {
    answer = data?.Answer?.filter(answerData => answerData.type === data?.Question[0]?.type)[0]
      ?.data;
  }
  return answer;
}

export const ResolvedTarget = (props: ResolvedTargetProps): JSX.Element => {
  const { errorClose } = props;
  const strF = useStrf();
  const { web } = useConfig();

  const setStatus = useFormState(s => s.setStatus);
  const displayTarget = useFormState(s => s.target.display);
  const setFormValue = useFormState(s => s.setFormValue);

  const color = useColorValue('secondary.500', 'secondary.300');
  const errorColor = useColorValue('red.500', 'red.300');

  const tooltip4 = strF(web.text.fqdnTooltip, { protocol: 'IPv4' });
  const tooltip6 = strF(web.text.fqdnTooltip, { protocol: 'IPv6' });

  const [messageStart, messageEnd] = web.text.fqdnMessage.split('{fqdn}');
  const [errorStart, errorEnd] = web.text.fqdnError.split('{fqdn}');

  const {
    data: data4,
    isLoading: isLoading4,
    isError: isError4,
    error: error4,
  } = useDNSQuery(displayTarget, 4);

  const {
    data: data6,
    isLoading: isLoading6,
    isError: isError6,
    error: error6,
  } = useDNSQuery(displayTarget, 6);

  isError4 && console.error(error4);
  isError6 && console.error(error6);

  const answer4 = useMemo(() => findAnswer(data4), [data4]);
  const answer6 = useMemo(() => findAnswer(data6), [data6]);

  function selectTarget(value: string): void {
    setFormValue('queryTarget', [value]);
    setStatus('results');
  }

  const hasAnswer = useMemo(
    () => (!isError4 || !isError6) && (answer4 || answer6),
    [answer4, answer6, isError4, isError6],
  );
  const showA = useMemo(() => !isLoading4 && !isError4 && answer4, [isLoading4, isError4, answer4]);
  const showAAAA = useMemo(
    () => !isLoading6 && !isError6 && answer6,
    [isLoading6, isError6, answer6],
  );

  return (
    <VStack w="100%" spacing={4} justify="center">
      {hasAnswer && (
        <Text fontSize="sm" textAlign="center">
          {messageStart}
          <Text as="span" fontSize="sm" fontWeight="bold" color={color}>
            {`${displayTarget}`.toLowerCase()}
          </Text>
          {messageEnd}
        </Text>
      )}
      <Stack spacing={2}>
        {showA && (
          <Button
            size="sm"
            fontSize="xs"
            title={tooltip4}
            fontFamily="mono"
            colorScheme="primary"
            justifyContent="space-between"
            onClick={() => selectTarget(answer4)}
            rightIcon={<DynamicIcon icon={{ fa: 'FaArrowCircleRight' }} boxSize="18px" />}
          >
            {answer4}
          </Button>
        )}
        {showAAAA && (
          <Button
            size="sm"
            fontSize="xs"
            title={tooltip6}
            fontFamily="mono"
            colorScheme="secondary"
            justifyContent="space-between"
            onClick={() => selectTarget(answer6)}
            rightIcon={<DynamicIcon icon={{ fa: 'FaArrowCircleRight' }} boxSize="18px" />}
          >
            {answer6}
          </Button>
        )}
        {!hasAnswer && (
          <>
            <Text fontSize="sm" textAlign="center" color={errorColor}>
              {errorStart}
              <Text as="span" fontSize="sm" fontWeight="bold">
                {`${displayTarget}`.toLowerCase()}
              </Text>
              {errorEnd}
            </Text>
            <Button
              colorScheme="red"
              variant="outline"
              size="sm"
              onClick={errorClose}
              leftIcon={<DynamicIcon icon={{ fa: 'FaArrowCircleLeft' }} />}
            >
              {web.text.fqdnErrorButton}
            </Button>
          </>
        )}
      </Stack>
    </VStack>
  );
};
