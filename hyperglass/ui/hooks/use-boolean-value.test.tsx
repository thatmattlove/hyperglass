import { expect, describe, it } from 'vitest';
import { renderHook } from '@testing-library/react';
import '@testing-library/jest-dom';
import { useBooleanValue } from './use-boolean-value';

const VALUE_IF_TRUE = 'Is True';
const VALUE_IF_FALSE = 'Is False';

describe('useBooleanValue Hook', () => {
  it('text should reflect boolean state', () => {
    const { result, rerender } = renderHook(
      ({ initial }) => useBooleanValue(initial, VALUE_IF_TRUE, VALUE_IF_FALSE),
      { initialProps: { initial: false } },
    );
    expect(result.current).toBe(VALUE_IF_FALSE);
    rerender({ initial: true });
    expect(result.current).toBe(VALUE_IF_TRUE);
    rerender({ initial: false });
    expect(result.current).toBe(VALUE_IF_FALSE);
  });
});
