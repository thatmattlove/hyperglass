import React from "react";
import ChakraSelect from "~/components/ChakraSelect";

export default ({ vrfs, onChange }) => {
    return (
        <ChakraSelect
            size="lg"
            placeholder="VRF"
            onChange={e => onChange({ field: "query_vrf", value: e.value })}
            name="query_vrf"
            options={vrfs}
        />
    );
};
