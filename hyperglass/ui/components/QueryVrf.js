import React from "react";
import ChakraSelect from "~/components/ChakraSelect";

const QueryVrf = ({ vrfs, onChange, label }) => {
  return (
    <ChakraSelect
      size="lg"
      onChange={e => onChange({ field: "query_vrf", value: e.value })}
      name="query_vrf"
      options={vrfs}
      aria-label={label}
    />
  );
};

QueryVrf.displayName = "QueryVrf";
export default QueryVrf;
