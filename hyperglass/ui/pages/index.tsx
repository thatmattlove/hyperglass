import dynamic from 'next/dynamic';
import { If, Then, Else } from 'react-if';
import { Loading } from '~/elements';
import { useView } from '~/hooks';

import type { NextPage } from 'next';
import type { AnimatePresenceProps } from 'framer-motion';

const AnimatePresence = dynamic<AnimatePresenceProps>(() =>
  import('framer-motion').then(i => i.AnimatePresence),
);

const LookingGlassForm = dynamic<Dict>(() => import('~/components').then(i => i.LookingGlassForm), {
  loading: Loading,
});

const Results = dynamic<Dict>(() => import('~/components').then(i => i.Results), {
  loading: Loading,
});

const Index: NextPage = () => {
  const view = useView();
  return (
    <If condition={view === 'results'}>
      <Then>
        <Results />
      </Then>
      <Else>
        <AnimatePresence>
          <LookingGlassForm />
        </AnimatePresence>
      </Else>
    </If>
  );
};

export default Index;
