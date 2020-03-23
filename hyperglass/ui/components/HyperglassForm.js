import React, { useState, useEffect } from "react";
import { Box, Flex } from "@chakra-ui/core";
import { useForm } from "react-hook-form";
import lodash from "lodash";
import * as yup from "yup";
import format from "string-format";
import FormField from "~/components/FormField";
import HelpModal from "~/components/HelpModal";
import QueryLocation from "~/components/QueryLocation";
import QueryType from "~/components/QueryType";
import QueryTarget from "~/components/QueryTarget";
import QueryVrf from "~/components/QueryVrf";
import ResolvedTarget from "~/components/ResolvedTarget";
import SubmitButton from "~/components/SubmitButton";
import useConfig from "~/components/HyperglassProvider";

format.extend(String.prototype, {});

const formSchema = config =>
    yup.object().shape({
        query_location: yup
            .array()
            .of(yup.string())
            .required(config.messages.no_input.format({ field: config.web.text.query_location })),
        query_type: yup
            .string()
            .required(config.messages.no_input.format({ field: config.web.text.query_type })),
        query_vrf: yup.string(),
        query_target: yup
            .string()
            .required(config.messages.no_input.format({ field: config.web.text.query_target }))
    });

const FormRow = ({ children, ...props }) => (
    <Flex
        flexDirection="row"
        flexWrap="wrap"
        w="100%"
        justifyContent={["center", "center", "space-between", "space-between"]}
        {...props}
    >
        {children}
    </Flex>
);

const HyperglassForm = React.forwardRef(
    ({ isSubmitting, setSubmitting, setFormData, ...props }, ref) => {
        const config = useConfig();
        const { handleSubmit, register, setValue, errors } = useForm({
            validationSchema: formSchema(config)
        });

        const [queryLocation, setQueryLocation] = useState([]);
        const [queryType, setQueryType] = useState("");
        const [queryVrf, setQueryVrf] = useState("");
        const [queryTarget, setQueryTarget] = useState("");
        const [availVrfs, setAvailVrfs] = useState([]);
        const [fqdnTarget, setFqdnTarget] = useState("");
        const [displayTarget, setDisplayTarget] = useState("");
        const onSubmit = values => {
            if (values.query_vrf === undefined) {
                values.query_vrf = "default";
            }
            setFormData(values);
            setSubmitting(true);
        };

        const handleLocChange = locObj => {
            setQueryLocation(locObj.value);
            const allVrfs = [];
            locObj.value.map(loc => {
                const locVrfs = [];
                config.devices[loc].vrfs.map(vrf => {
                    locVrfs.push({ label: vrf.display_name, value: vrf.id });
                });
                allVrfs.push(locVrfs);
            });
            const intersecting = lodash.intersectionWith(...allVrfs, lodash.isEqual);
            setAvailVrfs(intersecting);
            !intersecting.includes(queryVrf) && setQueryVrf("");
        };

        const handleChange = e => {
            setValue(e.field, e.value);
            e.field === "query_location"
                ? handleLocChange(e)
                : e.field === "query_type"
                ? setQueryType(e.value)
                : e.field === "query_vrf"
                ? setQueryVrf(e.value)
                : e.field === "query_target"
                ? setQueryTarget(e.value)
                : null;
        };

        const vrfContent = config.content.vrf[queryVrf]?.[queryType];
        const validFqdnQueryType =
            ["ping", "traceroute", "bgp_route"].includes(queryType) &&
            fqdnTarget &&
            queryVrf === "default"
                ? fqdnTarget
                : null;

        useEffect(() => {
            register({ name: "query_location" });
            register({ name: "query_target" });
            register({ name: "query_type" });
            register({ name: "query_vrf" });
        });
        return (
            <Box
                maxW={["100%", "100%", "75%", "75%"]}
                w="100%"
                p={0}
                mx="auto"
                my={4}
                textAlign="left"
                ref={ref}
                {...props}
            >
                <form onSubmit={handleSubmit(onSubmit)}>
                    <FormRow>
                        <FormField
                            label={config.web.text.query_location}
                            name="query_location"
                            error={errors.query_location}
                        >
                            <QueryLocation onChange={handleChange} locations={config.networks} />
                        </FormField>
                        <FormField
                            label={config.web.text.query_type}
                            name="query_type"
                            error={errors.query_type}
                            labelAddOn={
                                vrfContent && <HelpModal item={vrfContent} name="query_type" />
                            }
                        >
                            <QueryType onChange={handleChange} queryTypes={config.queries.list} />
                        </FormField>
                    </FormRow>
                    <FormRow>
                        {availVrfs.length > 1 && (
                            <FormField
                                label={config.web.text.query_vrf}
                                name="query_vrf"
                                error={errors.query_vrf}
                            >
                                <QueryVrf
                                    placeholder={config.web.text.query_vrf}
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
                                validFqdnQueryType && (
                                    <ResolvedTarget
                                        queryTarget={queryTarget}
                                        fqdnTarget={validFqdnQueryType}
                                        setTarget={handleChange}
                                    />
                                )
                            }
                        >
                            <QueryTarget
                                name="query_target"
                                placeholder={config.web.text.query_target}
                                register={register}
                                resolveTarget={["ping", "traceroute", "bgp_route"].includes(
                                    queryType
                                )}
                                value={queryTarget}
                                setFqdn={setFqdnTarget}
                                setTarget={handleChange}
                                displayValue={displayTarget}
                                setDisplayValue={setDisplayTarget}
                            />
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
                            flex="0 0 0"
                        >
                            <SubmitButton isLoading={isSubmitting} />
                        </Flex>
                    </FormRow>
                </form>
            </Box>
        );
    }
);

HyperglassForm.displayName = "HyperglassForm";
export default HyperglassForm;
