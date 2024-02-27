import { expect, describe, it } from 'vitest';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import { useStrf } from './use-strf';

const TEMPLATE = 'Testing {name} hook';
const OBJECT = { name: 'useStrf' };
const FINAL_VALUE = 'Testing useStrf hook';

const TestComponent = (): JSX.Element => {
  const strf = useStrf();
  const value = strf(TEMPLATE, OBJECT);
  return <div>{value}</div>;
};

describe('useStrf Hook', () => {
  it('text be formatted', () => {
    const { queryByText } = render(<TestComponent />);
    expect(queryByText(FINAL_VALUE)).toBeInTheDocument();
  });
});
