import { useState } from 'react';
import { Accordion, Box, Stack, useToken } from '@chakra-ui/react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnimatedDiv, Label } from '~/components';
import { useConfig, useBreakpointValue } from '~/context';
import { useDevice } from '~/hooks';
import { isQueryType } from '~/types';
import { Result } from './individual';

import type { TResults } from './types';

export const Results = (props: TResults) => {
  const { queryLocation, queryType, queryVrf, queryTarget, ...rest } = props;
  const { request_timeout, queries, vrfs, web } = useConfig();
  const getDevice = useDevice();
  const targetBg = useToken('colors', 'teal.600');
  const queryBg = useToken('colors', 'cyan.500');
  const vrfBg = useToken('colors', 'blue.500');

  const animateLeft = useBreakpointValue({
    base: { opacity: 1, x: 0 },
    md: { opacity: 1, x: 0 },
    lg: { opacity: 1, x: 0 },
    xl: { opacity: 1, x: 0 },
  });

  const animateCenter = useBreakpointValue({
    base: { opacity: 1 },
    md: { opacity: 1 },
    lg: { opacity: 1 },
    xl: { opacity: 1 },
  });

  const animateRight = useBreakpointValue({
    base: { opacity: 1, x: 0 },
    md: { opacity: 1, x: 0 },
    lg: { opacity: 1, x: 0 },
    xl: { opacity: 1, x: 0 },
  });

  const initialLeft = useBreakpointValue({
    base: { opacity: 0, x: -100 },
    md: { opacity: 0, x: -100 },
    lg: { opacity: 0, x: -100 },
    xl: { opacity: 0, x: -100 },
  });

  const initialCenter = useBreakpointValue({
    base: { opacity: 0 },
    md: { opacity: 0 },
    lg: { opacity: 0 },
    xl: { opacity: 0 },
  });

  const initialRight = useBreakpointValue({
    base: { opacity: 0, x: 100 },
    md: { opacity: 0, x: 100 },
    lg: { opacity: 0, x: 100 },
    xl: { opacity: 0, x: 100 },
  });

  const [resultsComplete, setComplete] = useState<number | null>(null);

  const matchedVrf =
    vrfs.filter(v => v.id === queryVrf)[0] ?? vrfs.filter(v => v.id === 'default')[0];

  let queryTypeLabel = '';
  if (isQueryType(queryType)) {
    queryTypeLabel = queries[queryType].display_name;
  }

  return (
    <>
      <Box
        p={0}
        my={4}
        w="100%"
        mx="auto"
        textAlign="left"
        maxW={{ base: '100%', lg: '75%', xl: '50%' }}
        {...rest}>
        <Stack isInline align="center" justify="center" mt={4} flexWrap="wrap">
          <AnimatePresence>
            {queryLocation && (
              <>
                <motion.div
                  initial={initialLeft}
                  animate={animateLeft}
                  exit={{ opacity: 0, x: -100 }}
                  transition={{ duration: 0.3, delay: 0.3 }}>
                  <Label
                    bg={queryBg}
                    label={web.text.query_type}
                    fontSize={{ base: 'xs', md: 'sm' }}
                    value={queryTypeLabel}
                  />
                </motion.div>
                <motion.div
                  initial={initialCenter}
                  animate={animateCenter}
                  exit={{ opacity: 0, scale: 0.5 }}
                  transition={{ duration: 0.3, delay: 0.3 }}>
                  <Label
                    bg={targetBg}
                    value={queryTarget}
                    label={web.text.query_target}
                    fontSize={{ base: 'xs', md: 'sm' }}
                  />
                </motion.div>
                <motion.div
                  initial={initialRight}
                  animate={animateRight}
                  exit={{ opacity: 0, x: 100 }}
                  transition={{ duration: 0.3, delay: 0.3 }}>
                  <Label
                    bg={vrfBg}
                    label={web.text.query_vrf}
                    value={matchedVrf.display_name}
                    fontSize={{ base: 'xs', md: 'sm' }}
                  />
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </Stack>
      </Box>
      <AnimatedDiv
        p={0}
        my={4}
        w="100%"
        mx="auto"
        rounded="lg"
        textAlign="left"
        borderWidth="1px"
        overflow="hidden"
        initial={{ opacity: 1 }}
        exit={{ opacity: 0, y: 300 }}
        transition={{ duration: 0.3 }}
        animate={{ opacity: 1, y: 0 }}
        maxW={{ base: '100%', md: '75%' }}>
        <Accordion allowMultiple>
          <AnimatePresence>
            {queryLocation &&
              queryLocation.map((loc, i) => {
                const device = getDevice(loc);
                return (
                  <motion.div
                    animate={{ opacity: 1, y: 0 }}
                    initial={{ opacity: 0, y: 300 }}
                    transition={{ duration: 0.3, delay: i * 0.3 }}
                    exit={{ opacity: 0, y: 300 }}>
                    <Result
                      key={loc}
                      index={i}
                      device={device}
                      queryLocation={loc}
                      queryVrf={queryVrf}
                      queryType={queryType}
                      queryTarget={queryTarget}
                      setComplete={setComplete}
                      timeout={request_timeout * 1000}
                      resultsComplete={resultsComplete}
                    />
                  </motion.div>
                );
              })}
          </AnimatePresence>
        </Accordion>
      </AnimatedDiv>
    </>
  );
};
