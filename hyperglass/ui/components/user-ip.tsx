import { useMemo } from 'react';
import { Button, Stack, Text, VStack, useDisclosure } from '@chakra-ui/react';
import { Prompt } from '~/components';
import { useConfig } from '~/context';
import { DynamicIcon } from '~/elements';
import { useStrf, useWtf, useColorValue } from '~/hooks';

interface UserIPProps {
  setTarget(target: string): void;
}

export const UserIP = (props: UserIPProps): JSX.Element => {
  const { setTarget } = props;
  const { onOpen, ...disclosure } = useDisclosure();
  const strF = useStrf();
  const { web } = useConfig();

  const errorColor = useColorValue('red.500', 'red.300');

  const noIPv4 = strF(web.text.noIp, { protocol: 'IPv4' });
  const noIPv6 = strF(web.text.noIp, { protocol: 'IPv6' });

  const [ipv4, ipv6, query] = useWtf();

  const hasResult = useMemo(
    () => (!ipv4.isError || !ipv6.isError) && (ipv4.data?.ip !== null || ipv6.data?.ip !== null),
    [ipv4, ipv6],
  );

  const show4 = useMemo(() => !ipv4.isError && ipv4.data?.ip !== null, [ipv4]);
  const show6 = useMemo(() => !ipv6.isError && ipv6.data?.ip !== null, [ipv6]);

  function handleOpen(): void {
    onOpen();
    query();
  }

  return (
    <Prompt
      trigger={
        <Button size="sm" onClick={handleOpen}>
          {web.text.ipButton}
        </Button>
      }
      onOpen={handleOpen}
      {...disclosure}
    >
      <VStack w="100%" spacing={4} justify="center">
        {hasResult && (
          <Text fontSize="sm" textAlign="center">
            {web.text.ipSelect}
          </Text>
        )}
        <Stack spacing={2}>
          {show4 && (
            <Button
              size="sm"
              fontSize="xs"
              fontFamily="mono"
              colorScheme="primary"
              isDisabled={ipv4.isError}
              isLoading={ipv4.isLoading}
              justifyContent="space-between"
              onClick={() => {
                ipv4?.data?.ip && setTarget(ipv4.data.ip);
                disclosure.onClose();
              }}
              rightIcon={<DynamicIcon icon={{ fa: 'FaArrowCircleRight' }} boxSize="18px" />}
            >
              {ipv4?.data?.ip ?? noIPv4}
            </Button>
          )}
          {show6 && (
            <Button
              size="sm"
              fontSize="xs"
              fontFamily="mono"
              colorScheme="secondary"
              isDisabled={ipv6.isError}
              isLoading={ipv6.isLoading}
              justifyContent="space-between"
              onClick={() => {
                ipv6?.data?.ip && setTarget(ipv6.data.ip);
                disclosure.onClose();
              }}
              rightIcon={<DynamicIcon icon={{ fa: 'FaArrowCircleRight' }} boxSize="18px" />}
            >
              {ipv6?.data?.ip ?? noIPv6}
            </Button>
          )}
          {!hasResult && (
            <Text fontSize="sm" textAlign="center" color={errorColor}>
              {web.text.ipError}
            </Text>
          )}
        </Stack>
      </VStack>
    </Prompt>
  );
};
