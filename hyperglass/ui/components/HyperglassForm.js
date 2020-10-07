import * as React from 'react';
import { forwardRef, useState, useEffect } from 'react';
import { Box, Flex } from '@chakra-ui/core';
import { useForm } from 'react-hook-form';
import { intersectionWith, isEqual } from 'lodash';
import * as yup from 'yup';
import format from 'string-format';
import {
  FormField,
  HelpModal,
  QueryLocation,
  QueryType,
  QueryTarget,
  CommunitySelect,
  QueryVrf,
  ResolvedTarget,
  SubmitButton,
} from 'app/components';
import { useConfig } from 'app/context';

format.extend(String.prototype, {});

const formSchema = config =>
  yup.object().shape({
    query_location: yup
      .array()
      .of(yup.string())
      .required(
        config.messages.no_input.format({
          field: config.web.text.query_location,
        }),
      ),
    query_type: yup
      .string()
      .required(config.messages.no_input.format({ field: config.web.text.query_type })),
    query_vrf: yup.string(),
    query_target: yup
      .string()
      .required(config.messages.no_input.format({ field: config.web.text.query_target })),
  });

const FormRow = ({ children, ...props }) => (
  <Flex
    flexDirection="row"
    flexWrap="wrap"
    w="100%"
    justifyContent={['center', 'center', 'space-between', 'space-between']}
    {...props}>
    {children}
  </Flex>
);

export const HyperglassForm = forwardRef(
  ({ isSubmitting, setSubmitting, setFormData, greetingAck, setGreetingAck, ...props }, ref) => {
    const config = useConfig();
    const { handleSubmit, register, unregister, setValue, errors } = useForm({
      validationSchema: formSchema(config),
      defaultValues: { query_vrf: 'default', query_target: '' },
    });

    const [queryLocation, setQueryLocation] = useState([]);
    const [queryType, setQueryType] = useState('');
    const [queryVrf, setQueryVrf] = useState('');
    const [queryTarget, setQueryTarget] = useState('');
    const [availVrfs, setAvailVrfs] = useState([]);
    const [fqdnTarget, setFqdnTarget] = useState('');
    const [displayTarget, setDisplayTarget] = useState('');
    const [families, setFamilies] = useState([]);
    const onSubmit = values => {
      if (!greetingAck && config.web.greeting.required) {
        window.location.reload(false);
        setGreetingAck(false);
      } else {
        setFormData(values);
        setSubmitting(true);
      }
    };

    const handleLocChange = locObj => {
      setQueryLocation(locObj.value);
      const allVrfs = [];
      const deviceVrfs = [];
      locObj.value.map(loc => {
        const locVrfs = [];
        config.devices[loc].vrfs.map(vrf => {
          locVrfs.push({
            label: vrf.display_name,
            value: vrf.id,
          });
          deviceVrfs.push([{ id: vrf.id, ipv4: vrf.ipv4, ipv6: vrf.ipv6 }]);
        });
        allVrfs.push(locVrfs);
      });

      const intersecting = intersectionWith(...allVrfs, isEqual);
      setAvailVrfs(intersecting);
      !intersecting.includes(queryVrf) && queryVrf !== 'default' && setQueryVrf('default');

      let ipv4 = 0;
      let ipv6 = 0;
      deviceVrfs.length !== 0 &&
        intersecting.length !== 0 &&
        deviceVrfs
          .filter(v => intersecting.every(i => i.id === v.id))
          .reduce((a, b) => a.concat(b))
          .filter(v => v.id === 'default')
          .map(v => {
            v.ipv4 === true && ipv4++;
            v.ipv6 === true && ipv6++;
          });
      if (ipv4 !== 0 && ipv4 === ipv6) {
        setFamilies([4, 6]);
      } else if (ipv4 > ipv6) {
        setFamilies([4]);
      } else if (ipv4 < ipv6) {
        setFamilies([6]);
      } else {
        setFamilies([]);
      }
    };

    const handleChange = e => {
      setValue(e.field, e.value);
      e.field === 'query_location'
        ? handleLocChange(e)
        : e.field === 'query_type'
        ? setQueryType(e.value)
        : e.field === 'query_vrf'
        ? setQueryVrf(e.value)
        : e.field === 'query_target'
        ? setQueryTarget(e.value)
        : null;
    };

    const vrfContent = config.content.vrf[queryVrf]?.[queryType];

    const validFqdnQueryType =
      ['ping', 'traceroute', 'bgp_route'].includes(queryType) &&
      fqdnTarget &&
      queryVrf === 'default'
        ? fqdnTarget
        : null;

    useEffect(() => {
      register({ name: 'query_location' });
      register({ name: 'query_type' });
      register({ name: 'query_vrf' });
    }, [register]);
    Object.keys(errors).length >= 1 && console.error(errors);
    return (
      <Box
        as="form"
        onSubmit={handleSubmit(onSubmit)}
        maxW={['100%', '100%', '75%', '75%']}
        w="100%"
        p={0}
        mx="auto"
        my={4}
        textAlign="left"
        ref={ref}
        {...props}>
        <FormRow>
          <FormField
            label={config.web.text.query_location}
            name="query_location"
            error={errors.query_location}>
            <QueryLocation
              onChange={handleChange}
              locations={config.networks}
              label={config.web.text.query_location}
            />
          </FormField>
          <FormField
            label={config.web.text.query_type}
            name="query_type"
            error={errors.query_type}
            labelAddOn={vrfContent && <HelpModal item={vrfContent} name="query_type" />}>
            <QueryType
              onChange={handleChange}
              queryTypes={config.queries.list}
              label={config.web.text.query_type}
            />
          </FormField>
        </FormRow>
        <FormRow>
          {availVrfs.length > 1 && (
            <FormField label={config.web.text.query_vrf} name="query_vrf" error={errors.query_vrf}>
              <QueryVrf
                label={config.web.text.query_vrf}
                vrfs={availVrfs}
                onChange={handleChange}
              />
            </FormField>
          )}
          <FormField
            label={config.web.text.query_target}
            name="query_target"
            error={errors.query_target}
            fieldAddOn={
              queryLocation.length !== 0 &&
              validFqdnQueryType && (
                <ResolvedTarget
                  queryTarget={queryTarget}
                  fqdnTarget={validFqdnQueryType}
                  setTarget={handleChange}
                  families={families}
                  availVrfs={availVrfs}
                />
              )
            }>
            {queryType === 'bgp_community' && config.queries.bgp_community.mode === 'select' ? (
              <CommunitySelect
                label={config.queries.bgp_community.display_name}
                name="query_target"
                register={register}
                unregister={unregister}
                onChange={handleChange}
                communities={config.queries.bgp_community.communities}
              />
            ) : (
              <QueryTarget
                name="query_target"
                placeholder={config.web.text.query_target}
                register={register}
                unregister={unregister}
                resolveTarget={['ping', 'traceroute', 'bgp_route'].includes(queryType)}
                value={queryTarget}
                setFqdn={setFqdnTarget}
                setTarget={handleChange}
                displayValue={displayTarget}
                setDisplayValue={setDisplayTarget}
              />
            )}
          </FormField>
        </FormRow>
        <FormRow mt={0} justifyContent="flex-end">
          <Flex
            w="100%"
            maxW="100%"
            ml="auto"
            my={2}
            mr={[0, 0, 2, 2]}
            flexDirection="column"
            flex="0 0 0">
            <SubmitButton isLoading={isSubmitting} />
          </Flex>
        </FormRow>
      </Box>
    );
  },
);
