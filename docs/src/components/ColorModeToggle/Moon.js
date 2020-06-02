import * as React from "react";

export const Moon = ({ color, size = "1.5rem", ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 16 16"
    style={{
      height: size,
      width: size,
    }}
    strokeWidth={0}
    stroke="currentColor"
    fill="currentColor"
    {...props}
  >
    <path
      d="M14.53 10.53a7 7 0 01-9.058-9.058A7.003 7.003 0 008 15a7.002 7.002 0 006.53-4.47z"
      fill={color || "currentColor"}
      fillRule="evenodd"
      clipRule="evenodd"
    />
  </svg>
);
