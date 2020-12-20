import { AnimatePresence } from 'framer-motion';
import { If, HyperglassForm, Results } from '~/components';
import { useLGState } from '~/hooks';
import { all } from '~/util';
import { Frame } from './frame';

export const Layout: React.FC = () => {
  const { isSubmitting, formData } = useLGState();
  return (
    <Frame>
      <If
        c={
          isSubmitting.value &&
          all(
            formData.query_location.value,
            formData.query_target.value,
            formData.query_type.value,
            formData.query_vrf.value,
          )
        }>
        <Results />
      </If>
      <AnimatePresence>
        <If c={!isSubmitting.value}>
          <HyperglassForm />
        </If>
      </AnimatePresence>
    </Frame>
  );
};
