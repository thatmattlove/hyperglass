import * as React from "react";
import styles from "./styles.module.css";

const JSXCode = (props: React.ComponentProps<"span">): JSX.Element => {
  return <span className={styles.code} {...props} />;
};

export default JSXCode;
