/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable react-hooks/rules-of-hooks */
import { memo, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { chakra, Icon as ChakraIcon } from '@chakra-ui/react';
import isEqual from 'react-fast-compare';

import type { IconProps as ChakraIconProps, TooltipProps } from '@chakra-ui/react';

interface IconMap {
  [library: string]: string;
}

interface DynamicIconProps extends Omit<ChakraIconProps, 'icon'> {
  icon: IconMap;
}

interface ErrorIconProps {
  message: string;
}

interface IconErrorConstructor {
  original: IconMap;
  library: string;
  iconName: string;
}

/**
 * Extend builtin `Error` for easier handling of icon rendering errors.
 */
class IconError extends Error {
  /**
   * Original family → icon mapping object.
   */
  original: IconMap;
  /**
   * Determined family/icon library.
   */
  library: string;
  /**
   * Determined icon name.
   */
  iconName: string;

  constructor({ original, library, iconName }: IconErrorConstructor) {
    super();
    this.original = original;
    this.library = library;
    this.iconName = iconName;
    this.stack += `\nOriginal object: '${JSON.stringify(this.original)}'`;
  }

  get message(): string {
    return `No icon matches 'react-icons/${this.library}/${this.iconName}'`;
  }
}

/**
 * Derive `react-icons` icon family → icon name mapping with proper capitalization. Also handles
 * existence (or not) of the family prefix.
 * @param iconObj Family to icon name mapping.
 *
 * @example
 * ```js
 * iconPath({ fa: 'FaPlus' });
 * iconPath({ fa: 'faplus' });
 * iconPath({ fa: 'plus' });
 * // all return → ['fa', 'FaPlus']
 * ```
 * @returns
 */
function iconPath(iconObj: IconMap): [string, string] {
  // Capitalize the first character of a string.
  const capitalizeFirst = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

  // Get the first object key.
  const [familyKey] = Object.keys(iconObj);
  // Capitalize the family name.
  const family = capitalizeFirst(familyKey!);
  // Get the icon name.
  const initialName = iconObj[familyKey!];
  // Capitalize the icon name. If `faplus` is provided, it will now be `Faplus`.
  let name = capitalizeFirst(initialName!);
  // Create a regex pattern to determine if the family name is in the icon name. If `name` is
  // `Faplus`, this will be true.
  const familyPattern = new RegExp(`^${family}`, 'g');

  if (name.match(familyPattern)) {
    // If the icon name contains the family name, remove it and capitalize the result. If `name`
    // was `Faplus`, it is now `Plus`.
    name = capitalizeFirst(name.replace(familyPattern, ''));
  }
  // Return a tuple of [family, icon name], i.e. [fa, FaPlus].
  return [family.toLowerCase(), `${family}${name}`];
}

/**
 * Generic error icon to indicate that there was a problem dynamically importing or otherwise
 * rendering the dynamic icon. Wraps generic icon in a tooltip that provides more detail. This
 * is dynamically imported at render time in an effort to reduce load times.
 *
 * @param props Error message to be displayed.
 */
const ErrorIcon = (props: ErrorIconProps): JSX.Element => {
  const Tooltip = dynamic<TooltipProps>(() => import('@chakra-ui/react').then(m => m.Tooltip));
  return (
    <Tooltip hasArrow bg="red.500" label={props.message}>
      <chakra.span boxSize={8} color="red.500" p={1} textAlign="center">
        &#9888;
      </chakra.span>
    </Tooltip>
  );
};

const _DynamicIcon = (props: DynamicIconProps): JSX.Element => {
  const { icon: iconObj, ...rest } = props;
  // Create a string representation of the icon family and name mapping for memoization.
  const key = Object.entries(iconObj).flat().join('--');
  try {
    const [library, iconName] = useMemo(() => {
      return iconPath(iconObj);
    }, [key]);

    if (!library || !iconName) {
      // If either the library or icon name are falsy, error out.
      throw new IconError({ original: iconObj, iconName, library });
    }
    // Create a memoized version of the imported component, to update only when the computed
    // family/icon names are changed. Attempt to dynamically import icon from formatted
    // library/icon name.

    const Component = useMemo(
      () =>
        dynamic(() =>
          import(`react-icons/${library}/index.js`)
            .then(i => {
              if (!(iconName in i)) {
                // If the icon name doesn't exist in the module, error out.
                throw new IconError({ original: iconObj, iconName, library });
              }
              // Otherwise, return the imported icon.
              return i[iconName as keyof typeof i];
            })
            .catch(error => {
              // Handle any error that occurs during dynamic import.
              console.error(error);
              const CaughtError = (): JSX.Element => <ErrorIcon message={String(error)} />;
              return CaughtError;
            }),
        ),
      [library, iconName],
    );

    // Return a Chakra-UI icon instance with the imported icon.
    return <ChakraIcon as={Component} {...rest} />;
  } catch (error) {
    // Handle any other uncaught errors.
    console.error(error);
    return <ErrorIcon message={String(error)} />;
  }
};

/**
 * Dynamically import a `react-icons` icon by name and wrap it in a Chakra-UI icon component.
 *
 * @param props Icon family to icon name mapping.
 *
 * @throws An error icon is produced if there is any error during the dynamic import process. A
 * console message is also displayed with additional details.
 *
 * @example
 * ```js
 * <>
 *   <Icon icon={{ fa: 'FaPlus' }} />
 *   // This also works:
 *   <Icon icon={{ fa: 'plus' }} />
 * </>
 * ```
 */
export const DynamicIcon = memo(_DynamicIcon, isEqual);
export default DynamicIcon;
