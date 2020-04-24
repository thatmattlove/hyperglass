import * as React from "react";
import { IconButton } from "@chakra-ui/core";

// export const TableIconButton = ({ icon, onClick, isDisabled, children, variantColor, ...rest }) => {
//     return (
//         <IconButton
//             size="sm"
//             {...rest}
//             icon={icon}
//             borderWidth={1}
//             onClick={onClick}
//             variantColor={variantColor}
//             isDisabled={isDisabled}
//             aria-label="Table Icon button"
//         >
//             {children}
//         </IconButton>
//     );
// };

// TableIconButton.defaultProps = {
//     variantColor: "gray",
// };

const TableIconButton = ({
  icon,
  onClick,
  isDisabled,
  color,
  children,
  ...props
}) => {
  return (
    <IconButton
      size="sm"
      icon={icon}
      borderWidth={1}
      onClick={onClick}
      variantColor={color}
      isDisabled={isDisabled}
      aria-label="Table Icon Button"
      {...props}
    >
      {children}
    </IconButton>
  );
};

TableIconButton.displayName = "TableIconButton";

export default TableIconButton;
