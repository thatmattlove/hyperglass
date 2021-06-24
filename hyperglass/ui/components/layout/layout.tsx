import { AnimatePresence } from 'framer-motion';
import { LookingGlass, Results } from '~/components';
import { useLGMethods } from '~/hooks';
import { Frame } from './frame';

export const Layout: React.FC = () => {
  const { formReady } = useLGMethods();
  const ready = formReady();
  console.log('ready', ready);
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
