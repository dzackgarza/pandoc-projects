"use strict";
// PandocEditor.ts
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.PandocEditor = void 0;
const vscode = __importStar(require("vscode"));
const PandocHandler_1 = require("../services/PandocHandler/PandocHandler");
const logger_1 = require("../utils/logger");
/**
 * Implements a WYSIWYG Markdown editor using Pandoc for conversion
 */
class PandocEditor {
    constructor(context) {
        this.context = context;
        this.isUpdating = false; // Prevents update loops between editor and document
        this.documentChangeListener = null;
    }
    /**
     * Register the editor with VS Code
     */
    static register(context) {
        return vscode.window.registerCustomEditorProvider(PandocEditor.viewType, new PandocEditor(context), {
            webviewOptions: {
                retainContextWhenHidden: true,
                enableFindWidget: true
            },
            supportsMultipleEditorsPerDocument: false
        });
    }
    /**
     * Called when the editor is opened
     */
    resolveCustomTextEditor(document, webviewPanel, _token) {
        return __awaiter(this, void 0, void 0, function* () {
            // Configure webview
            webviewPanel.webview.options = {
                enableScripts: true,
                localResourceRoots: [this.context.extensionUri]
            };
            // Set up message handling from the webview
            this.setupMessageHandlers(webviewPanel, document);
            // Initial render
            yield this.updateWebview(document, webviewPanel);
            // Listen for document changes
            this.documentChangeListener = vscode.workspace.onDidChangeTextDocument(e => {
                if (e.document.uri.toString() === document.uri.toString() && !this.isUpdating) {
                    this.updateWebview(document, webviewPanel);
                }
            });
            // Clean up on dispose
            webviewPanel.onDidDispose(() => {
                if (this.documentChangeListener) {
                    this.documentChangeListener.dispose();
                    this.documentChangeListener = null;
                }
            });
        });
    }
    /**
     * Set up message handlers for communication with the webview
     */
    setupMessageHandlers(webviewPanel, document) {
        webviewPanel.webview.onDidReceiveMessage((message) => __awaiter(this, void 0, void 0, function* () {
            try {
                switch (message.type) {
                    case 'save':
                        try {
                            const htmlContent = message.content;
                            // 1. Convert HTML from webview to clean Markdown
                            const cleanMarkdown = yield this.updateDocument(document, htmlContent);
                            // 2. Notify webview that save was successful
                            webviewPanel.webview.postMessage({
                                type: 'saved',
                                success: true,
                                content: cleanMarkdown // Send back the cleaned markdown for consistency
                            });
                        }
                        catch (error) {
                            const errorMessage = error instanceof Error ? error.message : String(error);
                            console.error('Error saving document:', error);
                            webviewPanel.webview.postMessage({
                                type: 'saved',
                                success: false,
                                error: errorMessage
                            });
                            vscode.window.showErrorMessage(`Failed to save document: ${errorMessage}`);
                        }
                        break;
                    case 'updateContent':
                        yield this.updateDocument(document, message.content);
                        break;
                    case 'ready':
                        yield this.updateWebview(document, webviewPanel);
                        break;
                }
            }
            catch (error) {
                console.error('Error handling webview message:', error);
                vscode.window.showErrorMessage(`Error: ${error instanceof Error ? error.message : String(error)}`);
            }
        }));
    }
    /**
     * Update the document with new content from the webview
     */
    updateDocument(document, htmlContent) {
        return __awaiter(this, void 0, void 0, function* () {
            if (this.isUpdating)
                return document.getText();
            this.isUpdating = true;
            try {
                const pandocHandler = PandocHandler_1.PandocHandler.getInstance(logger_1.Logger.getInstance());
                const cleanMarkdown = yield pandocHandler.convertHtmlToMarkdown(htmlContent);
                // Update the document
                const edit = new vscode.WorkspaceEdit();
                edit.replace(document.uri, new vscode.Range(0, 0, document.lineCount, 0), cleanMarkdown);
                yield vscode.workspace.applyEdit(edit);
                yield document.save();
                return cleanMarkdown;
            }
            catch (error) {
                console.error('Error updating document:', error);
                const errorMessage = error instanceof Error ? error.message : 'Unknown error';
                vscode.window.showErrorMessage(`Error saving document: ${errorMessage}`);
                throw error;
            }
            finally {
                this.isUpdating = false;
            }
        });
    }
    /**
     * Update the webview with the current document content
     */
    updateWebview(document, webviewPanel) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const markdown = document.getText();
                const pandocHandler = PandocHandler_1.PandocHandler.getInstance(logger_1.Logger.getInstance());
                const html = yield pandocHandler.convertMarkdownToHtml(markdown, { mathjax: true });
                webviewPanel.webview.html = this.getWebviewContent(html);
            }
            catch (error) {
                console.error('Error updating webview:', error);
                const errorMessage = error instanceof Error ? error.message : 'Unknown error';
                vscode.window.showErrorMessage(`Error rendering document: ${errorMessage}`);
            }
        });
    }
    /**
     * Generate the complete HTML for the webview
     */
    getWebviewContent(html) {
        return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pandoc WYSIWYG Editor</title>
        <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        <style>
          body {
            font-family: var(--vscode-font-family);
            padding: 0 20px;
            line-height: 1.6;
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
          }
          :focus { outline: 1px solid var(--vscode-focusBorder); }
        </style>
      </head>
      <body>
        <div id="editor" contenteditable="true" style="min-height: 100vh; outline: none;">
          ${html}
        </div>
        <script>
          const vscode = acquireVsCodeApi();
          const editor = document.getElementById('editor');

          // Save content on change with debounce
          let saveTimeout;
          editor.addEventListener('input', () => {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
              vscode.postMessage({
                type: 'save',
                content: editor.innerHTML
              });
            }, 500);
          });

          // Handle messages from the extension
          window.addEventListener('message', event => {
            const message = event.data;
            if (message.type === 'update') {
              editor.innerHTML = message.content;
            } else if (message.type === 'saved') {
              // Handle save confirmation if needed
            }
          });
        </script>
      </body>
      </html>
    `;
    }
    /**
     * Generate an error view for when rendering fails
     */
    getErrorView(error) {
        return `
      <!DOCTYPE html>
      <html>
      <head>
        <style>
          body {
            font-family: var(--vscode-font-family);
            padding: 20px;
            color: var(--vscode-errorForeground);
          }
          pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            overflow-x: auto;
            max-width: 100%;
          }
        </style>
      </head>
      <body>
        <h2>Error Rendering Document</h2>
        <pre>${error}</pre>
      </body>
      </html>
    `;
    }
    /**
     * Generate a nonce for CSP
     */
    getNonce() {
        let text = '';
        const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        for (let i = 0; i < 32; i++) {
            text += possible.charAt(Math.floor(Math.random() * possible.length));
        }
        return text;
    }
}
exports.PandocEditor = PandocEditor;
PandocEditor.viewType = 'pandoc-wysiwyg.editor';
