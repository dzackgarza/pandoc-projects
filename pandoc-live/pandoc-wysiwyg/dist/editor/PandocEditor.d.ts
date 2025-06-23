import * as vscode from 'vscode';
/**
 * Implements a WYSIWYG Markdown editor using Pandoc for conversion
 */
export declare class PandocEditor implements vscode.CustomTextEditorProvider {
    private readonly context;
    static readonly viewType = "pandoc-wysiwyg.editor";
    private isUpdating;
    private documentChangeListener;
    constructor(context: vscode.ExtensionContext);
    /**
     * Register the editor with VS Code
     */
    static register(context: vscode.ExtensionContext): vscode.Disposable;
    /**
     * Called when the editor is opened
     */
    resolveCustomTextEditor(document: vscode.TextDocument, webviewPanel: vscode.WebviewPanel, _token: vscode.CancellationToken): Promise<void>;
    /**
     * Set up message handlers for communication with the webview
     */
    private setupMessageHandlers;
    /**
     * Update the document with new content from the webview
     */
    private updateDocument;
    /**
     * Update the webview with the current document content
     */
    private updateWebview;
    /**
     * Generate the complete HTML for the webview
     */
    private getWebviewContent;
    /**
     * Generate an error view for when rendering fails
     */
    private getErrorView;
    /**
     * Generate a nonce for CSP
     */
    private getNonce;
}
