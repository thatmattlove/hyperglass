import { createState, useState } from '@hookstate/core';
import type { TGlobalState, TUseGlobalState } from './types';

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

const defaultFormData = {
  query_location: [],
  query_target: '',
  query_type: '',
  query_vrf: '',
} as TGlobalState['formData'];

const globalState = createState<TGlobalState>({
  isSubmitting: false,
  formData: defaultFormData,
});

export function useGlobalState(): TUseGlobalState {
  const state = useState<TGlobalState>(globalState);
  function resetForm(): void {
    state.formData.set(defaultFormData);
    state.isSubmitting.set(false);
  }
  return { resetForm, ...state };
}
