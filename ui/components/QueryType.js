import React from "react";
import ChakraSelect from "~/components/ChakraSelect";

const buildQueries = queryTypes => {
    const queries = [];
    queryTypes.map(q => {
        queries.push({ value: q.name, label: q.display_name });
    });
    return queries;
};

export default ({ queryTypes, onChange }) => {
    const queries = buildQueries(queryTypes);
    return (
        <ChakraSelect
            size="lg"
            name="query_type"
            onChange={e => onChange({ field: "query_type", value: e.value })}
            options={queries}
        />
    );
};
