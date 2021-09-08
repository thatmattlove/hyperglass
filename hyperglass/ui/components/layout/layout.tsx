import { AnimatePresence } from 'framer-motion';
import { LookingGlass, Results } from '~/components';
import { useLGMethods } from '~/hooks';
import { Frame } from './frame';

export const Layout: React.FC = () => {
  const { formReady } = useLGMethods();
  const ready = formReady();
  return (
    <Frame>
      {ready ? (
        <Results />
      ) : (
        <AnimatePresence>
          <LookingGlass />
        </AnimatePresence>
      )}
    </Frame>
  );
};
