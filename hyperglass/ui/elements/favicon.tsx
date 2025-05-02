import type { Favicon as FaviconProps } from '~/types';

/**
 * Render a `<link/>` element to reference a server-side favicon.
 */
export const Favicon = (props: FaviconProps): JSX.Element => {
  const { image_format, dimensions, prefix, rel } = props;
  const [w, h] = dimensions;
  const src = `/images/favicons/${prefix}-${w}x${h}.${image_format}`;
  return <link rel={rel ?? ''} href={src} type={`image/${image_format}`} />;
};
