import * as React from "react";

type DatetimeProps = {
  year?: boolean;
};

const Datetime = (
  props: React.PropsWithChildren<DatetimeProps>
): JSX.Element => {
  const { year } = props;
  const date = new Date();
  const granularity = year ? date.getFullYear() : date.toString();
  return <span {...props}>{granularity}</span>;
};

export default Datetime;
