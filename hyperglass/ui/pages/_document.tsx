import fs from 'fs';
import { ColorModeScript } from '@chakra-ui/react';
import Document, { Html, Head, Main, NextScript } from 'next/document';
import { CustomHtml, CustomJavascript, Favicon } from '~/elements';
import { googleFontUrl } from '~/util';
import favicons from '../favicon-formats';

import type { DocumentContext, DocumentInitialProps } from 'next/document';
import type { Config, ThemeConfig } from '~/types';

// Declare imported JSON type to avoid type errors when file is not present (testing).
const config = (await import('../hyperglass.json')) as unknown as Config;

interface DocumentExtra
  extends DocumentInitialProps,
    Pick<ThemeConfig, 'defaultColorMode' | 'fonts'> {
  customJs: string;
  customHtml: string;
}

class MyDocument extends Document<DocumentExtra> {
  static async getInitialProps(ctx: DocumentContext): Promise<DocumentExtra> {
    const initialProps = await Document.getInitialProps(ctx);
    let customJs = '';
    let customHtml = '';

    if (fs.existsSync('custom.js')) {
      customJs = fs.readFileSync('custom.js').toString();
    }
    if (fs.existsSync('custom.html')) {
      customHtml = fs.readFileSync('custom.html').toString();
    }

    let fonts = { body: '', mono: '' };
    let defaultColorMode: 'light' | 'dark' | null = null;

    // const hyperglassUrl = process.env.HYPERGLASS_URL ?? '';
    // const {
    //   web: {
    //     theme: { fonts: themeFonts, defaultColorMode: themeDefaultColorMode },
    //   },
    // } = await getHyperglassConfig(hyperglassUrl);

    fonts = {
      body: googleFontUrl(config.web.theme.fonts.body),
      mono: googleFontUrl(config.web.theme.fonts.mono),
    };
    defaultColorMode = config.web.theme.defaultColorMode;

    return { customJs, customHtml, fonts, defaultColorMode, ...initialProps };
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
          <link rel="dns-prefetch" href="//fonts.gstatic.com" />
          <link rel="dns-prefetch" href="//fonts.googleapis.com" />
          <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
          <link href={this.props.fonts.mono} rel="stylesheet" />
          <link href={this.props.fonts.body} rel="stylesheet" />
          {favicons.map(favicon => (
            <Favicon key={JSON.stringify(favicon)} {...favicon} />
          ))}
          <CustomJavascript>{this.props.customJs}</CustomJavascript>
        </Head>
        <body>
          <ColorModeScript initialColorMode={this.props.defaultColorMode ?? 'system'} />
          <Main />
          <CustomHtml>{this.props.customHtml}</CustomHtml>
          <NextScript />
        </body>
      </Html>
    );
  }
}

export default MyDocument;
