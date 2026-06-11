import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/react';
import { cleanup } from '@testing-library/react';
import { afterEach, describe, expect, it } from 'vitest';
import { MessageItem } from './MessageItem';

afterEach(() => cleanup());

describe('MessageItem', () => {
    it('applies wrapping rules to long unbroken messages', () => {
        const text = 'a'.repeat(300);
        render(<MessageItem message={{
            id: 'long',
            sender: 'user',
            text,
            timestamp: '2026-06-11T00:00:00Z'
        }} />);
        const paragraph = screen.getByText(text);
        expect(paragraph).toHaveClass('break-words');
        expect(paragraph.className).toContain('[overflow-wrap:anywhere]');
    });
});
