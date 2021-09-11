import { isObject } from '~/types';

import type { Config, FaviconComponent } from '~/types';

export class ConfigLoadError extends Error {
  public url: string = '/ui/props/';
  public detail?: string;
  public baseMessage: string;

  constructor(detail?: string) {
    super();
    this.detail = detail;
    this.baseMessage = `Unable to connect to hyperglass at`;
    this.message = `${this.baseMessage} '${this.url}'`;
    console.error(this);
  }

  public toString(): string {
    if (typeof this.detail !== 'undefined') {
      return `${this.message} (${this.detail})`;
    }
    return this.message;
  }
}

export async function getHyperglassConfig(): Promise<Config> {
  let mode: RequestInit['mode'];

  if (process.env.NODE_ENV === 'production') {
    mode = 'same-origin';
  } else if (process.env.NODE_ENV === 'development') {
    mode = 'cors';
  }
  const options: RequestInit = { method: 'GET', mode, headers: { 'user-agent': 'hyperglass-ui' } };

  try {
    const response = await fetch('/ui/props/', options);
    const data = await response.json();
    if (!response.ok) {
      throw response;
    }
    if (isObject(data)) {
      return data as Config;
    }
  } catch (error) {
    if (error instanceof TypeError) {
      throw new ConfigLoadError('Network Connection Error');
    }
    if (error instanceof Response) {
      throw new ConfigLoadError(`${error.status}: ${error.statusText}`);
    }
    if (error instanceof Error) {
      throw new ConfigLoadError();
    }
    throw new ConfigLoadError(String(error));
  }
  throw new ConfigLoadError('Unknown Error');
}

export async function getFavicons(): Promise<FaviconComponent[]> {
  const { favicons: faviconConfig } = process.env.hyperglass;
  return faviconConfig.map(icon => {
    const { image_format, dimensions, prefix } = icon;
    const [w, h] = dimensions;
    const rel = icon.rel ?? '';
    const src = `/images/favicons/${prefix}-${w}x${h}.${image_format}`;
    return { rel, href: src, type: `image/${image_format}` };
  });
}
