import React from "React";
import classnames from "classnames";
import styles from "./fonts.module.css";

export default ({ name }) => {
    const fontClass = { Nunito: "fontBody", "Fira Code": "fontMono" };
    return (
        <a href={`https://fonts.google.com/specimen/${name.split(" ").join("+")}`}>
            <span className={classnames(styles.font, styles[fontClass[name]])}>{name}</span>
        </a>
    );
};
