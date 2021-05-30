import * as React from "react";
import clsx from "clsx";
import styles from "./fonts.module.css";

type FontProps = {
  name: string;
};

const Font = (props: React.PropsWithChildren<FontProps>): JSX.Element => {
  const { name } = props;
  const fontClass = { Nunito: "fontBody", "Fira Code": "fontMono" };
  return (
    <a href={`https://fonts.google.com/specimen/${name.split(" ").join("+")}`}>
      <span className={clsx(styles.font, styles[fontClass[name]])}>{name}</span>
    </a>
  );
};

export default Font;
