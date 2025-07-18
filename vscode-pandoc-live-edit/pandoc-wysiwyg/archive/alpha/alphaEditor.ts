import * as vscode from 'vscode';
import * as cp from 'child_process';
import { FileBroker } from '../services/FileBroker/FileBroker';

export class AlphaPandocEditor implements vscode.CustomTextEditorProvider {
  public static readonly viewType = 'pandoc-wysiwyg.alpha';

  public static register(context: vscode.ExtensionContext): vscode.Disposable {
    return vscode.window.registerCustomEditorProvider(
      AlphaPandocEditor.viewType,
      new AlphaPandocEditor(context),
      { 
        webviewOptions: { retainContextWhenHidden: true },
        supportsMultipleEditorsPerDocument: false 
      }
    );
  }

  private fileBroker: FileBroker;

  constructor(private readonly context: vscode.ExtensionContext) {
    this.fileBroker = FileBroker.getInstance();
    this.initializeFileBroker();
  }

  private async initializeFileBroker() {
    try {
      await this.fileBroker.initialize();
    } catch (error) {
      console.error('Failed to initialize FileBroker:', error);
      vscode.window.showErrorMessage('Failed to initialize file system. Some features may not work correctly.');
    }
  }

  public async resolveCustomTextEditor(
    document: vscode.TextDocument,
    webviewPanel: vscode.WebviewPanel,
    _token: vscode.CancellationToken
  ): Promise<void> {
    // Setup webview
    webviewPanel.webview.options = {
      enableScripts: true,
      localResourceRoots: [this.context.extensionUri]
    };

    // Initial content load
    const updateWebview = async () => {
      try {
        const md = document.getText();
        const html = await this.convertMarkdownToHtml(md);
        webviewPanel.webview.html = this.getHtmlForWebview(html, webviewPanel.webview);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : String(err);
        webviewPanel.webview.html = this.getErrorHtml(errorMessage);
      }
    };

    // Handle document changes
    const changeDocumentSubscription = vscode.workspace.onDidChangeTextDocument(e => {
      if (e.document.uri.toString() === document.uri.toString()) {
        updateWebview();
      }
    });

    // Handle webview messages
    webviewPanel.webview.onDidReceiveMessage(
      async (message: any) => {
        try {
          switch (message.command) {
            case 'edit':
              await this.updateDocument(document, message.content);
              break;
            case 'save':
              try {
                const success = await this.saveDocument(document, message.content);
                // Send confirmation back to the webview
                if (webviewPanel.webview) {
                  webviewPanel.webview.postMessage({
                    command: 'saved',
                    success: success
                  });
                }
              } catch (error) {
                console.error('Error saving document:', error);
                const errorMessage = error instanceof Error ? error.message : String(error);
                vscode.window.showErrorMessage(`Failed to save file: ${errorMessage}`);
                if (webviewPanel.webview) {
                  webviewPanel.webview.postMessage({
                    command: 'error',
                    message: errorMessage
                  });
                }
              }
              break;
          }
        } catch (error) {
          console.error('Error handling webview message:', error);
          if (webviewPanel.webview) {
            const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
            webviewPanel.webview.postMessage({
              command: 'error',
              message: errorMessage
            });
          }
        }
      },
      undefined,
      this.context.subscriptions
    );

    // Clean up
    webviewPanel.onDidDispose(() => {
      changeDocumentSubscription.dispose();
    });

    // Initial render
    updateWebview();
  }

  private async saveDocument(document: vscode.TextDocument, content: string): Promise<boolean> {
    try {
      // Save using FileBroker which will handle cleaning
      await this.fileBroker.saveFile(document.uri.fsPath, content);
      return true;
    } catch (error) {
      console.error('Error saving file:', error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      vscode.window.showErrorMessage(`Failed to save file: ${errorMessage}`);
      return false;
    }
  }

  private async updateDocument(document: vscode.TextDocument, content: string) {
    const edit = new vscode.WorkspaceEdit();
    const fullRange = new vscode.Range(
      document.positionAt(0),
      document.positionAt(document.getText().length)
    );
    
    edit.replace(document.uri, fullRange, content);
    await vscode.workspace.applyEdit(edit);
  }

  private async convertMarkdownToHtml(content: string): Promise<string> {
    // If the content is already HTML (contains HTML tags), return it directly
    if (/<[a-z][\s\S]*>/i.test(content)) {
      return content;
    }

    // Otherwise, convert markdown to HTML using pandoc
    return new Promise((resolve, reject) => {
      const pandoc = cp.spawn("pandoc", [
        "--from=commonmark_x+sourcepos",
        "--to=html",
        "--mathjax"
      ]);

      let stdout = "";
      let stderr = "";

      pandoc.stdout.on("data", (chunk: Buffer) => (stdout += chunk.toString()));
      pandoc.stderr.on("data", (chunk: Buffer) => (stderr += chunk.toString()));

      pandoc.on("close", (code: number | null) => {
        if (code === 0) {
          resolve(stdout);
        } else {
          console.error('Pandoc conversion error:', stderr);
          // Fallback to a simple HTML wrapper if pandoc fails
          resolve(`<div>${content.replace(/\n/g, '<br>')}</div>`);
        }
      });

      pandoc.on("error", (err) => {
        console.error('Failed to start pandoc:', err);
        // Fallback to a simple HTML wrapper if pandoc is not available
        resolve(`<div>${content.replace(/\n/g, '<br>')}</div>`);
      });

      pandoc.stdin.write(content);
      pandoc.stdin.end();
    });
  }

  private getHtmlForWebview(htmlBody: string, webview: vscode.Webview): string {
    const mathjaxCdn = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js";
    const nonce = this.getNonce();

    return `<!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta http-equiv="Content-Security-Policy" 
              content="default-src 'none'; 
                      script-src 'nonce-${nonce}' 'unsafe-inline' 'unsafe-eval' ${webview.cspSource} https:; 
                      style-src 'unsafe-inline' ${webview.cspSource} https:; 
                      img-src ${webview.cspSource} https: data:;
                      font-src ${webview.cspSource} https: data:;">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script nonce="${nonce}" id="MathJax-script" async src="${mathjaxCdn}"></script>
        <style nonce="${nonce}">
          body { 
            font-family: var(--vscode-font-family, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif); 
            line-height: 1.6; 
            padding: 20px; 
            max-width: 800px; 
            margin: 0 auto; 
          }
          #editor { 
            min-height: 100vh;
            outline: none;
          }
          :focus {
            outline: 2px solid var(--vscode-focusBorder, #007fd4);
            outline-offset: 2px;
          }
          div.theorem { 
            border-left: 3px solid #007acc; 
            padding: 0.5em 1em; 
            margin: 1em 0; 
            background-color: rgba(0, 122, 204, 0.05);
            border-radius: 0 4px 4px 0;
          }
        </style>
      </head>
      <body>
        <div id="editor" contenteditable="true">${htmlBody}</div>
        <div id="status-bar" style="position: fixed; bottom: 10px; right: 10px; background: var(--vscode-statusBar-background); color: var(--vscode-statusBar-foreground); padding: 4px 8px; border-radius: 4px; display: none;">
          Saved
        </div>
        <script nonce="${nonce}">
          const vscode = acquireVsCodeApi();
          const editor = document.getElementById('editor');
          const statusBar = document.getElementById('status-bar');
          let isUpdating = false;
          let lastContent = editor.innerHTML;
          let saveTimeout;
          let mathJaxReady = false;
          
          function showStatus(message, duration = 2000) {
            if (!statusBar) return;
            statusBar.textContent = message;
            statusBar.style.display = 'block';
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
              if (statusBar) statusBar.style.display = 'none';
            }, duration);
          }

          // Handle content changes with debounce
          let updateTimeout;
          function handleContentChange() {
            if (isUpdating) return;
            clearTimeout(updateTimeout);
            updateTimeout = setTimeout(() => {
              const content = editor.innerHTML;
              if (content !== lastContent) {
                lastContent = content;
                vscode.postMessage({
                  command: 'edit',
                  content: content
                });
              }
            }, 300);
          }

          // Initialize MathJax
          function initMathJax() {
            if (window.MathJax) {
              window.MathJax = {
                ...window.MathJax,
                startup: {
                  typeset: false,
                  pageReady: function() {
                    return window.MathJax.startup.defaultPageReady().then(function() {
                      mathJaxReady = true;
                      renderMathJax();
                    });
                  }
                },
                tex: {
                  inlineMath: [['$', '$'], ['\\(', '\\)']],
                  displayMath: [['$$', '$$'], ['\\[', '\\]']],
                  processEscapes: true,
                  packages: {'[+]': ['noerrors']}
                },
                options: {
                  enableMenu: false,
                  ignoreHtmlClass: 'tex2jax_ignore',
                  processHtmlClass: 'tex2jax_process',
                  renderActions: {
                    addMenu: []
                  }
                },
                loader: {load: ['[tex]/noerrors']}
              };
            }
          }

          // Render MathJax
          function renderMathJax() {
            if (window.MathJax && mathJaxReady) {
              window.MathJax.typesetPromise().catch(err => console.error('MathJax typeset error:', err));
            }
          }

          // Initialize
          document.addEventListener('DOMContentLoaded', () => {
            initMathJax();
            
            // Handle content changes
            editor.addEventListener('input', handleContentChange);
            
            // Handle paste events to clean HTML
            editor.addEventListener('paste', (e) => {
              e.preventDefault();
              const text = (e.clipboardData || window.clipboardData).getData('text/plain');
              document.execCommand('insertText', false, text);
              handleContentChange();
            });
            
            // Handle save command
            document.addEventListener('keydown', (e) => {
              if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                const content = editor.innerHTML;
                vscode.postMessage({ 
                  command: 'save',
                  content: content 
                });
                showStatus('Saving...');
              }
            });
          });
          
          // Handle save confirmation and errors
          window.addEventListener('message', event => {
            const message = event.data;
            if (message.command === 'saved') {
              showStatus(message.success ? 'Saved' : 'Save failed');
            } else if (message.command === 'error') {
              showStatus('Error: ' + message.message, 5000);
              console.error('Webview error:', message.message);
            } else if (message.command === 'update') {
              try {
                isUpdating = true;
                editor.innerHTML = message.content;
                lastContent = message.content;
                renderMathJax();
              } finally {
                isUpdating = false;
              }
            }
          });
        </script>
      </body>
      </html>`;
  }

  private getErrorHtml(error: string): string {
    return `<!DOCTYPE html>
      <html>
      <body>
        <h1>Error</h1>
        <pre>${error}</pre>
      </body>
      </html>`;
  }

  private getNonce(): string {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
      text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
  }
}
