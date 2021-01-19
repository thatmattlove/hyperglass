import { useCallback, useEffect, useMemo } from 'react';
import { Flex } from '@chakra-ui/react';
import { FormProvider, useForm } from 'react-hook-form';
import { intersectionWith } from 'lodash';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';
import {
  If,
  FormRow,
  QueryVrf,
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
import { isQueryType, isQueryContent, isString } from '~/types';

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
  const { web, content, messages } = useConfig();

  const { ack, greetingReady } = useGreeting();
  const getDevice = useDevice();

  const noQueryType = useStrf(messages.no_input, { field: web.text.query_type });
  const noQueryLoc = useStrf(messages.no_input, { field: web.text.query_location });
  const noQueryTarget = useStrf(messages.no_input, { field: web.text.query_target });

  const formSchema = yup.object().shape({
    query_location: yup.array().of(yup.string()).required(noQueryLoc),
    query_target: yup.string().required(noQueryTarget),
    query_type: yup.string().required(noQueryType),
    query_vrf: yup.string(),
  });

  const formInstance = useForm<TFormData>({
    resolver: yupResolver(formSchema),
    defaultValues: { query_vrf: 'default', query_target: '', query_location: [], query_type: '' },
  });

  const { handleSubmit, register, setValue } = formInstance;

  const {
    queryVrf,
    families,
    queryType,
    availVrfs,
    btnLoading,
    queryTarget,
    isSubmitting,
    queryLocation,
    displayTarget,
  } = useLGState();

  const { resolvedOpen, resetForm } = useLGMethods();

  const isFqdnQuery = useIsFqdn(queryTarget.value, queryType.value);

  function submitHandler() {
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
    const allVrfs = [] as TDeviceVrf[][];

    queryLocation.set(locations);

    // Create an array of each device's VRFs.
    for (const loc of locations) {
      const device = getDevice(loc);
      allVrfs.push(device.vrfs);
    }

    // Use _.intersectionWith to create an array of VRFs common to all selected locations.
    const intersecting = intersectionWith(
      ...allVrfs,
      (a: TDeviceVrf, b: TDeviceVrf) => a.id === b.id,
    );

    availVrfs.set(intersecting);

    // If there are no intersecting VRFs, use the default VRF.
    if (
      intersecting.filter(i => i.id === queryVrf.value).length === 0 &&
      queryVrf.value !== 'default'
    ) {
      queryVrf.set('default');
    }

    // Determine which address families are available in the intersecting VRFs.
    let ipv4 = 0;
    let ipv6 = 0;

    for (const intersection of intersecting) {
      if (intersection.ipv4) {
        // If IPv4 is enabled in this VRF, count it.
        ipv4++;
      }
      if (intersection.ipv6) {
        // If IPv6 is enabled in this VRF, count it.
        ipv6++;
      }
    }

    if (ipv4 !== 0 && ipv4 === ipv6) {
      /**
       * If ipv4 & ipv6 are equal, this means every VRF has both IPv4 & IPv6 enabled. In that
       * case, signal that both A & AAAA records should be queried if the query is an FQDN.
       */
      families.set([4, 6]);
    } else if (ipv4 > ipv6) {
      /**
       * If ipv4 is greater than ipv6, this means that IPv6 is not enabled on all VRFs, i.e. there
       * are some VRFs with IPv4 enabled but IPv6 disabled. In that case, only query A records.
       */
      families.set([4]);
    } else if (ipv4 < ipv6) {
      /**
       * If ipv6 is greater than ipv4, this means that IPv4 is not enabled on all VRFs, i.e. there
       * are some VRFs with IPv6 enabled but IPv4 disabled. In that case, only query AAAA records.
       */
      families.set([6]);
    } else {
      /**
       * If both ipv4 and ipv6 are 0, then both ipv4 and ipv6 are disabled, and why does that VRF
       * even exist?
       */
      families.set([]);
    }
  }

  function handleChange(e: OnChangeArgs): void {
    // Signal the field & value to react-hook-form.
    setValue(e.field, e.value);

    if (e.field === 'query_location' && Array.isArray(e.value)) {
      handleLocChange(e.value);
    } else if (e.field === 'query_type' && isQueryType(e.value)) {
      queryType.set(e.value);
      if (queryTarget.value !== '') {
        /**
         * Reset queryTarget as well, so that, for example, selecting BGP Community, and selecting
         * a community, then changing the queryType to BGP Route doesn't preserve the selected
         * community as the queryTarget.
         */
        queryTarget.set('');
        displayTarget.set('');
      }
    } else if (e.field === 'query_vrf' && isString(e.value)) {
      queryVrf.set(e.value);
    } else if (e.field === 'query_target' && isString(e.value)) {
      queryTarget.set(e.value);
    }
  }

  /**
   * Select the correct help content based on the selected VRF & Query Type. Also remove the icon
   * if no locations are set.
   */
  const vrfContent = useMemo(() => {
    if (queryLocation.value.length === 0) {
      return null;
    }
    if (Object.keys(content.vrf).includes(queryVrf.value) && queryType.value !== '') {
      return content.vrf[queryVrf.value][queryType.value];
    } else {
      return null;
    }
  }, [queryVrf.value, queryLocation.value, queryType.value]);

  useEffect(() => {
    register({ name: 'query_location', required: true });
    register({ name: 'query_target', required: true });
    register({ name: 'query_type', required: true });
    register({ name: 'query_vrf' });
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
          <FormField
            name="query_type"
            label={web.text.query_type}
            labelAddOn={
              <HelpModal visible={isQueryContent(vrfContent)} item={vrfContent} name="query_type" />
            }
          >
            <QueryType onChange={handleChange} label={web.text.query_type} />
          </FormField>
        </FormRow>
        <FormRow>
          <If c={availVrfs.length > 1}>
            <FormField label={web.text.query_vrf} name="query_vrf">
              <QueryVrf label={web.text.query_vrf} vrfs={availVrfs.value} onChange={handleChange} />
            </FormField>
          </If>
          <FormField name="query_target" label={web.text.query_target}>
            <QueryTarget
              name="query_target"
              register={register}
              onChange={handleChange}
              placeholder={web.text.query_target}
            />
          </FormField>
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
            <SubmitButton handleChange={handleChange} />
          </Flex>
        </FormRow>
      </AnimatedDiv>
    </FormProvider>
  );
};
