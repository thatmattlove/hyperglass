/** @jsx jsx */
import { jsx } from '@emotion/core';
import { forwardRef, useEffect, useState } from 'react';
import {
  AccordionItem,
  AccordionHeader,
  AccordionPanel,
  Alert,
  Box,
  ButtonGroup,
  css,
  Flex,
  Tooltip,
  Text,
  useColorMode,
  useTheme,
} from '@chakra-ui/core';
import { BsLightningFill } from '@meronex/icons/bs';
import styled from '@emotion/styled';
import useAxios from 'axios-hooks';
import strReplace from 'react-string-replace';
import format from 'string-format';
import { startCase } from 'lodash';
import { useConfig, useMedia } from 'app/context';
import {
  BGPTable,
  CacheTimeout,
  CopyButton,
  RequeryButton,
  ResultHeader,
  TextOutput,
} from 'app/components';
import { tableToString } from 'app/util';

format.extend(String.prototype, {});

const FormattedError = ({ keywords, message }) => {
  const patternStr = keywords.map(kw => `(${kw})`).join('|');
  const pattern = new RegExp(patternStr, 'gi');
  let errorFmt;
  try {
    errorFmt = strReplace(message, pattern, match => (
      <Text key={match} as="strong">
        {match}
      </Text>
    ));
  } catch (err) {
    errorFmt = <Text as="span">{message}</Text>;
  }
  return <Text as="span">{keywords.length !== 0 ? errorFmt : message}</Text>;
};

const AccordionHeaderWrapper = styled(Flex)`
  justify-content: space-between;
  &:hover {
    background-color: ${props => props.hoverBg};
  }
  &:focus {
    box-shadow: 'outline';
  }
`;

const statusMap = {
  success: 'success',
  warning: 'warning',
  error: 'warning',
  danger: 'error',
};

const color = { dark: 'white', light: 'black' };
const scrollbar = { dark: 'whiteAlpha.300', light: 'blackAlpha.300' };
const scrollbarHover = { dark: 'whiteAlpha.400', light: 'blackAlpha.400' };
const scrollbarBg = { dark: 'whiteAlpha.50', light: 'blackAlpha.50' };

export const Result = forwardRef(
  (
    {
      device,
      timeout,
      queryLocation,
      queryType,
      queryVrf,
      queryTarget,
      index,
      resultsComplete,
      setComplete,
    },
    ref,
  ) => {
    const config = useConfig();
    const theme = useTheme();
    const { isSm } = useMedia();
    const { colorMode } = useColorMode();
    let [{ data, loading, error }, refetch] = useAxios({
      url: '/api/query/',
      method: 'post',
      data: {
        query_location: queryLocation,
        query_type: queryType,
        query_vrf: queryVrf,
        query_target: queryTarget,
      },
      timeout: timeout,
      useCache: false,
    });

    const [isOpen, setOpen] = useState(false);
    const [hasOverride, setOverride] = useState(false);

    const handleToggle = () => {
      setOpen(!isOpen);
      setOverride(true);
    };

    const errorKw = (error && error.response?.data?.keywords) || [];

    let errorMsg;
    if (error && error.response?.data?.output) {
      errorMsg = error.response.data.output;
    } else if (error && error.message.startsWith('timeout')) {
      errorMsg = config.messages.request_timeout;
    } else if (error?.response?.statusText) {
      errorMsg = startCase(error.response.statusText);
    } else if (error && error.message) {
      errorMsg = startCase(error.message);
    } else {
      errorMsg = config.messages.general;
    }

    error && console.error(error);

    const errorLevel =
      (error?.response?.data?.level && statusMap[error.response?.data?.level]) ?? 'error';

    const structuredDataComponent = {
      bgp_route: BGPTable,
      bgp_aspath: BGPTable,
      bgp_community: BGPTable,
      ping: TextOutput,
      traceroute: TextOutput,
    };

    let Output = TextOutput;
    let copyValue = data?.output;

    if (data?.format === 'application/json') {
      Output = structuredDataComponent[queryType];
      copyValue = tableToString(queryTarget, data, config);
    }

    if (error) {
      copyValue = errorMsg;
    }

    useEffect(() => {
      !loading && resultsComplete === null && setComplete(index);
    }, [loading, resultsComplete]);

    useEffect(() => {
      resultsComplete === index && !hasOverride && setOpen(true);
    }, [resultsComplete, index]);

    return (
      <AccordionItem
        isOpen={isOpen}
        isDisabled={loading}
        ref={ref}
        css={css({
          '&:last-of-type': { borderBottom: 'none' },
          '&:first-of-type': { borderTop: 'none' },
        })(theme)}>
        <AccordionHeaderWrapper hoverBg="blackAlpha.50">
          <AccordionHeader
            flex="1 0 auto"
            py={2}
            _hover={{}}
            _focus={{}}
            w="unset"
            onClick={handleToggle}>
            <ResultHeader
              title={device.display_name}
              loading={loading}
              error={error}
              errorMsg={errorMsg}
              errorLevel={errorLevel}
              runtime={data?.runtime}
            />
          </AccordionHeader>
          <ButtonGroup px={[1, 1, 3, 3]} py={2}>
            <CopyButton copyValue={copyValue} variant="ghost" isDisabled={loading} />
            <RequeryButton requery={refetch} variant="ghost" isDisabled={loading} />
          </ButtonGroup>
        </AccordionHeaderWrapper>
        <AccordionPanel
          pb={4}
          overflowX="auto"
          css={css({
            WebkitOverflowScrolling: 'touch',
            '&::-webkit-scrollbar': { height: '5px' },
            '&::-webkit-scrollbar-track': {
              backgroundColor: scrollbarBg[colorMode],
            },
            '&::-webkit-scrollbar-thumb': {
              backgroundColor: scrollbar[colorMode],
            },
            '&::-webkit-scrollbar-thumb:hover': {
              backgroundColor: scrollbarHover[colorMode],
            },

            '-ms-overflow-style': { display: 'none' },
          })(theme)}>
          <Flex direction="column" flexWrap="wrap">
            <Flex direction="column" flex="1 0 auto" maxW={error ? '100%' : null}>
              {!error && data && <Output>{data?.output}</Output>}
              {error && (
                <Alert rounded="lg" my={2} py={4} status={errorLevel}>
                  <FormattedError keywords={errorKw} message={errorMsg} />
                </Alert>
              )}
            </Flex>
          </Flex>

          <Flex direction="row" flexWrap="wrap">
            <Flex
              px={3}
              mt={2}
              justifyContent={['flex-start', 'flex-start', 'flex-end', 'flex-end']}
              flex="1 0 auto">
              {config.cache.show_text && data && !error && (
                <>
                  {!isSm && (
                    <CacheTimeout
                      timeout={config.cache.timeout}
                      text={config.web.text.cache_prefix}
                    />
                  )}
                  <Tooltip
                    display={data?.cached ? null : 'none'}
                    hasArrow
                    label={config.web.text.cache_icon.format({
                      time: data?.timestamp,
                    })}
                    placement="top">
                    <Box ml={1} display={data?.cached ? 'block' : 'none'}>
                      <BsLightningFill color={color[colorMode]} />
                    </Box>
                  </Tooltip>
                  {isSm && (
                    <CacheTimeout
                      timeout={config.cache.timeout}
                      text={config.web.text.cache_prefix}
                    />
                  )}
                </>
              )}
            </Flex>
          </Flex>
        </AccordionPanel>
      </AccordionItem>
    );
  },
);
