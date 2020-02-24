import React from "react";
import { Button } from "@chakra-ui/core";
import { FiChevronLeft } from "react-icons/fi";

export default React.forwardRef(({ isSubmitting, onClick }, ref) => (
    <Button
        ref={ref}
        aria-label="Reset Form"
        opacity={isSubmitting ? 1 : 0}
        variant="ghost"
        color="current"
        onClick={onClick}
    >
        <FiChevronLeft size={24} />
    </Button>
));
