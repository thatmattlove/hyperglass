import { AnimatePresence } from 'framer-motion';
import { LookingGlass, Results } from '~/components';
import { useView } from '~/hooks';
import { Frame } from './frame';

export const Layout = (): JSX.Element => {
  const view = useView();
  return (
    <Frame>
      {view === 'results' ? (
        <Results />
      ) : (
        <AnimatePresence>
          <LookingGlass />
        </AnimatePresence>
      )}
    </Frame>
  );
};
