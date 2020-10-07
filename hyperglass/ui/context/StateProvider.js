import * as React from 'react';
import { createContext, useContext, useMemo, useState } from 'react';
import { useSessionStorage } from 'app/hooks';

const StateContext = createContext(null);

export const StateProvider = ({ children }) => {
  const [isSubmitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({});
  const [greetingAck, setGreetingAck] = useSessionStorage('hyperglass-greeting-ack', false);
  const resetForm = layoutRef => {
    layoutRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    setSubmitting(false);
    setFormData({});
  };
  const value = useMemo(() => ({
    isSubmitting,
    setSubmitting,
    formData,
    setFormData,
    greetingAck,
    setGreetingAck,
    resetForm,
  }));
  return <StateContext.Provider value={value}>{children}</StateContext.Provider>;
};

export const useHyperglassState = () => useContext(StateContext);
