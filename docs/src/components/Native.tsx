import * as React from "react";
import styles from "./styles.module.css";

const Native = (props: React.ComponentProps<"span">): JSX.Element => {
  const { children } = props;
  return <span className={styles.Native}>{children}</span>;
};

export default Native;
