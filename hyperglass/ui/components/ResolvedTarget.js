import * as React from 'react';
import { forwardRef, useEffect } from 'react';
import { Button, Icon, Spinner, Stack, Tag, Text, Tooltip, useColorMode } from '@chakra-ui/core';
import useAxios from 'axios-hooks';
import format from 'string-format';
import { useConfig } from 'app/context';

format.extend(String.prototype, {});

const labelBg = { dark: 'secondary', light: 'secondary' };
const labelBgSuccess = { dark: 'success', light: 'success' };

export const ResolvedTarget = forwardRef(
  ({ fqdnTarget, setTarget, queryTarget, families, availVrfs }, ref) => {
    const { colorMode } = useColorMode();
    const config = useConfig();
    const labelBgStatus = {
      true: labelBgSuccess[colorMode],
      false: labelBg[colorMode],
    };
    const dnsUrl = config.web.dns_provider.url;
    const query4 = families.includes(4);
    const query6 = families.includes(6);
    const params = {
      4: {
        url: dnsUrl,
        params: { name: fqdnTarget, type: 'A' },
        headers: { accept: 'application/dns-json' },
        crossdomain: true,
        timeout: 1000,
      },
      6: {
        url: dnsUrl,
        params: { name: fqdnTarget, type: 'AAAA' },
        headers: { accept: 'application/dns-json' },
        crossdomain: true,
        timeout: 1000,
      },
    };

    const [{ data: data4, loading: loading4, error: error4 }] = useAxios(params[4]);

    const [{ data: data6, loading: loading6, error: error6 }] = useAxios(params[6]);

    const handleOverride = overridden => {
      setTarget({ field: 'query_target', value: overridden });
    };

    const isSelected = value => {
      return labelBgStatus[value === queryTarget];
    };

    const findAnswer = data => {
      return data?.Answer?.filter(answerData => answerData.type === data?.Question[0]?.type)[0]
        ?.data;
    };

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
        ref={ref}
        isInline
        w="100%"
        justifyContent={
          query4 && data4?.Answer && query6 && data6?.Answer && availVrfs.length > 1
            ? 'space-between'
            : 'flex-end'
        }
        flexWrap="wrap">
        {loading4 ||
          error4 ||
          (query4 && findAnswer(data4) && (
            <Tag my={2}>
              <Tooltip
                hasArrow
                label={config.web.text.fqdn_tooltip.format({
                  protocol: 'IPv4',
                })}
                placement="bottom">
                <Button
                  height="unset"
                  minW="unset"
                  fontSize="xs"
                  py="0.1rem"
                  px={2}
                  mr={2}
                  variantColor={labelBgStatus[findAnswer(data4) === queryTarget]}
                  borderRadius="md"
                  onClick={() => handleOverride(findAnswer(data4))}>
                  IPv4
                </Button>
              </Tooltip>
              {loading4 && <Spinner />}
              {error4 && <Icon name="warning" />}
              {findAnswer(data4) && (
                <Text fontSize="xs" fontFamily="mono" as="span" fontWeight={400}>
                  {findAnswer(data4)}
                </Text>
              )}
            </Tag>
          ))}
        {loading6 ||
          error6 ||
          (query6 && findAnswer(data6) && (
            <Tag my={2}>
              <Tooltip
                hasArrow
                label={config.web.text.fqdn_tooltip.format({
                  protocol: 'IPv6',
                })}
                placement="bottom">
                <Button
                  height="unset"
                  minW="unset"
                  fontSize="xs"
                  py="0.1rem"
                  px={2}
                  mr={2}
                  variantColor={isSelected(findAnswer(data6))}
                  borderRadius="md"
                  onClick={() => handleOverride(findAnswer(data6))}>
                  IPv6
                </Button>
              </Tooltip>
              {loading6 && <Spinner />}
              {error6 && <Icon name="warning" />}
              {findAnswer(data6) && (
                <Text fontSize="xs" fontFamily="mono" as="span" fontWeight={400}>
                  {findAnswer(data6)}
                </Text>
              )}
            </Tag>
          ))}
      </Stack>
    );
  },
);
