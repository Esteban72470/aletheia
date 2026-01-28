/**
 * Insert Block Command
 *
 * Inserts a selected block from parsed content into the editor.
 */

import * as vscode from 'vscode';

// Store for selected blocks from preview
let selectedBlock: string | undefined;

/**
 * Set the selected block from preview.
 */
export function setSelectedBlock(text: string): void {
    selectedBlock = text;
}

/**
 * Get the selected block.
 */
export function getSelectedBlock(): string | undefined {
    return selectedBlock;
}

/**
 * Clear the selected block.
 */
export function clearSelectedBlock(): void {
    selectedBlock = undefined;
}

/**
 * Execute the insert block command.
 */
export async function insertBlockCommand(): Promise<void> {
    const editor = vscode.window.activeTextEditor;

    if (!editor) {
        vscode.window.showWarningMessage('No active editor');
        return;
    }

    if (!selectedBlock) {
        // Prompt for text if no block selected
        const text = await vscode.window.showInputBox({
            prompt: 'Enter text to insert',
            placeHolder: 'Paste or type content...'
        });

        if (!text) {
            return;
        }

        await insertText(editor, text);
    } else {
        await insertText(editor, selectedBlock);
        clearSelectedBlock();
    }
}

/**
 * Insert text at cursor position.
 */
async function insertText(editor: vscode.TextEditor, text: string): Promise<void> {
    await editor.edit((editBuilder) => {
        editBuilder.insert(editor.selection.active, text);
    });

    vscode.window.showInformationMessage('Block inserted');
}
