import { forwardRef, memo, useEffect, useMemo } from 'react';
import {
  Box,
  Flex,
  Alert,
  chakra,
  HStack,
  Tooltip,
  useToast,
  AccordionItem,
  AccordionPanel,
  AccordionButton,
  useAccordionContext,
} from '@chakra-ui/react';
import { motion } from 'framer-motion';
import startCase from 'lodash/startCase';
import isEqual from 'react-fast-compare';
import { If, Then, Else } from 'react-if';
import { BGPTable, Countdown, DynamicIcon, Path, TextOutput } from '~/components';
import { useColorValue, useConfig, useMobile } from '~/context';
import { useStrf, useLGQuery, useTableToString, useFormState, useDevice } from '~/hooks';
import { isStructuredOutput, isStringOutput } from '~/types';
import { isStackError, isFetchError, isLGError, isLGOutputOrError } from './guards';
import { RequeryButton } from './requery-button';
import { CopyButton } from './copy-button';
import { FormattedError } from './formatted-error';
import { ResultHeader } from './header';

import type { ErrorLevels } from '~/types';

interface ResultProps {
  index: number;
  queryLocation: string;
}

const AnimatedAccordionItem = motion(AccordionItem);

const AccordionHeaderWrapper = chakra('div', {
  baseStyle: {
    display: 'flex',
    justifyContent: 'space-between',
    _hover: { bg: 'blackAlpha.50' },
    _focus: { boxShadow: 'outline' },
  },
});

const _Result: React.ForwardRefRenderFunction<HTMLDivElement, ResultProps> = (
  props: ResultProps,
  ref,
) => {
  const { index, queryLocation } = props;
  const toast = useToast();
  const { web, cache, messages } = useConfig();
  const { index: indices, setIndex } = useAccordionContext();
  const getDevice = useDevice();
  const device = getDevice(queryLocation);

  const isMobile = useMobile();
  const color = useColorValue('black', 'white');
  const scrollbar = useColorValue('blackAlpha.300', 'whiteAlpha.300');
  const scrollbarHover = useColorValue('blackAlpha.400', 'whiteAlpha.400');
  const scrollbarBg = useColorValue('blackAlpha.50', 'whiteAlpha.50');

  const addResponse = useFormState(s => s.addResponse);
  const form = useFormState(s => s.form);

  const { data, error, isError, isLoading, refetch, isFetchedAfterMount } = useLGQuery(
    {
      queryLocation,
      queryTarget: form.queryTarget,
      queryType: form.queryType,
    },
    {
      onSuccess(data) {
        if (device !== null) {
          addResponse(device.id, data);
        }
      },
      onError(error) {
        console.error(error);
      },
    },
  );
  const isCached = useMemo(() => data?.cached || !isFetchedAfterMount, [data, isFetchedAfterMount]);

  const strF = useStrf();
  const cacheLabel = strF(web.text.cacheIcon, { time: data?.timestamp });

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
      return messages.requestTimeout;
    } else if (isStackError(error)) {
      return startCase(error.message);
    } else {
      return messages.general;
    }
  }, [error, data, messages.general, messages.requestTimeout]);

  const errorLevel = useMemo<ErrorLevels>(() => {
    const statusMap = {
      success: 'success',
      warning: 'warning',
      error: 'warning',
      danger: 'error',
    } as { [K in ResponseLevel]: 'success' | 'warning' | 'error' };

    let e: ErrorLevels = 'error';

    if (isLGError(error)) {
      const idx = error.level as ResponseLevel;
      e = statusMap[idx];
    }
    return e;
  }, [error]);

  const tableComponent = useMemo<boolean>(() => {
    let result = false;
    if (data?.format === 'application/json') {
      result = true;
    }
    return result;
  }, [data?.format]);

  let copyValue = data?.output as string;

  const formatData = useTableToString(form.queryTarget, data, [data?.format]);

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
  }, [data, index, indices, isLoading, isError, setIndex]);

  if (device === null) {
    const id = `toast-queryLocation-${index}-${queryLocation}`;
    if (!toast.isActive(id)) {
      toast({
        id,
        title: messages.general,
        description: `Configuration for device with ID '${queryLocation}' not found.`,
        status: 'error',
        isClosable: true,
      });
    }
    return <></>;
  }

  return (
    <AnimatedAccordionItem
      ref={ref}
      id={device.id}
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
      <AccordionHeaderWrapper>
        <AccordionButton py={2} w="unset" _hover={{}} _focus={{}} flex="1 0 auto">
          <ResultHeader
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
            <Path device={device.id} />
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
            <If condition={cache.showText && !isError && isCached}>
              <If condition={isMobile}>
                <Then>
                  <Countdown timeout={cache.timeout} text={web.text.cachePrefix} />
                  <Tooltip hasArrow label={cacheLabel} placement="top">
                    <Box>
                      <DynamicIcon icon={{ bs: 'BsLightningFill' }} color={color} />
                    </Box>
                  </Tooltip>
                </Then>
                <Else>
                  <Tooltip hasArrow label={cacheLabel} placement="top">
                    <Box>
                      <DynamicIcon icon={{ bs: 'BsLightningFill' }} color={color} />
                    </Box>
                  </Tooltip>
                  <Countdown timeout={cache.timeout} text={web.text.cachePrefix} />
                </Else>
              </If>
            </If>
          </HStack>
        </Flex>
      </AccordionPanel>
    </AnimatedAccordionItem>
  );
};

export const Result = memo(forwardRef<HTMLDivElement, ResultProps>(_Result), isEqual);
