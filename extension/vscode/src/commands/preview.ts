/**
 * Preview Command
 *
 * Shows a visual preview of parsed documents with overlays.
 */

import * as vscode from 'vscode';
import { SidecarClient } from '../sidecar/client';
import { createWebviewContent } from '../webview/renderer';

/**
 * Execute the preview command.
 */
export async function previewCommand(
    context: vscode.ExtensionContext,
    client: SidecarClient
): Promise<void> {
    // Get current file
    const fileUri = vscode.window.activeTextEditor?.document.uri;

    if (!fileUri) {
        vscode.window.showWarningMessage('No file selected for preview');
        return;
    }

    // Create webview panel
    const panel = vscode.window.createWebviewPanel(
        'aletheiaPreview',
        `Aletheia: ${fileUri.fsPath.split(/[\\/]/).pop()}`,
        vscode.ViewColumn.Beside,
        {
            enableScripts: true,
            retainContextWhenHidden: true,
            localResourceRoots: [
                vscode.Uri.joinPath(context.extensionUri, 'media')
            ]
        }
    );

    // Show loading
    panel.webview.html = getLoadingHtml();

    try {
        // Parse document
        const result = await client.parseFile(fileUri.fsPath);

        // Render preview
        panel.webview.html = createWebviewContent(result, panel.webview, context.extensionUri);

        // Handle messages from webview
        panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.command) {
                    case 'insertBlock':
                        await insertBlockToEditor(message.text);
                        break;
                    case 'copyBlock':
                        await vscode.env.clipboard.writeText(message.text);
                        vscode.window.showInformationMessage('Block copied to clipboard');
                        break;
                }
            },
            undefined,
            context.subscriptions
        );

    } catch (error) {
        panel.webview.html = getErrorHtml(String(error));
    }
}

/**
 * Insert text into the active editor.
 */
async function insertBlockToEditor(text: string): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (editor) {
        await editor.edit((editBuilder) => {
            editBuilder.insert(editor.selection.active, text);
        });
    }
}

/**
 * Get loading HTML.
 */
function getLoadingHtml(): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { display: flex; justify-content: center; align-items: center; height: 100vh; }
                .loading { font-size: 1.2em; color: var(--vscode-foreground); }
            </style>
        </head>
        <body>
            <div class="loading">Loading preview...</div>
        </body>
        </html>
    `;
}

/**
 * Get error HTML.
 */
function getErrorHtml(error: string): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { padding: 20px; color: var(--vscode-foreground); }
                .error { color: var(--vscode-errorForeground); }
            </style>
        </head>
        <body>
            <h2>Error</h2>
            <p class="error">${error}</p>
        </body>
        </html>
    `;
}
