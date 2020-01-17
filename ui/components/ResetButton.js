import React from "react";
import { Box, Button } from "@chakra-ui/core";
import { FiChevronLeft } from "react-icons/fi";

export default React.forwardRef(({ isSubmitting, onClick }, ref) => (
    <Box ref={ref} position="fixed" bottom={16} left={8} opacity={isSubmitting ? 1 : 0}>
        <Button variantColor="primary" variant="outline" p={2} onClick={onClick}>
            <FiChevronLeft size={24} />
        </Button>
    </Box>
));
