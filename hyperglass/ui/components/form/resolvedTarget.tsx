import { useEffect } from 'react';
import { Button, Icon, Spinner, Stack, Tag, Text, Tooltip } from '@chakra-ui/react';
import { useQuery } from 'react-query';
import { useConfig } from '~/context';
import { useStrf } from '~/hooks';

import type { DnsOverHttps, ColorNames } from '~/types';
import type { TResolvedTarget } from './types';

function findAnswer(data: DnsOverHttps.Response | undefined): string {
  let answer = '';
  if (typeof data !== 'undefined') {
    answer = data?.Answer?.filter(answerData => answerData.type === data?.Question[0]?.type)[0]
      ?.data;
  }
  return answer;
}

export const ResolvedTarget = (props: TResolvedTarget) => {
  const { fqdnTarget, setTarget, queryTarget, families, availVrfs } = props;
  const { web } = useConfig();

  const dnsUrl = web.dns_provider.url;
  const query4 = Array.from(families).includes(4);
  const query6 = Array.from(families).includes(6);

  const tooltip4 = useStrf(web.text.fqdn_tooltip, { protocol: 'IPv4' });
  const tooltip6 = useStrf(web.text.fqdn_tooltip, { protocol: 'IPv6' });

  const { data: data4, isLoading: isLoading4, isError: isError4 } = useQuery(
    [fqdnTarget, 4],
    dnsQuery,
  );

  const { data: data6, isLoading: isLoading6, isError: isError6 } = useQuery(
    [fqdnTarget, 6],
    dnsQuery,
  );

  async function dnsQuery(
    target: string,
    family: 4 | 6,
  ): Promise<DnsOverHttps.Response | undefined> {
    let json;
    const type = family === 4 ? 'A' : family === 6 ? 'AAAA' : '';
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 1000);
    const res = await fetch(`${dnsUrl}?name=${target}&type=${type}`, {
      headers: { accept: 'application/dns-json' },
      signal: controller.signal,
      mode: 'cors',
    });
    json = await res.json();
    clearTimeout(timeout);
    return json;
  }

  function handleOverride(value: string): void {
    setTarget({ field: 'query_target', value });
  }

  function isSelected(value: string): ColorNames {
    if (value === queryTarget) {
      return 'success';
    } else {
      return 'secondary';
    }
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
    <Stack
      isInline
      w="100%"
      justifyContent={
        query4 && data4?.Answer && query6 && data6?.Answer && availVrfs.length > 1
          ? 'space-between'
          : 'flex-end'
      }
      flexWrap="wrap">
      {isLoading4 ||
        isError4 ||
        (query4 && findAnswer(data4) && (
          <Tag my={2}>
            <Tooltip hasArrow label={tooltip4} placement="bottom">
              <Button
                px={2}
                mr={2}
                py="0.1rem"
                minW="unset"
                fontSize="xs"
                height="unset"
                borderRadius="md"
                colorScheme={isSelected(findAnswer(data4))}
                onClick={() => handleOverride(findAnswer(data4))}>
                IPv4
              </Button>
            </Tooltip>
            {isLoading4 && <Spinner />}
            {isError4 && <Icon name="warning" />}
            {findAnswer(data4) && (
              <Text fontSize="xs" fontFamily="mono" as="span" fontWeight={400}>
                {findAnswer(data4)}
              </Text>
            )}
          </Tag>
        ))}
      {isLoading6 ||
        isError6 ||
        (query6 && findAnswer(data6) && (
          <Tag my={2}>
            <Tooltip hasArrow label={tooltip6} placement="bottom">
              <Button
                px={2}
                mr={2}
                py="0.1rem"
                minW="unset"
                fontSize="xs"
                height="unset"
                borderRadius="md"
                colorScheme={isSelected(findAnswer(data6))}
                onClick={() => handleOverride(findAnswer(data6))}>
                IPv6
              </Button>
            </Tooltip>
            {isLoading6 && <Spinner />}
            {isError6 && <Icon name="warning" />}
            {findAnswer(data6) && (
              <Text fontSize="xs" fontFamily="mono" as="span" fontWeight={400}>
                {findAnswer(data6)}
              </Text>
            )}
          </Tag>
        ))}
    </Stack>
  );
};
