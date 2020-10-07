import * as React from 'react';
import { useState } from 'react';
import { Accordion, Box, Stack, useTheme } from '@chakra-ui/core';
import { motion, AnimatePresence } from 'framer-motion';
import { Label, Result } from 'app/components';
import { useConfig, useMedia } from 'app/context';

const AnimatedResult = motion.custom(Result);
const AnimatedLabel = motion.custom(Label);

const labelInitial = {
  left: {
    sm: { opacity: 0, x: -100 },
    md: { opacity: 0, x: -100 },
    lg: { opacity: 0, x: -100 },
    xl: { opacity: 0, x: -100 },
  },
  center: {
    sm: { opacity: 0 },
    md: { opacity: 0 },
    lg: { opacity: 0 },
    xl: { opacity: 0 },
  },
  right: {
    sm: { opacity: 0, x: 100 },
    md: { opacity: 0, x: 100 },
    lg: { opacity: 0, x: 100 },
    xl: { opacity: 0, x: 100 },
  },
};
const labelAnimate = {
  left: {
    sm: { opacity: 1, x: 0 },
    md: { opacity: 1, x: 0 },
    lg: { opacity: 1, x: 0 },
    xl: { opacity: 1, x: 0 },
  },
  center: {
    sm: { opacity: 1 },
    md: { opacity: 1 },
    lg: { opacity: 1 },
    xl: { opacity: 1 },
  },
  right: {
    sm: { opacity: 1, x: 0 },
    md: { opacity: 1, x: 0 },
    lg: { opacity: 1, x: 0 },
    xl: { opacity: 1, x: 0 },
  },
};

export const Results = ({
  queryLocation,
  queryType,
  queryVrf,
  queryTarget,
  setSubmitting,
  ...props
}) => {
  const config = useConfig();
  const theme = useTheme();
  const { mediaSize } = useMedia();
  const matchedVrf =
    config.vrfs.filter(v => v.id === queryVrf)[0] ?? config.vrfs.filter(v => v.id === 'default')[0];
  const [resultsComplete, setComplete] = useState(null);
  return (
    <>
      <Box
        maxW={['100%', '100%', '75%', '50%']}
        w="100%"
        p={0}
        mx="auto"
        my={4}
        textAlign="left"
        {...props}>
        <Stack isInline align="center" justify="center" mt={4} flexWrap="wrap">
          <AnimatePresence>
            {queryLocation && (
              <>
                <AnimatedLabel
                  initial={labelInitial.left[mediaSize]}
                  animate={labelAnimate.left[mediaSize]}
                  transition={{ duration: 0.3, delay: 0.3 }}
                  exit={{ opacity: 0, x: -100 }}
                  label={config.web.text.query_type}
                  value={config.queries[queryType].display_name}
                  valueBg={theme.colors.cyan[500]}
                  fontSize={['xs', 'sm', 'sm', 'sm']}
                />
                <AnimatedLabel
                  initial={labelInitial.center[mediaSize]}
                  animate={labelAnimate.center[mediaSize]}
                  transition={{ duration: 0.3, delay: 0.3 }}
                  exit={{ opacity: 0, scale: 0.5 }}
                  label={config.web.text.query_target}
                  value={queryTarget}
                  valueBg={theme.colors.teal[600]}
                  fontSize={['xs', 'sm', 'sm', 'sm']}
                />
                <AnimatedLabel
                  initial={labelInitial.right[mediaSize]}
                  animate={labelAnimate.right[mediaSize]}
                  transition={{ duration: 0.3, delay: 0.3 }}
                  exit={{ opacity: 0, x: 100 }}
                  label={config.web.text.query_vrf}
                  value={matchedVrf.display_name}
                  valueBg={theme.colors.blue[500]}
                  fontSize={['xs', 'sm', 'sm', 'sm']}
                />
              </>
            )}
          </AnimatePresence>
        </Stack>
      </Box>
      <Box
        maxW={['100%', '100%', '75%', '75%']}
        w="100%"
        p={0}
        mx="auto"
        my={4}
        textAlign="left"
        borderWidth="1px"
        rounded="lg"
        overflow="hidden">
        <Accordion
          allowMultiple
          initial={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 300 }}>
          <AnimatePresence>
            {queryLocation &&
              queryLocation.map((loc, i) => (
                <AnimatedResult
                  initial={{ opacity: 0, y: 300 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: i * 0.3 }}
                  exit={{ opacity: 0, y: 300 }}
                  key={loc}
                  timeout={config.request_timeout * 1000}
                  device={config.devices[loc]}
                  queryLocation={loc}
                  queryType={queryType}
                  queryVrf={queryVrf}
                  queryTarget={queryTarget}
                  setSubmitting={setSubmitting}
                  index={i}
                  resultsComplete={resultsComplete}
                  setComplete={setComplete}
                />
              ))}
          </AnimatePresence>
        </Accordion>
      </Box>
    </>
  );
};
