import dynamic from 'next/dynamic';
import { AnimatePresence } from 'framer-motion';
import { If, Then, Else } from 'react-if';
import { Loading } from '~/elements';
import { useView } from '~/hooks';

import type { NextPage } from 'next';

const LookingGlassForm = dynamic<Dict>(
  () => import('~/components/looking-glass-form').then(i => i.LookingGlassForm),
  {
    loading: Loading,
  },
);

const Results = dynamic<Dict>(() => import('~/components/results').then(i => i.Results), {
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
