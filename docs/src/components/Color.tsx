import * as React from "react";
import styles from "./styles.module.css";

type ColorProps = {
  hex: string;
};

const Color = (props: React.PropsWithChildren<ColorProps>): JSX.Element => {
  const { hex } = props;
  return (
    <div className={styles.colorCode}>
      <span style={{ backgroundColor: hex }} className={styles.color} />
      <span className={styles.code}>{hex}</span>
    </div>
  );
};

export default Color;
