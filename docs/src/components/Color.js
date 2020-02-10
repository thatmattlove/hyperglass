import React from "react";
import styles from "./styles.module.css";

export default ({ hex }) => (
    <div className={styles.colorCode}>
        <span style={{ backgroundColor: hex }} className={styles.color} />
        <span className={styles.code}>{hex}</span>
    </div>
);
