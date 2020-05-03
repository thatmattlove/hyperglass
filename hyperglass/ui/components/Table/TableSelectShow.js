import * as React from "react";
import { Select } from "@chakra-ui/core";

{
  /* <select 
    value={pageSize}
    onChange={e => {setPageSize(Number(e.target.value))}}
>
    {[5, 10, 20, 30, 40, 50].map(pageSize => (
        <option key={pageSize} value={pageSize}>
            Show {pageSize}
        </option>
    ))}
</select> */
}

const TableSelectShow = ({ value, onChange, children, ...props }) => {
  return (
    <Select size="sm" onChange={onChange} {...props}>
      {[5, 10, 20, 30, 40, 50].map(value => (
        <option key={value} value={value}>
          Show {value}
        </option>
      ))}
      {children}
    </Select>
  );
};

TableSelectShow.displayName = "TableSelectShow";

export default TableSelectShow;
