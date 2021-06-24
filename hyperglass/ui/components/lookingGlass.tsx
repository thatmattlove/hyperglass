import { useCallback, useEffect, useMemo } from 'react';
import { Flex, ScaleFade, SlideFade } from '@chakra-ui/react';
import { FormProvider, useForm } from 'react-hook-form';
import { intersectionWith } from 'lodash';
import isEqual from 'react-fast-compare';
import { vestResolver } from '@hookform/resolvers/vest';
import vest, { test, enforce } from 'vest';
import {
  If,
  FormRow,
  QueryGroup,
  FormField,
  HelpModal,
  QueryType,
  AnimatedDiv,
  QueryTarget,
  SubmitButton,
  QueryLocation,
} from '~/components';
import { useConfig } from '~/context';
import { useStrf, useGreeting, useDevice, useLGState, useLGMethods } from '~/hooks';
import { isQueryType, isQueryContent, isString, isQueryField, TDirective } from '~/types';

import type { TFormData, TDeviceVrf, OnChangeArgs } from '~/types';

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

function useIsFqdn(target: string, _type: string) {
  return useCallback(
    (): boolean => ['bgp_route', 'ping', 'traceroute'].includes(_type) && fqdnPattern.test(target),
    [target, _type],
  );
}

export const LookingGlass: React.FC = () => {
  const { web, messages } = useConfig();

  const { ack, greetingReady } = useGreeting();
  const getDevice = useDevice();

  const noQueryType = useStrf(messages.no_input, { field: web.text.query_type });
  const noQueryLoc = useStrf(messages.no_input, { field: web.text.query_location });
  const noQueryTarget = useStrf(messages.no_input, { field: web.text.query_target });

  const {
    availableGroups,
    queryVrf,
    queryType,
    directive,
    availableTypes,
    btnLoading,
    queryGroup,
    queryTarget,
    isSubmitting,
    queryLocation,
    displayTarget,
    selections,
  } = useLGState();

  const queryTypes = useMemo(() => availableTypes.map(t => t.id.value), [availableTypes.length]);

  const formSchema = vest.create((data: TFormData = {} as TFormData) => {
    test('query_location', noQueryLoc, () => {
      enforce(data.query_location).isArrayOf(enforce.isString()).isNotEmpty();
    });
    test('query_target', noQueryTarget, () => {
      enforce(data.query_target).longerThan(1);
    });
    test('query_type', noQueryType, () => {
      enforce(data.query_type).inside(queryTypes);
    });
    test('query_group', 'Query Group is empty', () => {
      enforce(data.query_group).isString();
    });
  });

  const formInstance = useForm<TFormData>({
    resolver: vestResolver(formSchema),
    defaultValues: {
      // query_vrf: 'default',
      query_target: '',
      query_location: [],
      query_type: '',
      query_group: '',
    },
  });

  const { handleSubmit, register, setValue, setError, clearErrors } = formInstance;

  const { resolvedOpen, resetForm, getDirective } = useLGMethods();

  const isFqdnQuery = useIsFqdn(queryTarget.value, queryType.value);

  const selectedDirective = useMemo(() => {
    if (queryType.value === '') {
      return null;
    }
    for (const loc of queryLocation) {
      const device = getDevice(loc.value);
      for (const directive of device.directives) {
        if (directive.name === queryType.value) {
          return directive;
        }
      }
    }
    return null;
  }, [queryType.value]);

  function submitHandler() {
    console.table({
      'Query Location': queryLocation.value,
      'Query Type': queryType.value,
      'Query Group': queryGroup.value,
      'Query Target': queryTarget.value,
      'Selected Directive': selectedDirective?.name ?? null,
    });
    /**
     * Before submitting a query, make sure the greeting is acknowledged if required. This should
     * be handled before loading the app, but people be sneaky.
     */
    if (!greetingReady()) {
      resetForm();
      location.reload();
    }

    // Determine if queryTarget is an FQDN.
    const isFqdn = isFqdnQuery();

    if (greetingReady() && !isFqdn) {
      return isSubmitting.set(true);
    }

    if (greetingReady() && isFqdn) {
      btnLoading.set(true);
      return resolvedOpen();
    } else {
      console.group('%cSomething went wrong', 'color:red;');
      console.table({
        'Greeting Required': web.greeting.required,
        'Greeting Ready': greetingReady(),
        'Greeting Acknowledged': ack.value,
        'Query Target': queryTarget.value,
        'Query Type': queryType.value,
        'Is FQDN': isFqdn,
      });
      console.groupEnd();
    }
  }

  function handleLocChange(locations: string[]): void {
    clearErrors('query_location');
    const allVrfs = [] as TDeviceVrf[][];
    const locationNames = [] as string[];
    const allGroups = [] as string[][];
    const allTypes = [] as TDirective[][];
    const allDevices = [];

    queryLocation.set(locations);

    // Create an array of each device's VRFs.
    for (const loc of locations) {
      const device = getDevice(loc);
      locationNames.push(device.name);
      allVrfs.push(device.vrfs);
      allDevices.push(device);
      const groups = new Set<string>();
      for (const directive of device.directives) {
        for (const group of directive.groups) {
          groups.add(group);
        }
      }
      allGroups.push(Array.from(groups));
    }

    const intersecting = intersectionWith(...allGroups, isEqual);

    if (!intersecting.includes(queryGroup.value)) {
      queryGroup.set('');
      queryType.set('');
      directive.set(null);
      selections.merge({ queryGroup: null, queryType: null });
    }

    for (const group of intersecting) {
      for (const device of allDevices) {
        for (const directive of device.directives) {
          if (directive.groups.includes(group)) {
            // allTypes.add(directive.name);
            allTypes.push(device.directives);
            // allTypes.push(device.directives.map(d => d.name));
          }
        }
      }
    }

    const intersectingTypes = intersectionWith(...allTypes, isEqual);

    availableGroups.set(intersecting);
    availableTypes.set(intersectingTypes);

    // If there is more than one location selected, but there are no intersecting VRFs, show an error.
    if (locations.length > 1 && intersecting.length === 0) {
      setError('query_location', {
        // message: `${locationNames.join(', ')} have no VRFs in common.`,
        message: `${locationNames.join(', ')} have no groups in common.`,
      });
    }
    // If there is only one intersecting VRF, set it as the form value so the user doesn't have to.
    else if (intersecting.length === 1) {
      // queryVrf.set(intersecting[0]._id);
      queryGroup.set(intersecting[0]);
    }
    if (availableGroups.length > 1 && intersectingTypes.length === 0) {
      setError('query_location', {
        message: `${locationNames.join(', ')} have no query types in common.`,
      });
    } else if (intersectingTypes.length === 1) {
      queryType.set(intersectingTypes[0].id);
    }
  }

  function handleGroupChange(group: string): void {
    queryGroup.set(group);
    const availTypes = new Set<string>();
    for (const loc of queryLocation) {
      const device = getDevice(loc.value);
      for (const directive of device.directives) {
        if (directive.groups.includes(group)) {
          availTypes.add(directive.name);
        }
      }
    }
    availableTypes.set(Array.from(availTypes));
    if (availableTypes.length === 1) {
      queryType.set(availableTypes[0].value);
    }
  }

  function handleChange(e: OnChangeArgs): void {
    // Signal the field & value to react-hook-form.
    if (isQueryField(e.field)) {
      setValue(e.field, e.value);
    } else {
      throw new Error(`Field '${e.field}' is not a valid form field.`);
    }

    if (e.field === 'query_location' && Array.isArray(e.value)) {
      handleLocChange(e.value);
    } else if (e.field === 'query_type' && isString(e.value)) {
      queryType.set(e.value);
      if (queryTarget.value !== '') {
        // Reset queryTarget as well, so that, for example, selecting BGP Community, and selecting
        // a community, then changing the queryType to BGP Route doesn't preserve the selected
        // community as the queryTarget.
        queryTarget.set('');
        displayTarget.set('');
      }
    } else if (e.field === 'query_vrf' && isString(e.value)) {
      queryVrf.set(e.value);
    } else if (e.field === 'query_target' && isString(e.value)) {
      queryTarget.set(e.value);
    } else if (e.field === 'query_group' && isString(e.value)) {
      // queryGroup.set(e.value);
      handleGroupChange(e.value);
    }
  }

  useEffect(() => {
    register('query_location', { required: true });
    register('query_target', { required: true });
    register('query_type', { required: true });
    register('query_group');
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
          <FormField name="query_location" label={web.text.query_location}>
            <QueryLocation onChange={handleChange} label={web.text.query_location} />
          </FormField>
          <If c={availableGroups.length > 1}>
            <FormField label={web.text.query_vrf} name="query_group">
              <QueryGroup
                label={web.text.query_vrf}
                groups={availableGroups.value}
                onChange={handleChange}
              />
            </FormField>
          </If>
        </FormRow>
        <FormRow>
          <SlideFade offsetX={-100} in={availableTypes.length > 1} unmountOnExit>
            <FormField
              name="query_type"
              label={web.text.query_type}
              labelAddOn={
                <HelpModal
                  visible={selectedDirective?.info !== null}
                  item={selectedDirective?.info ?? null}
                  name="query_type"
                />
              }
            >
              <QueryType onChange={handleChange} label={web.text.query_type} />
            </FormField>
          </SlideFade>
          <SlideFade offsetX={100} in={selectedDirective !== null} unmountOnExit>
            {selectedDirective !== null && (
              <FormField name="query_target" label={web.text.query_target}>
                <QueryTarget
                  name="query_target"
                  register={register}
                  onChange={handleChange}
                  placeholder={selectedDirective.description}
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
            <ScaleFade initialScale={0.5} in={queryTarget.value !== ''}>
              <SubmitButton handleChange={handleChange} />
            </ScaleFade>
          </Flex>
        </FormRow>
      </AnimatedDiv>
    </FormProvider>
  );
};
