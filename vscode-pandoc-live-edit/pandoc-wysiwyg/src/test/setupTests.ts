// Import Jest globals
import { beforeAll, afterAll, expect, jest } from '@jest/globals';

// Extend Jest expect with custom matchers
declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace jest {
    interface Matchers<R> {
      toBeWithinRange(floor: number, ceiling: number): R;
    }
  }
}

// Setup mock timers
beforeAll(() => {
  jest.useFakeTimers();
  
  // Mock the console to keep test output clean
  const consoleError = console.error;
  const consoleWarn = console.warn;
  
  // Mock console.error to fail tests on error
  console.error = (message: string) => {
    throw new Error(`Unexpected console.error: ${message}`);
  };

  // Mock console.warn to fail tests on warning
  console.warn = (message: string) => {
    throw new Error(`Unexpected console.warn: ${message}`);
  };
  
  // Restore original console methods after all tests
  afterAll(() => {
    console.error = consoleError;
    console.warn = consoleWarn;
  });
});

// Add custom matchers
expect.extend({
  toBeWithinRange(received: number, floor: number, ceiling: number) {
    const pass = received >= floor && received <= ceiling;
    if (pass) {
      return {
        message: () =>
          `expected ${received} not to be within range ${floor} - ${ceiling}`,
        pass: true,
      };
    } else {
      return {
        message: () =>
          `expected ${received} to be within range ${floor} - ${ceiling}`,
        pass: false,
      };
    }
  },
});
