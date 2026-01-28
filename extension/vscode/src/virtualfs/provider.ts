/**
 * Virtual File System Provider
 *
 * Provides virtual documents for parsed content.
 */

import * as vscode from 'vscode';

/**
 * Provider for virtual Aletheia documents.
 */
export class AletheiaDocumentProvider implements vscode.TextDocumentContentProvider {
    private documents = new Map<string, string>();
    private _onDidChange = new vscode.EventEmitter<vscode.Uri>();

    readonly onDidChange = this._onDidChange.event;

    /**
     * Set content for a virtual document.
     */
    setContent(uri: vscode.Uri, content: string): void {
        this.documents.set(uri.toString(), content);
        this._onDidChange.fire(uri);
    }

    /**
     * Get content for a virtual document.
     */
    provideTextDocumentContent(uri: vscode.Uri): string {
        return this.documents.get(uri.toString()) || '';
    }

    /**
     * Remove a virtual document.
     */
    removeDocument(uri: vscode.Uri): void {
        this.documents.delete(uri.toString());
    }

    /**
     * Clear all virtual documents.
     */
    clear(): void {
        this.documents.clear();
    }

    /**
     * Dispose the provider.
     */
    dispose(): void {
        this._onDidChange.dispose();
        this.documents.clear();
    }
}

/**
 * Create a URI for a virtual Aletheia document.
 */
export function createAletheiaUri(documentId: string): vscode.Uri {
    return vscode.Uri.parse(`aletheia:${documentId}.md`);
}
