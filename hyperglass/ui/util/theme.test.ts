import { googleFontUrl } from './theme';
import { describe, expect, test } from 'vitest';

describe('google font URL generation', () => {
  test('no space font', () => {
    const result = googleFontUrl('Inter', [100, 200, 300]);
    expect(result).toBe('https://fonts.googleapis.com/css?family=Inter:100,200,300&display=swap');
  });
  test('space font', () => {
    const result = googleFontUrl('Open Sans', [100, 200, 300]);
    expect(result).toBe(
      'https://fonts.googleapis.com/css?family=Open+Sans:100,200,300&display=swap',
    );
  });
});
