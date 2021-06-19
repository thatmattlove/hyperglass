import * as React from "react";

type MiniNodeProps = {
  newLine: boolean;
};

const MiniNote = (
  props: React.PropsWithChildren<MiniNodeProps>
): JSX.Element => {
  const { newLine, children } = props;
  return (
    <>
      {newLine && <br />}
      <span
        style={{
          fontSize: "var(--ifm-font-size-sm)",
          color: "var(--ifm-blockquote-color)",
          display: "inline-block",
          fontStyle: "italic",
        }}
      >
        {children}
      </span>
    </>
  );
};

export default MiniNote;
