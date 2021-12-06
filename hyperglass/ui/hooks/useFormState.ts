import { useMemo } from 'react';
import create from 'zustand';
import intersectionWith from 'lodash/intersectionWith';
import plur from 'plur';
import isEqual from 'react-fast-compare';
import { all, andJoin, dedupObjectArray, withDev } from '~/util';

import type { SingleValue, MultiValue } from 'react-select';
import type { StateCreator } from 'zustand';
import { UseFormSetError, UseFormClearErrors } from 'react-hook-form';
import type { SingleOption, Directive, FormData, Text } from '~/types';
import type { UseDevice } from './types';

type FormStatus = 'form' | 'results';

interface FormValues {
  queryLocation: string[];
  queryTarget: string;
  queryType: string;
}

/**
 * Selected *options*, vs. values.
 */
interface FormSelections<Opt extends SingleOption = SingleOption> {
  queryLocation: MultiValue<Opt>;
  queryType: SingleValue<Opt>;
}

interface Filtered {
  types: Directive[];
  groups: string[];
}

interface Responses {
  [deviceId: string]: QueryResponse;
}

interface Target {
  display: string;
}

interface FormStateType<Opt extends SingleOption = SingleOption> {
  // Values
  filtered: Filtered;
  form: FormValues;
  loading: boolean;
  responses: Responses;
  selections: FormSelections<Opt>;
  status: FormStatus;
  target: Target;
  resolvedIsOpen: boolean;

  // Methods
  resolvedOpen(): void;
  resolvedClose(): void;
  response(deviceId: string): QueryResponse | null;
  addResponse(deviceId: string, data: QueryResponse): void;
  setLoading(value: boolean): void;
  setStatus(value: FormStatus): void;
  setSelection<
    Opt extends SingleOption,
    K extends keyof FormSelections<Opt> = keyof FormSelections<Opt>,
  >(
    field: K,
    value: FormSelections[K],
  ): void;
  setTarget(update: Partial<Target>): void;
  getDirective(): Directive | null;
  reset(): void;
  setFormValue<K extends keyof FormValues>(field: K, value: FormValues[K]): void;
  locationChange(
    locations: string[],
    extra: {
      setError: UseFormSetError<FormData>;
      clearErrors: UseFormClearErrors<FormData>;
      getDevice: UseDevice;
      text: Text;
    },
  ): void;
}

const formState: StateCreator<FormStateType> = (set, get) => ({
  filtered: { types: [], groups: [] },
  form: { queryLocation: [], queryTarget: '', queryType: '' },
  loading: false,
  responses: {},
  selections: { queryLocation: [], queryType: null },
  status: 'form',
  target: { display: '' },
  resolvedIsOpen: false,

  setFormValue<K extends keyof FormValues>(field: K, value: FormValues[K]): void {
    set(state => ({ form: { ...state.form, [field]: value } }));
  },

  setLoading(loading: boolean): void {
    set({ loading });
  },

  setStatus(status: FormStatus): void {
    set({ status });
  },

  setSelection<
    Opt extends SingleOption,
    K extends keyof FormSelections<Opt> = keyof FormSelections<Opt>,
  >(field: K, value: FormSelections[K]): void {
    set(state => ({ selections: { ...state.selections, [field]: value } }));
  },

  setTarget(update: Partial<Target>): void {
    set(state => ({ target: { ...state.target, ...update } }));
  },

  resolvedOpen(): void {
    set({ resolvedIsOpen: true });
  },

  resolvedClose(): void {
    set({ resolvedIsOpen: false });
  },

  addResponse(deviceId: string, data: QueryResponse): void {
    set(state => ({ responses: { ...state.responses, [deviceId]: data } }));
  },

  getDirective(): Directive | null {
    const { form, filtered } = get();
    const [matching] = filtered.types.filter(t => t.id === form.queryType);
    if (typeof matching !== 'undefined') {
      return matching;
    }
    return null;
  },

  locationChange(
    locations: string[],
    extra: {
      setError: UseFormSetError<FormData>;
      clearErrors: UseFormClearErrors<FormData>;
      getDevice: UseDevice;
      text: Text;
    },
  ): void {
    const { setError, clearErrors, getDevice, text } = extra;

    clearErrors('queryLocation');
    const locationNames = [] as string[];
    const allGroups = [] as string[][];
    const allTypes = [] as Directive[][];
    const allDevices = [];
    set(state => ({ form: { ...state.form, queryLocation: locations } }));

    for (const loc of locations) {
      const device = getDevice(loc);
      if (device !== null) {
        locationNames.push(device.name);
        allDevices.push(device);
        const groups = new Set<string>();
        for (const directive of device.directives) {
          for (const group of directive.groups) {
            groups.add(group);
          }
        }
        allGroups.push(Array.from(groups));
      }
    }

    const intersecting = intersectionWith(...allGroups, isEqual);

    for (const group of intersecting) {
      for (const device of allDevices) {
        for (const directive of device.directives) {
          if (directive.groups.includes(group)) {
            allTypes.push(device.directives);
          }
        }
      }
    }

    let intersectingTypes = intersectionWith(...allTypes, isEqual);
    intersectingTypes = dedupObjectArray<Directive>(intersectingTypes, 'id');
    set({ filtered: { groups: intersecting, types: intersectingTypes } });

    // If there is more than one location selected, but there are no intersecting groups, show an error.
    if (locations.length > 1 && intersecting.length === 0) {
      setError('queryLocation', {
        message: `${locationNames.join(', ')} have no groups in common.`,
      });
    }
    // If there is only one intersecting group, set it as the form value so the user doesn't have to.
    const { selections, form } = get();
    if (form.queryLocation.length > 1 && intersectingTypes.length === 0) {
      const start = plur(text.queryLocation, selections.queryLocation.length);
      const locationsAnd = andJoin(selections.queryLocation.map(s => s.label));
      const types = plur(text.queryType, 2);
      const message = `${start} ${locationsAnd} have no ${types} in common.`;
      setError('queryLocation', {
        // message: `${locationNames.join(', ')} have no query types in common.`,
        message,
      });
    } else if (intersectingTypes.length === 1) {
      set(state => ({ form: { ...state.form, queryType: intersectingTypes[0].id } }));
    }
  },

  response(deviceId: string): QueryResponse | null {
    const { responses } = get();
    for (const [id, response] of Object.entries(responses)) {
      if (id === deviceId) {
        return response;
      }
    }
    return null;
  },

  reset(): void {
    set({
      filtered: { types: [], groups: [] },
      form: { queryLocation: [], queryTarget: '', queryType: '' },
      loading: false,
      responses: {},
      selections: { queryLocation: [], queryType: null },
      status: 'form',
      target: { display: '' },
      resolvedIsOpen: false,
    });
  },
});

export const useFormState = create<FormStateType>(
  withDev<FormStateType>(formState, 'useFormState'),
);

export function useFormSelections<Opt extends SingleOption = SingleOption>(): FormSelections<Opt> {
  return useFormState(s => s.selections as FormSelections<Opt>);
}

export function useView(): FormStatus {
  const { status, form } = useFormState(({ status, form }) => ({ status, form }));
  return useMemo(() => {
    const ready = all(
      status === 'results',
      form.queryLocation.length !== 0,
      form.queryType !== '',
      form.queryTarget !== '',
    );
    return ready ? 'results' : 'form';
  }, [status, form]);
}
