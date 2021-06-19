import * as React from "react";

const Required = (): JSX.Element => {
  return (
    <span style={{ color: "var(--ifm-color-danger)", display: "inline-block" }}>
      *
    </span>
  );
};

export default Required;
