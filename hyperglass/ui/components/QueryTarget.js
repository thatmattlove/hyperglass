import React, { useState } from "react";
import styled from "@emotion/styled";
import { Input, useColorMode } from "@chakra-ui/core";

const StyledInput = styled(Input)`
    &::placeholder {
        color: ${props => props.placeholderColor};
    }
`;

const fqdnPattern = /^(?!:\/\/)([a-zA-Z0-9]+\.)?[a-zA-Z0-9][a-zA-Z0-9-]+\.[a-zA-Z]{2,6}?$/gim;

const bg = { dark: "whiteAlpha.100", light: "white" };
const color = { dark: "whiteAlpha.800", light: "gray.400" };
const border = { dark: "whiteAlpha.50", light: "gray.100" };
const placeholderColor = { dark: "whiteAlpha.400", light: "gray.400" };

const QueryTarget = ({
    placeholder,
    register,
    setFqdn,
    name,
    value,
    setTarget,
    resolveTarget,
    displayValue,
    setDisplayValue
}) => {
    const { colorMode } = useColorMode();

    const handleBlur = () => {
        if (resolveTarget && displayValue && fqdnPattern.test(displayValue)) {
            setFqdn(displayValue);
        } else if (resolveTarget && !displayValue) {
            setFqdn(false);
        }
    };
    const handleChange = e => {
        setDisplayValue(e.target.value);
        setTarget({ field: name, value: e.target.value });
    };
    const handleKeyDown = e => {
        if ([9, 13].includes(e.keyCode)) {
            handleBlur();
        }
    };
    return (
        <>
            <input hidden readOnly name={name} ref={register} value={value} />
            <StyledInput
                size="lg"
                name="query_target_display"
                bg={bg[colorMode]}
                onBlur={handleBlur}
                onFocus={handleBlur}
                onKeyDown={handleKeyDown}
                value={displayValue}
                borderRadius="0.25rem"
                onChange={handleChange}
                color={color[colorMode]}
                placeholder={placeholder}
                borderColor={border[colorMode]}
                placeholderColor={placeholderColor[colorMode]}
            />
        </>
    );
};

QueryTarget.displayName = "QueryTarget";
export default QueryTarget;
