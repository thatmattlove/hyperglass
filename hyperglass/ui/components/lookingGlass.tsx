import { useCallback, useEffect, useMemo } from 'react';
import isEqual from 'react-fast-compare';
import { Flex, ScaleFade, SlideFade } from '@chakra-ui/react';
import { FormProvider, useForm } from 'react-hook-form';
import { vestResolver } from '@hookform/resolvers/vest';
import vest, { test, enforce } from 'vest';
import {
  FormRow,
  FormField,
  HelpModal,
  QueryType,
  AnimatedDiv,
  QueryTarget,
  SubmitButton,
  QueryLocation,
} from '~/components';
import { useConfig } from '~/context';
import { useStrf, useGreeting, useDevice, useFormState } from '~/hooks';
import { isString, isQueryField, Directive } from '~/types';

import type { FormData, OnChangeArgs } from '~/types';

/**
 * Don't set the global flag on this.
 * @see https://stackoverflow.com/questions/24084926/javascript-regexp-cant-use-twice
 *
 * TLDR: the test() will pass the first time, but not the second. In React Strict Mode & in a dev
 * environment, this will mean isFqdn will be true the first time, then false the second time,
 * submitting the FQDN to hyperglass the second time.
 */
const fqdnPattern = new RegExp(
  /^(?!:\/\/)([a-zA-Z0-9-]+\.)?[a-zA-Z0-9-][a-zA-Z0-9-]+\.[a-zA-Z-]{2,6}?$/im,
);

export const LookingGlass = (): JSX.Element => {
  const { web, messages } = useConfig();

  const greetingReady = useGreeting(s => s.greetingReady);

  const getDevice = useDevice();
  const strF = useStrf();
  const setLoading = useFormState(s => s.setLoading);
  const setStatus = useFormState(s => s.setStatus);
  const locationChange = useFormState(s => s.locationChange);
  const setTarget = useFormState(s => s.setTarget);
  const setFormValue = useFormState(s => s.setFormValue);
  const { form, filtered } = useFormState(
    useCallback(({ form, filtered }) => ({ form, filtered }), []),
    isEqual,
  );

  const getDirective = useFormState(useCallback(s => s.getDirective, []));
  const resolvedOpen = useFormState(useCallback(s => s.resolvedOpen, []));
  const resetForm = useFormState(useCallback(s => s.reset, []));

  const noQueryType = strF(messages.noInput, { field: web.text.queryType });
  const noQueryLoc = strF(messages.noInput, { field: web.text.queryLocation });
  const noQueryTarget = strF(messages.noInput, { field: web.text.queryTarget });

  const queryTypes = useMemo(() => filtered.types.map(t => t.id), [filtered.types]);

  const formSchema = vest.create((data: FormData = {} as FormData) => {
    test('queryLocation', noQueryLoc, () => {
      enforce(data.queryLocation).isArrayOf(enforce.isString()).isNotEmpty();
    });
    test('queryTarget', noQueryTarget, () => {
      enforce(data.queryTarget).longerThan(1);
    });
    test('queryType', noQueryType, () => {
      enforce(data.queryType).inside(queryTypes);
    });
  });

  const formInstance = useForm<FormData>({
    resolver: vestResolver(formSchema),
    defaultValues: {
      queryTarget: '',
      queryLocation: [],
      queryType: '',
    },
  });

  const { handleSubmit, register, setValue, setError, clearErrors } = formInstance;

  // const isFqdnQuery = useIsFqdn(form.queryTarget, form.queryType);
  const isFqdnQuery = useCallback(
    (target: string, fieldType: Directive['fieldType'] | null): boolean =>
      fieldType === 'text' && fqdnPattern.test(target),
    [],
  );

  const directive = useMemo<Directive | null>(
    () => getDirective(),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [form.queryType, form.queryLocation, getDirective],
  );

  function submitHandler(): void {
    console.table({
      'Query Location': form.queryLocation.toString(),
      'Query Type': form.queryType,
      'Query Target': form.queryTarget,
      'Selected Directive': directive?.name ?? null,
    });
    // Before submitting a query, make sure the greeting is acknowledged if required. This should
    // be handled before loading the app, but people be sneaky.

    if (!greetingReady) {
      resetForm();
      location.reload();
      return;
    }

    // Determine if queryTarget is an FQDN.
    const isFqdn = isFqdnQuery(form.queryTarget, directive?.fieldType ?? null);

    if (greetingReady && !isFqdn) {
      return setStatus('results');
    }

    if (greetingReady && isFqdn) {
      setLoading(true);
      return resolvedOpen();
    } else {
      console.group('%cSomething went wrong', 'color:red;');
      console.table({
        'Greeting Required': web.greeting.required,
        'Greeting Ready': greetingReady,
        'Query Target': form.queryTarget,
        'Query Type': form.queryType,
        'Is FQDN': isFqdn,
      });
      console.groupEnd();
    }
  }

  const handleLocChange = (locations: string[]) =>
    locationChange(locations, { setError, clearErrors, getDevice, text: web.text });

  function handleChange(e: OnChangeArgs): void {
    // Signal the field & value to react-hook-form.
    if (isQueryField(e.field)) {
      setValue(e.field, e.value);
    } else {
      throw new Error(`Field '${e.field}' is not a valid form field.`);
    }

    if (e.field === 'queryLocation' && Array.isArray(e.value)) {
      handleLocChange(e.value);
    } else if (e.field === 'queryType' && isString(e.value)) {
      setValue('queryType', e.value);
      setFormValue('queryType', e.value);
      if (form.queryTarget !== '') {
        // Reset queryTarget as well, so that, for example, selecting BGP Community, and selecting
        // a community, then changing the queryType to BGP Route doesn't preserve the selected
        // community as the queryTarget.
        setFormValue('queryTarget', '');
        setTarget({ display: '' });
      }
    } else if (e.field === 'queryTarget' && isString(e.value)) {
      setFormValue('queryTarget', e.value);
    }
  }

  useEffect(() => {
    register('queryLocation', { required: true });
    register('queryType', { required: true });
  }, [register]);

  return (
    <FormProvider {...formInstance}>
      <AnimatedDiv
        p={0}
        my={4}
        w="100%"
        as="form"
        mx="auto"
        textAlign="left"
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        exit={{ opacity: 0, x: -300 }}
        initial={{ opacity: 0, y: 300 }}
        maxW={{ base: '100%', lg: '75%' }}
        onSubmit={handleSubmit(submitHandler)}
      >
        <FormRow>
          <FormField name="queryLocation" label={web.text.queryLocation}>
            <QueryLocation onChange={handleChange} label={web.text.queryLocation} />
          </FormField>
        </FormRow>
        <FormRow>
          <SlideFade offsetY={100} in={filtered.types.length > 0} unmountOnExit>
            <FormField
              name="queryType"
              label={web.text.queryType}
              labelAddOn={
                <HelpModal
                  visible={directive?.info !== null}
                  item={directive?.info ?? null}
                  name="queryType"
                />
              }
            >
              <QueryType onChange={handleChange} label={web.text.queryType} />
            </FormField>
          </SlideFade>
          <SlideFade offsetX={100} in={directive !== null} unmountOnExit>
            {directive !== null && (
              <FormField name="queryTarget" label={web.text.queryTarget}>
                <QueryTarget
                  name="queryTarget"
                  register={register}
                  onChange={handleChange}
                  placeholder={directive.description}
                />
              </FormField>
            )}
          </SlideFade>
        </FormRow>
        <FormRow mt={0} justifyContent="flex-end">
          <Flex
            my={2}
            w="100%"
            ml="auto"
            maxW="100%"
            flex="0 0 0"
            flexDir="column"
            mr={{ base: 0, lg: 2 }}
          >
            <ScaleFade initialScale={0.5} in={form.queryTarget !== ''}>
              <SubmitButton />
            </ScaleFade>
          </Flex>
        </FormRow>
      </AnimatedDiv>
    </FormProvider>
  );
};
