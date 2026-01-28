/**
 * Webview Renderer
 *
 * Generates HTML content for the preview webview.
 */

import * as vscode from 'vscode';

/**
 * Create webview HTML content.
 */
export function createWebviewContent(
    result: any,
    webview: vscode.Webview,
    extensionUri: vscode.Uri
): string {
    const styleUri = webview.asWebviewUri(
        vscode.Uri.joinPath(extensionUri, 'media', 'styles.css')
    );

    return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'unsafe-inline';">
            <link href="${styleUri}" rel="stylesheet">
            <title>Aletheia Preview</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                    padding: 20px;
                }
                .page {
                    border: 1px solid var(--vscode-panel-border);
                    margin-bottom: 20px;
                    padding: 15px;
                    border-radius: 4px;
                }
                .page-header {
                    font-weight: bold;
                    margin-bottom: 10px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid var(--vscode-panel-border);
                }
                .block {
                    padding: 8px;
                    margin: 4px 0;
                    background-color: var(--vscode-editor-inactiveSelectionBackground);
                    border-radius: 4px;
                    cursor: pointer;
                }
                .block:hover {
                    background-color: var(--vscode-editor-selectionBackground);
                }
                .block-heading {
                    font-size: 1.2em;
                    font-weight: bold;
                }
                .block-actions {
                    float: right;
                }
                .block-actions button {
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 4px 8px;
                    margin-left: 4px;
                    cursor: pointer;
                    border-radius: 2px;
                }
                .block-actions button:hover {
                    background: var(--vscode-button-hoverBackground);
                }
                .confidence {
                    font-size: 0.8em;
                    color: var(--vscode-descriptionForeground);
                }
                .table-container {
                    overflow-x: auto;
                    margin: 10px 0;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                }
                th, td {
                    border: 1px solid var(--vscode-panel-border);
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: var(--vscode-editor-inactiveSelectionBackground);
                }
            </style>
        </head>
        <body>
            <h1>Document Preview</h1>
            <p>Document ID: ${result.document_id || 'Unknown'}</p>
            ${renderPages(result.pages || [])}
            <script>
                const vscode = acquireVsCodeApi();

                function insertBlock(text) {
                    vscode.postMessage({ command: 'insertBlock', text: text });
                }

                function copyBlock(text) {
                    vscode.postMessage({ command: 'copyBlock', text: text });
                }
            </script>
        </body>
        </html>
    `;
}

/**
 * Render pages HTML.
 */
function renderPages(pages: any[]): string {
    return pages.map(page => `
        <div class="page">
            <div class="page-header">Page ${page.page_number}</div>
            ${renderBlocks(page.blocks || [])}
            ${renderTables(page.tables || [])}
        </div>
    `).join('');
}

/**
 * Render blocks HTML.
 */
function renderBlocks(blocks: any[]): string {
    return blocks.map(block => `
        <div class="block ${block.type === 'heading' ? 'block-heading' : ''}"
             onclick="this.classList.toggle('selected')">
            <div class="block-actions">
                <button onclick="insertBlock('${escapeHtml(block.text)}')">Insert</button>
                <button onclick="copyBlock('${escapeHtml(block.text)}')">Copy</button>
            </div>
            <div class="block-text">${escapeHtml(block.text)}</div>
            <div class="confidence">Confidence: ${(block.confidence * 100).toFixed(1)}%</div>
        </div>
    `).join('');
}

/**
 * Render tables HTML.
 */
function renderTables(tables: any[]): string {
    return tables.map(table => `
        <div class="table-container">
            <table>
                ${(table.cells || []).map((row: string[], i: number) => `
                    <tr>
                        ${row.map(cell => i === 0 ? `<th>${escapeHtml(cell)}</th>` : `<td>${escapeHtml(cell)}</td>`).join('')}
                    </tr>
                `).join('')}
            </table>
        </div>
    `).join('');
}

/**
 * Escape HTML entities.
 */
function escapeHtml(text: string): string {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
