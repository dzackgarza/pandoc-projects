// Mock implementation of the vscode module for testing
const vscode = {
  // Mock version of the ExtensionContext
  ExtensionContext: class {
    subscriptions = [];
    workspaceState = {
      get: jest.fn(),
      update: jest.fn(),
    };
    globalState = {
      get: jest.fn(),
      update: jest.fn(),
    };
    extensionPath = '';
    storagePath = '';
    globalStoragePath = '';
    logPath = '';
  },

  // Mock version of the window object
  window: {
    showInformationMessage: jest.fn(),
    showErrorMessage: jest.fn(),
    showWarningMessage: jest.fn(),
    showInputBox: jest.fn(),
    showQuickPick: jest.fn(),
    showOpenDialog: jest.fn(),
    showSaveDialog: jest.fn(),
    showTextDocument: jest.fn(),
    createStatusBarItem: jest.fn(),
    withProgress: jest.fn(),
  },

  // Mock version of the Uri class
  Uri: {
    parse: jest.fn().mockImplementation((value) => ({
      scheme: 'file',
      path: value,
      fsPath: value,
      with: jest.fn(),
      toString: () => value,
    })),
    file: jest.fn().mockImplementation((path) => ({
      scheme: 'file',
      path,
      fsPath: path,
      with: jest.fn(),
      toString: () => `file://${path}`,
    })),
  },

  // Mock version of ViewColumn
  ViewColumn: {
    Active: -1,
    Beside: -2,
    One: 1,
    Two: 2,
    Three: 3,
  },

  // Mock version of the workspace object
  workspace: {
    workspaceFolders: [],
    onDidChangeWorkspaceFolders: jest.fn(),
    createFileSystemWatcher: jest.fn(),
    onDidChangeConfiguration: jest.fn(),
    getConfiguration: jest.fn().mockReturnValue({
      get: jest.fn(),
      update: jest.fn(),
      has: jest.fn(),
      inspect: jest.fn(),
    }),
    onDidChangeTextDocument: jest.fn(),
    onDidOpenTextDocument: jest.fn(),
    onDidCloseTextDocument: jest.fn(),
    onDidSaveTextDocument: jest.fn(),
    openTextDocument: jest.fn(),
    fs: {
      readFile: jest.fn(),
      writeFile: jest.fn(),
      stat: jest.fn(),
      readDirectory: jest.fn(),
      createDirectory: jest.fn(),
      delete: jest.fn(),
      rename: jest.fn(),
      copy: jest.fn(),
      isWritableFileSystem: jest.fn(),
    },
    asRelativePath: jest.fn(),
  },

  // Mock version of the commands object
  commands: {
    executeCommand: jest.fn(),
    registerCommand: jest.fn(),
    registerTextEditorCommand: jest.fn(),
  },

  // Mock version of the Disposable class
  Disposable: class {
    constructor() {}
    dispose() {}
  },

  // Mock version of the EventEmitter class
  EventEmitter: class {
    event = jest.fn();
    fire = jest.fn();
    dispose = jest.fn();
  },

  // Mock version of the WebviewPanel class
  WebviewPanel: class {
    static activePanels = new Map();
    static createOrShow = jest.fn();
    static revive = jest.fn();
    static currentPanel = undefined;
    
    constructor() {
      this.webview = {
        html: '',
        onDidReceiveMessage: jest.fn(),
        postMessage: jest.fn(),
        asWebviewUri: jest.fn(),
        cspSource: 'vscode-webview://',
      };
      this.onDidDispose = jest.fn();
      this.onDidChangeViewState = jest.fn();
      this.visible = true;
      this.active = true;
      this.title = '';
      this.viewType = '';
      this.options = {};
    }
    
    dispose() {}
    reveal() {}
  },
};

// Mock the vscode module
jest.mock('vscode', () => vscode, { virtual: true });

// Export the mock for use in tests
module.exports = vscode;
