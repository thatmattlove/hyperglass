import { useMemo } from 'react';
import create from 'zustand';
import intersectionWith from 'lodash/intersectionWith';
import plur from 'plur';
import isEqual from 'react-fast-compare';
import { all, andJoin, dedupObjectArray, withDev } from '~/util';

import type { StateCreator } from 'zustand';
import type { UseFormSetError, UseFormClearErrors } from 'react-hook-form';
import type { SingleValue, MultiValue } from 'react-select';
import type { SingleOption, Directive, FormData, Text, Device } from '~/types';
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
    set(state => ({ form: { ...state.form, queryLocation: locations } }));

    // Get device configuration objects for each selected location ID.
    const allDevices = locations
      .map(getDevice)
      .filter((device): device is Device => device !== null);

    // Determine all unique group names.
    const allGroups = allDevices.map(dev =>
      Array.from(new Set(dev.directives.map(dir => dir.groups).flat())),
    );

    // Get group names that are common between all selected locations.
    const intersecting = intersectionWith(...allGroups, isEqual);

    // Get all directives of all selected devices.
    const allDirectives = locations
      .map(getDevice)
      .filter((device): device is Device => device !== null)
      .map(device => device.directives);

    // Get directive objects that are common between selected locations.
    const intersectingDirectives = intersectionWith(...allDirectives, isEqual);

    // Deduplicate all intersecting directives by ID.
    const directives = dedupObjectArray(intersectingDirectives, 'id');

    set({ filtered: { groups: intersecting, types: directives } });

    // If there is only one intersecting group, set it as the form value so the user doesn't have to.
    const { selections, form } = get();
    if (
      (form.queryLocation.length > 1 || locations.length > 1) &&
      intersectingDirectives.length === 0
    ) {
      const start = plur(text.queryLocation, selections.queryLocation.length);
      const locationsAnd = andJoin(selections.queryLocation.map(s => s.label));
      const types = plur(text.queryType, 2);
      const message = `${start} ${locationsAnd} have no ${types} in common.`;
      setError('queryLocation', { message });
    } else if (intersectingDirectives.length === 1) {
      set(state => ({ form: { ...state.form, queryType: intersectingDirectives[0].id } }));
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

export function useFormInteractive(): boolean {
  const { status, selections } = useFormState(({ status, selections }) => ({ status, selections }));
  return status === 'results' || selections.queryLocation.length > 0;
}
