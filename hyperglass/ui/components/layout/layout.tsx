import { AnimatePresence } from 'framer-motion';
import { If, HyperglassForm, Results } from '~/components';
import { useGlobalState } from '~/context';
import { all } from '~/util';
import { Frame } from './frame';

export const Layout: React.FC = () => {
  const { isSubmitting, formData } = useGlobalState();

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
        <Results
          queryLocation={formData.query_location.value}
          queryType={formData.query_type.value}
          queryVrf={formData.query_vrf.value}
          queryTarget={formData.query_target.value}
        />
      </If>
      <AnimatePresence>
        <If c={!isSubmitting.value}>
          <HyperglassForm />
        </If>
      </AnimatePresence>
    </Frame>
  );
};
