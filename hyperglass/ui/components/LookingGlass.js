import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Layout, HyperglassForm, Results } from 'app/components';
import { useHyperglassState } from 'app/context';

const AnimatedForm = motion.custom(HyperglassForm);

export const LookingGlass = () => {
  const {
    isSubmitting,
    setSubmitting,
    formData,
    setFormData,
    greetingAck,
    setGreetingAck,
  } = useHyperglassState();

  return (
    <Layout>
      {isSubmitting && formData && (
        <Results
          queryLocation={formData.query_location}
          queryType={formData.query_type}
          queryVrf={formData.query_vrf}
          queryTarget={formData.query_target}
          setSubmitting={setSubmitting}
        />
      )}
      <AnimatePresence>
        {!isSubmitting && (
          <AnimatedForm
            initial={{ opacity: 0, y: 300 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            exit={{ opacity: 0, x: -300 }}
            isSubmitting={isSubmitting}
            setSubmitting={setSubmitting}
            setFormData={setFormData}
            greetingAck={greetingAck}
            setGreetingAck={setGreetingAck}
          />
        )}
      </AnimatePresence>
    </Layout>
  );
};
