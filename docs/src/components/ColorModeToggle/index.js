import * as React from "react";
import classnames from "classnames";
import { Sun } from "./Sun";
import { Moon } from "./Moon";
import styles from "./styles.module.css";

const iconMap = { true: Moon, false: Sun };

export const ColorModeToggle = ({ isDark, toggle, ...props }) => {
  const Icon = iconMap[isDark];
  const handleToggle = () => {
    if (isDark) {
      return toggle(false);
    } else {
      return toggle(true);
    }
  };
  const label = `${isDark ? "Hurt" : "Rest"} your eyes`;
  return (
    <button
      aria-label={label}
      title={label}
      className={classnames(styles.colorModeToggle)}
      onClick={handleToggle}
      {...props}
    >
      <Icon />
    </button>
  );
};
