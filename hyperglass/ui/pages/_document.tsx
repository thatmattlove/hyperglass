import Document, { Html, Head, Main, NextScript } from 'next/document';
import { Favicon } from '~/components';
import favicons from '../favicon-formats';

import type { DocumentContext, DocumentInitialProps } from 'next/document';

class MyDocument extends Document {
  static async getInitialProps(ctx: DocumentContext): Promise<DocumentInitialProps> {
    const initialProps = await Document.getInitialProps(ctx);
    return { ...initialProps };
  }

  render(): JSX.Element {
    return (
      <Html lang="en">
        <Head>
          <meta name="language" content="en" />
          <meta httpEquiv="Content-Type" content="text/html" />
          <meta charSet="UTF-8" />
          <meta name="og:type" content="website" />
          <meta name="og:image" content="/images/opengraph.jpg" />
          <meta property="og:image:width" content="1200" />
          <meta property="og:image:height" content="630" />
          <meta
            name="viewport"
            content="width=device-width, initial-scale=1, user-scalable=no, maximum-scale=1.0, minimum-scale=1.0"
          />
          <link rel="dns-prefetch" href="//fonts.gstatic.com" />
          <link rel="dns-prefetch" href="//fonts.googleapis.com" />
          <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="true" />
          {favicons.map((favicon, idx) => (
            <Favicon key={idx} {...favicon} />
          ))}
        </Head>
        <body>
          <Main />
          <NextScript />
        </body>
      </Html>
    );
  }
}

export default MyDocument;
