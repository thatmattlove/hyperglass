import { forwardRef, useEffect, useMemo, useState } from 'react';
import {
  Box,
  Flex,
  Alert,
  Tooltip,
  ButtonGroup,
  AccordionItem,
  AccordionPanel,
  AccordionButton,
} from '@chakra-ui/react';
import { BsLightningFill } from '@meronex/icons/bs';
import useAxios from 'axios-hooks';
import { startCase } from 'lodash';
import { BGPTable, Countdown, CopyButton, RequeryButton, TextOutput, If } from '~/components';
import { useColorValue, useConfig, useMobile } from '~/context';
import { useStrf, useTableToString } from '~/hooks';
import { FormattedError } from './error';
import { ResultHeader } from './header';

import type { TAccordionHeaderWrapper, TResult } from './types';

type TErrorLevels = 'success' | 'warning' | 'error';

const AccordionHeaderWrapper = (props: TAccordionHeaderWrapper) => {
  const { hoverBg, ...rest } = props;
  return (
    <Flex
      justify="space-between"
      _hover={{ bg: hoverBg }}
      _focus={{ boxShadow: 'outline' }}
      {...rest}
    />
  );
};

export const Result = forwardRef<HTMLDivElement, TResult>((props, ref) => {
  const {
    index,
    device,
    timeout,
    queryVrf,
    queryType,
    queryTarget,
    setComplete,
    queryLocation,
    resultsComplete,
  } = props;

  const { web, cache, messages } = useConfig();
  const isMobile = useMobile();
  const color = useColorValue('black', 'white');
  const scrollbar = useColorValue('blackAlpha.300', 'whiteAlpha.300');
  const scrollbarHover = useColorValue('blackAlpha.400', 'whiteAlpha.400');
  const scrollbarBg = useColorValue('blackAlpha.50', 'whiteAlpha.50');

  let [{ data, loading, error }, refetch] = useAxios(
    {
      url: '/api/query/',
      method: 'post',
      data: {
        query_vrf: queryVrf,
        query_type: queryType,
        query_target: queryTarget,
        query_location: queryLocation,
      },
      timeout,
    },
    { useCache: false },
  );

  const cacheLabel = useStrf(web.text.cache_icon, { time: data?.timestamp }, [data?.timestamp]);

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
    errorMsg = messages.request_timeout;
  } else if (error?.response?.statusText) {
    errorMsg = startCase(error.response.statusText);
  } else if (error && error.message) {
    errorMsg = startCase(error.message);
  } else {
    errorMsg = messages.general;
  }

  error && console.error(error);

  const getErrorLevel = (): TErrorLevels => {
    const statusMap = {
      success: 'success',
      warning: 'warning',
      error: 'warning',
      danger: 'error',
    } as { [k in TResponseLevel]: 'success' | 'warning' | 'error' };

    let e: TErrorLevels = 'error';

    if (error?.response?.data?.level) {
      const idx = error.response.data.level as TResponseLevel;
      e = statusMap[idx];
    }
    return e;
  };

  const errorLevel = useMemo(() => getErrorLevel(), [error]);

  const tableComponent = useMemo(() => typeof queryType.match(/^bgp_\w+$/) !== null, [queryType]);

  let copyValue = data?.output;

  const formatData = useTableToString(queryTarget, data, [data.format]);

  if (data?.format === 'application/json') {
    copyValue = formatData();
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
      ref={ref}
      isOpen={isOpen}
      isDisabled={loading}
      css={{
        '&:last-of-type': { borderBottom: 'none' },
        '&:first-of-type': { borderTop: 'none' },
      }}>
      <AccordionHeaderWrapper hoverBg="blackAlpha.50">
        <AccordionButton
          py={2}
          w="unset"
          _hover={{}}
          _focus={{}}
          flex="1 0 auto"
          onClick={handleToggle}>
          <ResultHeader
            error={error}
            loading={loading}
            errorMsg={errorMsg}
            errorLevel={errorLevel}
            runtime={data?.runtime}
            title={device.display_name}
          />
        </AccordionButton>
        <ButtonGroup px={[1, 1, 3, 3]} py={2}>
          <CopyButton copyValue={copyValue} isDisabled={loading} />
          <RequeryButton requery={refetch} variant="ghost" isDisabled={loading} />
        </ButtonGroup>
      </AccordionHeaderWrapper>
      <AccordionPanel
        pb={4}
        overflowX="auto"
        css={{
          WebkitOverflowScrolling: 'touch',
          '&::-webkit-scrollbar': { height: '5px' },
          '&::-webkit-scrollbar-track': {
            backgroundColor: scrollbarBg,
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: scrollbar,
          },
          '&::-webkit-scrollbar-thumb:hover': {
            backgroundColor: scrollbarHover,
          },

          '-ms-overflow-style': { display: 'none' },
        }}>
        <Flex direction="column" flexWrap="wrap">
          <Flex direction="column" flex="1 0 auto" maxW={error ? '100%' : undefined}>
            <If c={!error && data}>
              <If c={tableComponent}>
                <BGPTable>{data?.output}</BGPTable>
              </If>
              <If c={!tableComponent}>
                <TextOutput>{data?.output}</TextOutput>
              </If>
            </If>

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
            <If c={cache.show_text && data && !error}>
              <If c={!isMobile}>
                <Countdown timeout={cache.timeout} text={web.text.cache_prefix} />
              </If>
              <Tooltip
                display={!data?.cached ? 'none' : undefined}
                hasArrow
                label={cacheLabel}
                placement="top">
                <Box ml={1} display={data?.cached ? 'block' : 'none'}>
                  <BsLightningFill color={color} />
                </Box>
              </Tooltip>
              <If c={isMobile}>
                <Countdown timeout={cache.timeout} text={web.text.cache_prefix} />
              </If>
            </If>
          </Flex>
        </Flex>
      </AccordionPanel>
    </AccordionItem>
  );
});
