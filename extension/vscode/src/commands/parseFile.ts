/**
 * Parse File Command
 *
 * Parses a document and displays the result.
 */

import * as vscode from 'vscode';
import { SidecarClient } from '../sidecar/client';

/**
 * Execute the parse file command.
 */
export async function parseFileCommand(client: SidecarClient): Promise<void> {
    // Get current file or prompt for selection
    let fileUri = vscode.window.activeTextEditor?.document.uri;

    if (!fileUri || !isSupportedFile(fileUri)) {
        const files = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectFolders: false,
            canSelectMany: false,
            filters: {
                'Documents': ['pdf'],
                'Images': ['png', 'jpg', 'jpeg', 'tiff']
            },
            title: 'Select a document to parse'
        });

        if (!files || files.length === 0) {
            return;
        }

        fileUri = files[0];
    }

    // Show progress
    await vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Parsing document...',
            cancellable: false
        },
        async (progress) => {
            try {
                progress.report({ increment: 0, message: 'Sending to sidecar...' });

                const result = await client.parseFile(fileUri!.fsPath);

                progress.report({ increment: 50, message: 'Processing result...' });

                // Create virtual document with parsed content
                const content = formatParsedContent(result);
                const doc = await vscode.workspace.openTextDocument({
                    content,
                    language: 'markdown'
                });

                await vscode.window.showTextDocument(doc, {
                    viewColumn: vscode.ViewColumn.Beside,
                    preview: true
                });

                progress.report({ increment: 100, message: 'Done!' });

            } catch (error) {
                vscode.window.showErrorMessage(`Failed to parse document: ${error}`);
            }
        }
    );
}

/**
 * Check if file type is supported.
 */
function isSupportedFile(uri: vscode.Uri): boolean {
    const ext = uri.fsPath.toLowerCase().split('.').pop();
    return ['pdf', 'png', 'jpg', 'jpeg', 'tiff'].includes(ext || '');
}

/**
 * Format parsed content for display.
 */
function formatParsedContent(result: any): string {
    const lines: string[] = [];

    lines.push(`# Parsed Document: ${result.document_id || 'Unknown'}`);
    lines.push('');
    lines.push(`*Parsed at: ${new Date().toISOString()}*`);
    lines.push('');

    if (result.pages) {
        for (const page of result.pages) {
            lines.push(`## Page ${page.page_number}`);
            lines.push('');

            for (const block of page.blocks || []) {
                if (block.type === 'heading') {
                    lines.push(`### ${block.text}`);
                } else {
                    lines.push(block.text);
                }
                lines.push('');
            }

            if (page.tables && page.tables.length > 0) {
                lines.push('### Tables');
                for (const table of page.tables) {
                    lines.push('```');
                    lines.push(table.csv || JSON.stringify(table.cells));
                    lines.push('```');
                    lines.push('');
                }
            }
        }
    }

    return lines.join('\n');
}
