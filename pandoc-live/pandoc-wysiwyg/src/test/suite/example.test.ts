import * as assert from 'assert';
import * as vscode from 'vscode';
import * as sinon from 'sinon';

// Mock vscode module
const mockVSCode = {
  window: {
    showInformationMessage: () => {},
    showErrorMessage: () => {}
  },
  Uri: {
    parse: (uri: string) => ({ path: uri, fsPath: uri })
  },
  ViewColumn: {
    Active: 1,
    Beside: 2,
    One: 1,
    Two: 2,
    Three: 3,
    Four: 4,
    Five: 5,
    Six: 6,
    Seven: 7,
    Eight: 8,
    Nine: 9
  },
  Disposable: class {},
  EventEmitter: class {},
  WebviewPanel: class {},
  workspace: {
    fs: {},
    onDidSaveTextDocument: () => { return { dispose: () => {} }; },
    onDidChangeTextDocument: () => { return { dispose: () => {} }; },
    textDocuments: []
  },
  commands: {
    executeCommand: () => {}
  }
};

// Mock the vscode module
jest.mock('vscode', () => mockVSCode);

// Import the module to test after mocking
import { PandocEditor } from '../../editor/PandocEditor';

describe('Extension Test Suite', () => {
  vscode.window.showInformationMessage('Start all tests.');

  it('Sample test', () => {
    assert.strictEqual(-1, [1, 2, 3].indexOf(5));
    assert.strictEqual(-1, [1, 2, 3].indexOf(0));
  });

  it('PandocEditor should be defined', () => {
    assert.ok(PandocEditor);
  });
});
