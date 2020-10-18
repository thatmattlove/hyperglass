import { createState, useState } from '@hookstate/core';
import type { IGlobalState } from './types';

// const StateContext = createContext(null);

// export const StateProvider = ({ children }) => {
//   const [isSubmitting, setSubmitting] = useState(false);
//   const [formData, setFormData] = useState({});
//   const [greetingAck, setGreetingAck] = useSessionStorage('hyperglass-greeting-ack', false);
//   const resetForm = layoutRef => {
//     layoutRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
//     setSubmitting(false);
//     setFormData({});
//   };
//   const value = useMemo(() => ({
//     isSubmitting,
//     setSubmitting,
//     formData,
//     setFormData,
//     greetingAck,
//     setGreetingAck,
//     resetForm,
//   }));
//   return <StateContext.Provider value={value}>{children}</StateContext.Provider>;
// };

// export const useHyperglassState = () => useContext(StateContext);

export const globalState = createState<IGlobalState>({
  isSubmitting: false,
  formData: { query_location: [], query_target: '', query_type: '', query_vrf: '' },
});
export const useGlobalState = () => useState(globalState);
