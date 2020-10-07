import * as React from 'react';
import { forwardRef } from 'react';
import { AccordionIcon, Icon, Spinner, Stack, Text, Tooltip, useColorMode } from '@chakra-ui/core';
import format from 'string-format';
import { useConfig } from 'app/context';

format.extend(String.prototype, {});

const runtimeText = (runtime, text) => {
  let unit;
  if (runtime === 1) {
    unit = 'second';
  } else {
    unit = 'seconds';
  }
  const fmt = text.format({ seconds: runtime });
  return `${fmt} ${unit}`;
};

const statusColor = { dark: 'primary.300', light: 'primary.500' };
const warningColor = { dark: 300, light: 500 };
const defaultStatusColor = {
  dark: 'success.300',
  light: 'success.500',
};

export const ResultHeader = forwardRef(
  ({ title, loading, error, errorMsg, errorLevel, runtime }, ref) => {
    const { colorMode } = useColorMode();
    const config = useConfig();
    return (
      <Stack ref={ref} isInline alignItems="center" w="100%">
        {loading ? (
          <Spinner size="sm" mr={4} color={statusColor[colorMode]} />
        ) : error ? (
          <Tooltip hasArrow label={errorMsg} placement="top">
            <Icon
              name="warning"
              color={`${errorLevel}.${warningColor[colorMode]}`}
              mr={4}
              size={6}
            />
          </Tooltip>
        ) : (
          <Tooltip
            hasArrow
            label={runtimeText(runtime, config.web.text.complete_time)}
            placement="top">
            <Icon name="check" color={defaultStatusColor[colorMode]} mr={4} size={6} />
          </Tooltip>
        )}
        <Text fontSize="lg">{title}</Text>
        <AccordionIcon ml="auto" />
      </Stack>
    );
  },
);
