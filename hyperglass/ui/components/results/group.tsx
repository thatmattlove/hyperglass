import { useEffect } from 'react';
import { Accordion } from '@chakra-ui/react';
import { AnimatePresence } from 'framer-motion';
import { AnimatedDiv } from '~/components';
import { useDevice, useLGState } from '~/hooks';
import { Result } from './individual';
import { Tags } from './tags';

export const Results: React.FC = () => {
  const { queryLocation, queryTarget, queryType, queryVrf } = useLGState();

  const getDevice = useDevice();

  // Scroll to the top of the page when results load - primarily for mobile.
  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.scrollTo(0, 0);
    }
  }, []);

  return (
    <>
      <Tags />
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
        maxW={{ base: '100%', md: '75%' }}
      >
        <Accordion allowMultiple allowToggle>
          <AnimatePresence>
            {queryLocation.value &&
              queryLocation.map((loc, i) => {
                const device = getDevice(loc.value);
                return (
                  <Result
                    index={i}
                    device={device}
                    key={device._id}
                    queryLocation={loc.value}
                    queryVrf={queryVrf.value}
                    queryType={queryType.value}
                    queryTarget={queryTarget.value}
                  />
                );
              })}
          </AnimatePresence>
        </Accordion>
      </AnimatedDiv>
    </>
  );
};
