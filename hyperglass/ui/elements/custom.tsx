/**
 * Render a generic script tag in the `<head/>` that contains any custom-defined Javascript, if
 * defined. It no custom JS is defined, an empty fragment is rendered, which will not appear in
 * the DOM.
 */
export const CustomJavascript = (props: React.PropsWithChildren<Dict>): JSX.Element => {
  const { children } = props;
  if (typeof children === 'string' && children !== '') {
    // biome-ignore lint/security/noDangerouslySetInnerHtml: required for injecting custom JS
    return <script id="custom-javascript" dangerouslySetInnerHTML={{ __html: children }} />;
  }
  return <></>;
};

/**
 * Render a generic div outside of the main application that contains any custom-defined HTML, if
 * defined. If no custom HTML is defined, an empty fragment is rendered, which will not appear in
 * the DOM.
 */
export const CustomHtml = (props: React.PropsWithChildren<Dict>): JSX.Element => {
  const { children } = props;
  if (typeof children === 'string' && children !== '') {
    // biome-ignore lint/security/noDangerouslySetInnerHtml: required for injecting custom HTML
    return <div id="custom-html" dangerouslySetInnerHTML={{ __html: children }} />;
  }
  return <></>;
};
