import { AnimatePresence } from 'framer-motion';
import { LookingGlass, Results } from '~/components';
import { useLGMethods } from '~/hooks';
import { Frame } from './frame';

export const Layout: React.FC = () => {
  const { formReady } = useLGMethods();
  return (
    <Frame>
      {formReady() ? (
        <Results />
      ) : (
        <AnimatePresence>
          <LookingGlass />
        </AnimatePresence>
      )}
    </Frame>
  );
};
