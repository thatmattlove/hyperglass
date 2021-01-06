import { Box, Stack, useToken } from '@chakra-ui/react';
import { motion, AnimatePresence } from 'framer-motion';
import { Label } from '~/components';
import { useConfig, useBreakpointValue } from '~/context';
import { useLGState } from '~/hooks';
import { isQueryType } from '~/types';

import type { Transition } from 'framer-motion';

const transition = { duration: 0.3, delay: 0.5 } as Transition;

export const Tags: React.FC = () => {
  const { queries, vrfs, web } = useConfig();
  const { queryLocation, queryTarget, queryType, queryVrf } = useLGState();

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
    base: { opacity: 0, x: '-100%' },
    md: { opacity: 0, x: '-100%' },
    lg: { opacity: 0, x: '-100%' },
    xl: { opacity: 0, x: '-100%' },
  });

  const initialCenter = useBreakpointValue({
    base: { opacity: 0 },
    md: { opacity: 0 },
    lg: { opacity: 0 },
    xl: { opacity: 0 },
  });

  const initialRight = useBreakpointValue({
    base: { opacity: 0, x: '100%' },
    md: { opacity: 0, x: '100%' },
    lg: { opacity: 0, x: '100%' },
    xl: { opacity: 0, x: '100%' },
  });

  let queryTypeLabel = '';
  if (isQueryType(queryType.value)) {
    queryTypeLabel = queries[queryType.value].display_name;
  }

  const matchedVrf =
    vrfs.filter(v => v.id === queryVrf.value)[0] ?? vrfs.filter(v => v.id === 'default')[0];

  return (
    <Box
      p={0}
      my={4}
      w="100%"
      mx="auto"
      textAlign="left"
      maxW={{ base: '100%', lg: '75%', xl: '50%' }}
    >
      <Stack isInline align="center" justify="center" mt={4} flexWrap="wrap">
        <AnimatePresence>
          {queryLocation.value && (
            <>
              <motion.div
                initial={initialLeft}
                animate={animateLeft}
                exit={{ opacity: 0, x: '-100%' }}
                transition={transition}
              >
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
                transition={transition}
              >
                <Label
                  bg={targetBg}
                  value={queryTarget.value}
                  label={web.text.query_target}
                  fontSize={{ base: 'xs', md: 'sm' }}
                />
              </motion.div>
              <motion.div
                initial={initialRight}
                animate={animateRight}
                exit={{ opacity: 0, x: '100%' }}
                transition={transition}
              >
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
  );
};
