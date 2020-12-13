import { useEffect, useMemo, useState } from 'react';
import { Flex } from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { intersectionWith } from 'lodash';
import * as yup from 'yup';
import {
  If,
  AnimatedForm,
  FormRow,
  QueryVrf,
  FormField,
  HelpModal,
  QueryType,
  QueryTarget,
  SubmitButton,
  QueryLocation,
  ResolvedTarget,
  CommunitySelect,
} from '~/components';
import { useConfig, useGlobalState } from '~/context';
import { useStrf, useGreeting, useDevice } from '~/hooks';
import { isQueryType, isString } from '~/types';

import type { Families, TFormData, TDeviceVrf, TQueryTypes, OnChangeArgs } from '~/types';

export const HyperglassForm = () => {
  const { web, content, messages, queries } = useConfig();

  const { formData, isSubmitting } = useGlobalState();
  const [greetingAck, setGreetingAck] = useGreeting();
  const getDevice = useDevice();

  const noQueryType = useStrf(messages.no_input, { field: web.text.query_type });
  const noQueryLoc = useStrf(messages.no_input, { field: web.text.query_location });
  const noQueryTarget = useStrf(messages.no_input, { field: web.text.query_target });

  const formSchema = yup.object().shape({
    query_location: yup.array().of(yup.string()).required(noQueryLoc),
    query_type: yup.string().required(noQueryType),
    query_vrf: yup.string(),
    query_target: yup.string().required(noQueryTarget),
  });

  const { handleSubmit, register, unregister, setValue, errors } = useForm<TFormData>({
    validationSchema: formSchema,
    defaultValues: { query_vrf: 'default', query_target: '' },
  });

  const [queryLocation, setQueryLocation] = useState<string[]>([]);
  const [queryType, setQueryType] = useState<TQueryTypes>('');
  const [queryVrf, setQueryVrf] = useState<string>('');
  const [queryTarget, setQueryTarget] = useState<string>('');
  const [availVrfs, setAvailVrfs] = useState<TDeviceVrf[]>([]);
  const [fqdnTarget, setFqdnTarget] = useState<string | null>('');
  const [displayTarget, setDisplayTarget] = useState<string>('');
  const [families, setFamilies] = useState<Families>([]);

  function onSubmit(values: TFormData): void {
    if (!greetingAck && web.greeting.required) {
      window.location.reload(false);
      setGreetingAck(false);
    } else {
      formData.set(values);
      isSubmitting.set(true);
    }
  }

  function handleLocChange(locations: string[]): void {
    const allVrfs = [] as TDeviceVrf[][];

    setQueryLocation(locations);

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

    setAvailVrfs(intersecting);

    // If there are no intersecting VRFs, use the default VRF.
    if (intersecting.filter(i => i.id === queryVrf).length === 0 && queryVrf !== 'default') {
      setQueryVrf('default');
    }

    let ipv4 = 0;
    let ipv6 = 0;

    if (intersecting.length !== 0) {
      for (const intersection of intersecting) {
        if (intersection.ipv4) {
          ipv4++;
        }
        if (intersection.ipv6) {
          ipv6++;
        }
      }
    }

    if (ipv4 !== 0 && ipv4 === ipv6) {
      setFamilies([4, 6]);
    } else if (ipv4 > ipv6) {
      setFamilies([4]);
    } else if (ipv4 < ipv6) {
      setFamilies([6]);
    } else {
      setFamilies([]);
    }
  }

  function handleChange(e: OnChangeArgs): void {
    setValue(e.field, e.value);

    if (e.field === 'query_location' && Array.isArray(e.value)) {
      handleLocChange(e.value);
    } else if (e.field === 'query_type' && isQueryType(e.value)) {
      setQueryType(e.value);
    } else if (e.field === 'query_vrf' && isString(e.value)) {
      setQueryVrf(e.value);
    } else if (e.field === 'query_target' && isString(e.value)) {
      setQueryTarget(e.value);
    }
  }

  const vrfContent = useMemo(() => {
    if (Object.keys(content.vrf).includes(queryVrf) && queryType !== '') {
      return content.vrf[queryVrf][queryType];
    }
  }, [queryVrf]);

  const isFqdnQuery = useMemo(() => {
    return ['bgp_route', 'ping', 'traceroute'].includes(queryType);
  }, [queryType]);

  const fqdnQuery = useMemo(() => {
    let result = null;
    if (fqdnTarget && queryVrf === 'default' && fqdnTarget) {
      result = fqdnTarget;
    }
    return result;
  }, [queryVrf, queryType]);

  useEffect(() => {
    register({ name: 'query_location' });
    register({ name: 'query_type' });
    register({ name: 'query_vrf' });
  }, [register]);

  Object.keys(errors).length >= 1 && console.error(errors);

  return (
    <AnimatedForm
      p={0}
      my={4}
      w="100%"
      mx="auto"
      textAlign="left"
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      exit={{ opacity: 0, x: -300 }}
      initial={{ opacity: 0, y: 300 }}
      onSubmit={handleSubmit(onSubmit)}
      maxW={{ base: '100%', lg: '75%' }}>
      <FormRow>
        <FormField
          name="query_location"
          errors={errors.query_location}
          label={web.text.query_location}>
          <QueryLocation onChange={handleChange} label={web.text.query_location} />
        </FormField>
        <FormField
          name="query_type"
          errors={errors.query_type}
          label={web.text.query_type}
          labelAddOn={vrfContent && <HelpModal item={vrfContent} name="query_type" />}>
          <QueryType onChange={handleChange} label={web.text.query_type} />
        </FormField>
      </FormRow>
      <FormRow>
        <If c={availVrfs.length > 1}>
          <FormField label={web.text.query_vrf} name="query_vrf" errors={errors.query_vrf}>
            <QueryVrf label={web.text.query_vrf} vrfs={availVrfs} onChange={handleChange} />
          </FormField>
        </If>
        <FormField
          name="query_target"
          errors={errors.query_target}
          label={web.text.query_target}
          fieldAddOn={
            queryLocation.length !== 0 &&
            fqdnQuery !== null && (
              <ResolvedTarget
                families={families}
                availVrfs={availVrfs}
                fqdnTarget={fqdnQuery}
                setTarget={handleChange}
                queryTarget={queryTarget}
              />
            )
          }>
          <If c={queryType === 'bgp_community' && queries.bgp_community.mode === 'select'}>
            <CommunitySelect
              name="query_target"
              register={register}
              unregister={unregister}
              onChange={handleChange}
              communities={queries.bgp_community.communities}
            />
          </If>
          <If c={!(queryType === 'bgp_community' && queries.bgp_community.mode === 'select')}>
            <QueryTarget
              name="query_target"
              register={register}
              value={queryTarget}
              unregister={unregister}
              setFqdn={setFqdnTarget}
              setTarget={handleChange}
              resolveTarget={isFqdnQuery}
              displayValue={displayTarget}
              setDisplayValue={setDisplayTarget}
              placeholder={web.text.query_target}
            />
          </If>
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
          mr={{ base: 0, lg: 2 }}>
          <SubmitButton isLoading={isSubmitting.value} />
        </Flex>
      </FormRow>
    </AnimatedForm>
  );
};
