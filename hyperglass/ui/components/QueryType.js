import React from "react";
import ChakraSelect from "~/components/ChakraSelect";

export default ({ queryTypes, onChange }) => {
    const queries = queryTypes
        .filter(q => q.enable === true)
        .map(q => {
            return { value: q.name, label: q.display_name };
        });
    return (
        <ChakraSelect
            size="lg"
            name="query_type"
            onChange={e => onChange({ field: "query_type", value: e.value })}
            options={queries}
        />
    );
};
