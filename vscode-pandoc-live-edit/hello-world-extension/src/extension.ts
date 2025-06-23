import * as vscode from "vscode";
import * as cp from "child_process";

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.window.registerCustomEditorProvider(
      "pandoc-wysiwyg.editor",
      new PandocCustomEditor(context),
      { supportsMultipleEditorsPerDocument: false }
    )
  );
}

class PandocCustomEditor implements vscode.CustomTextEditorProvider {
  constructor(private readonly context: vscode.ExtensionContext) {}

  async resolveCustomTextEditor(
    document: vscode.TextDocument,
    webviewPanel: vscode.WebviewPanel,
    _token: vscode.CancellationToken
  ): Promise<void> {
    webviewPanel.webview.options = {
      enableScripts: true,
      localResourceRoots: []
    };

    const updateWebview = () => {
      const md = document.getText();
      this.convertMarkdownToHtml(md)
        .then((html) => {
          webviewPanel.webview.html = this.getHtmlForWebview(html, webviewPanel.webview);
        })
        .catch((err) => {
          webviewPanel.webview.html = `<body><pre>Error running Pandoc:\n${err}</pre></body>`;
        });
    };

    updateWebview();

    const changeDocumentSubscription = vscode.workspace.onDidChangeTextDocument(e => {
      if (e.document.uri.toString() === document.uri.toString()) {
        updateWebview();
      }
    });

    webviewPanel.onDidDispose(() => {
      changeDocumentSubscription.dispose();
    });

    webviewPanel.webview.onDidReceiveMessage(message => {
      switch (message.command) {
        case 'alert':
          vscode.window.showInformationMessage(message.text);
          break;
      }
    });
  }

  private convertMarkdownToHtml(md: string): Promise<string> {
    return new Promise((resolve, reject) => {
      const pandoc = cp.spawn("pandoc", [
        "--from=markdown+sourcepos",
        "--to=html",
        "--mathjax"
      ]);

      let stdout = "";
      let stderr = "";

      pandoc.stdout.on("data", (chunk) => (stdout += chunk));
      pandoc.stderr.on("data", (chunk) => (stderr += chunk));

      pandoc.on("close", (code) => {
        if (code === 0) {
          resolve(stdout);
        } else {
          reject(stderr || `Pandoc exited with code ${code}`);
        }
      });

      pandoc.stdin.write(md);
      pandoc.stdin.end();
    });
  }

  private getHtmlForWebview(htmlBody: string, webview: vscode.Webview): string {
    const mathjaxCdn = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js";

    return `<!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline' https:; style-src 'unsafe-inline' https:;" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <script src="${mathjaxCdn}"></script>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; padding: 1rem; }
          div.theorem { border-left: 3px solid #007acc; padding-left: 1em; margin: 1em 0; background-color: #f0f8ff; }
        </style>
      </head>
      <body>
        ${htmlBody}
      </body>
      </html>`;
  }
}
