import { forwardRef, useEffect, useMemo } from 'react';
import {
  Box,
  Flex,
  chakra,
  Icon,
  Alert,
  HStack,
  Tooltip,
  AccordionItem,
  AccordionPanel,
  useAccordionContext,
  AccordionButton,
} from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { BsLightningFill } from '@meronex/icons/bs';
import { startCase } from 'lodash';
import { BGPTable, Countdown, TextOutput, If, Path } from '~/components';
import { useColorValue, useConfig, useMobile } from '~/context';
import { useStrf, useLGQuery, useLGState, useTableToString } from '~/hooks';
import { isStructuredOutput, isStringOutput } from '~/types';
import { isStackError, isFetchError, isLGError, isLGOutputOrError } from './guards';
import { RequeryButton } from './requeryButton';
import { CopyButton } from './copyButton';
import { FormattedError } from './error';
import { ResultHeader } from './header';

import type { TResult, TErrorLevels } from './types';

const AnimatedAccordionItem = motion.custom(AccordionItem);

const AccordionHeaderWrapper = chakra('div', {
  baseStyle: {
    display: 'flex',
    justifyContent: 'space-between',
    _hover: { bg: 'blackAlpha.50' },
    _focus: { boxShadow: 'outline' },
  },
});

const _Result: React.ForwardRefRenderFunction<HTMLDivElement, TResult> = (props: TResult, ref) => {
  const { index, device, queryVrf, queryType, queryTarget, queryLocation } = props;

  const { web, cache, messages } = useConfig();
  const { index: indices, setIndex } = useAccordionContext();

  const isMobile = useMobile();
  const color = useColorValue('black', 'white');
  const scrollbar = useColorValue('blackAlpha.300', 'whiteAlpha.300');
  const scrollbarHover = useColorValue('blackAlpha.400', 'whiteAlpha.400');
  const scrollbarBg = useColorValue('blackAlpha.50', 'whiteAlpha.50');

  const { responses } = useLGState();

  const { data, error, isError, isLoading, refetch, isFetching, isFetchedAfterMount } = useLGQuery({
    queryLocation,
    queryTarget,
    queryType,
    queryVrf,
  });

  const isCached = useMemo(() => data?.cached || !isFetchedAfterMount, [
    data,
    isLoading,
    isFetching,
  ]);

  if (typeof data !== 'undefined') {
    responses.merge({ [device._id]: data });
  }

  const cacheLabel = useStrf(web.text.cache_icon, { time: data?.timestamp }, [data?.timestamp]);

  const errorKeywords = useMemo(() => {
    let kw = [] as string[];
    if (isLGError(data)) {
      kw = data.keywords;
    }
    return kw;
  }, [data]);

  // Parse the the response and/or the error to determine from where to extract the error message.
  const errorMsg = useMemo(() => {
    if (isLGError(error)) {
      return error.output as string;
    } else if (isLGOutputOrError(data)) {
      return data.output as string;
    } else if (isFetchError(error)) {
      return startCase(error.statusText);
    } else if (isStackError(error) && error.message.toLowerCase().startsWith('timeout')) {
      return messages.request_timeout;
    } else if (isStackError(error)) {
      return startCase(error.message);
    } else {
      return messages.general;
    }
  }, [isError, error, data]);

  isError && console.error(error);

  const errorLevel = useMemo<TErrorLevels>(() => {
    const statusMap = {
      success: 'success',
      warning: 'warning',
      error: 'warning',
      danger: 'error',
    } as { [k in TResponseLevel]: 'success' | 'warning' | 'error' };

    let e: TErrorLevels = 'error';

    if (isLGError(error)) {
      const idx = error.level as TResponseLevel;
      e = statusMap[idx];
    }
    return e;
  }, [isError, isLoading, data]);

  const tableComponent = useMemo<boolean>(() => {
    let result = false;
    if (typeof queryType.match(/^bgp_\w+$/) !== null && data?.format === 'application/json') {
      result = true;
    }
    return result;
  }, [queryType, data?.format]);

  let copyValue = data?.output as string;

  const formatData = useTableToString(queryTarget, data, [data?.format]);

  if (data?.format === 'application/json') {
    copyValue = formatData();
  }

  if (error) {
    copyValue = errorMsg;
  }

  // Signal to the group that this result is done loading.
  useEffect(() => {
    // Only set the index if it's not already set and the query is finished loading.
    if (Array.isArray(indices) && indices.length === 0 && !isLoading) {
      // Only set the index if the response has data or an error.
      if (data || isError) {
        setIndex([index]);
      }
    }
  }, [data, isError]);

  return (
    <AnimatedAccordionItem
      ref={ref}
      id={device._id}
      isDisabled={isLoading}
      exit={{ opacity: 0, y: 300 }}
      animate={{ opacity: 1, y: 0 }}
      initial={{ opacity: 0, y: 300 }}
      transition={{ duration: 0.3, delay: index * 0.3 }}
      css={{
        '&:first-of-type': { borderTop: 'none' },
        '&:last-of-type': { borderBottom: 'none' },
      }}
    >
      <>
        <AccordionHeaderWrapper>
          <AccordionButton py={2} w="unset" _hover={{}} _focus={{}} flex="1 0 auto">
            <ResultHeader
              // isError={isLGOutputOrError(data)}
              isError={isError}
              loading={isLoading}
              errorMsg={errorMsg}
              errorLevel={errorLevel}
              runtime={data?.runtime ?? 0}
              title={device.name}
            />
          </AccordionButton>
          <HStack py={2} spacing={1}>
            {isStructuredOutput(data) && data.level === 'success' && tableComponent && (
              <Path device={device._id} />
            )}
            <CopyButton copyValue={copyValue} isDisabled={isLoading} />
            <RequeryButton requery={refetch} isDisabled={isLoading} />
          </HStack>
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
          }}
        >
          <Box>
            <Flex direction="column" flex="1 0 auto" maxW={error ? '100%' : undefined}>
              {!isError && typeof data !== 'undefined' ? (
                <>
                  {isStructuredOutput(data) && data.level === 'success' && tableComponent ? (
                    <BGPTable>{data.output}</BGPTable>
                  ) : isStringOutput(data) && data.level === 'success' && !tableComponent ? (
                    <TextOutput>{data.output}</TextOutput>
                  ) : isStringOutput(data) && data.level !== 'success' ? (
                    <Alert rounded="lg" my={2} py={4} status={errorLevel} variant="solid">
                      <FormattedError message={data.output} keywords={errorKeywords} />
                    </Alert>
                  ) : (
                    <Alert rounded="lg" my={2} py={4} status={errorLevel} variant="solid">
                      <FormattedError message={errorMsg} keywords={errorKeywords} />
                    </Alert>
                  )}
                </>
              ) : (
                <Alert rounded="lg" my={2} py={4} status={errorLevel} variant="solid">
                  <FormattedError message={errorMsg} keywords={errorKeywords} />
                </Alert>
              )}
            </Flex>
          </Box>

          <Flex direction="row" flexWrap="wrap">
            <HStack
              px={3}
              mt={2}
              spacing={1}
              flex="1 0 auto"
              justifyContent={{ base: 'flex-start', lg: 'flex-end' }}
            >
              <If c={cache.show_text && !isError && isCached}>
                <If c={!isMobile}>
                  <Countdown timeout={cache.timeout} text={web.text.cache_prefix} />
                </If>
                <Tooltip hasArrow label={cacheLabel} placement="top">
                  <Box>
                    <Icon as={BsLightningFill} color={color} />
                  </Box>
                </Tooltip>
                <If c={isMobile}>
                  <Countdown timeout={cache.timeout} text={web.text.cache_prefix} />
                </If>
              </If>
            </HStack>
          </Flex>
        </AccordionPanel>
      </>
    </AnimatedAccordionItem>
  );
};

export const Result = forwardRef<HTMLDivElement, TResult>(_Result);
