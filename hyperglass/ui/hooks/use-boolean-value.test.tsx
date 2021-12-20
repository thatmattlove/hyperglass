import { useState } from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import { useBooleanValue } from './use-boolean-value';

const VALUE_IF_TRUE = 'Is True';
const VALUE_IF_FALSE = 'Is False';

const TestComponent = (): JSX.Element => {
  const [state, setState] = useState<boolean>(false);
  const value = useBooleanValue(state, VALUE_IF_TRUE, VALUE_IF_FALSE);
  return (
    <div>
      <span>{value}</span>
      <button type="button" onClick={() => setState(p => !p)}>
        Toggle
      </button>
    </div>
  );
};

describe('useBooleanValue Hook', () => {
  it('text should reflect boolean state', () => {
    const { queryByText, getByRole } = render(<TestComponent />);

    expect(queryByText(VALUE_IF_FALSE)).toBeInTheDocument();

    userEvent.click(getByRole('button'));

    expect(queryByText(VALUE_IF_FALSE)).not.toBeInTheDocument();

    expect(queryByText(VALUE_IF_TRUE)).toBeInTheDocument();
  });
});
