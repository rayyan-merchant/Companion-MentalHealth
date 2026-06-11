import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import { Composer } from './Composer';

afterEach(() => cleanup());

describe('Composer', () => {
    it('shows an inline error for an empty message', async () => {
        render(<Composer onSend={vi.fn()} />);
        await userEvent.click(screen.getByRole('button', { name: /send message/i }));
        expect(screen.getByText(/enter a message before sending/i)).toBeInTheDocument();
    });

    it('clears input and sends trimmed text', async () => {
        const onSend = vi.fn();
        render(<Composer onSend={onSend} />);
        const input = screen.getByLabelText(/message input/i);
        await userEvent.type(input, '  hello  ');
        await userEvent.click(screen.getByRole('button', { name: /send message/i }));
        expect(onSend).toHaveBeenCalledWith('hello');
        expect(input).toHaveValue('');
    });

    it('shows the counter near the limit', async () => {
        render(<Composer onSend={vi.fn()} />);
        fireEvent.change(screen.getByLabelText(/message input/i), {
            target: { value: 'a'.repeat(3500) }
        });
        expect(screen.getByText('3,500 / 4,000')).toBeInTheDocument();
    });
});
