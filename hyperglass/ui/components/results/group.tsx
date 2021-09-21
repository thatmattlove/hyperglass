import { useEffect } from 'react';
import { Accordion } from '@chakra-ui/react';
import { AnimatePresence } from 'framer-motion';
import { AnimatedDiv } from '~/components';
import { useFormState } from '~/hooks';
import { Result } from './individual';
import { Tags } from './tags';

export const Results: React.FC = () => {
  const { queryLocation } = useFormState(s => s.form);

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
            {queryLocation.length > 0 &&
              queryLocation.map((location, index) => {
                return <Result index={index} key={location} queryLocation={location} />;
              })}
          </AnimatePresence>
        </Accordion>
      </AnimatedDiv>
    </>
  );
};
