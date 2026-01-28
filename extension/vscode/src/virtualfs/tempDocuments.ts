/**
 * Temporary Documents
 *
 * Manages temporary documents for parsed content.
 */

import * as vscode from 'vscode';

interface TempDocument {
    uri: vscode.Uri;
    documentId: string;
    createdAt: Date;
    content: string;
}

const tempDocuments = new Map<string, TempDocument>();

/**
 * Create a temporary document with parsed content.
 */
export async function createTempDocument(
    documentId: string,
    content: string
): Promise<vscode.TextDocument> {
    // Create untitled document
    const doc = await vscode.workspace.openTextDocument({
        content,
        language: 'markdown'
    });

    // Track it
    tempDocuments.set(documentId, {
        uri: doc.uri,
        documentId,
        createdAt: new Date(),
        content
    });

    return doc;
}

/**
 * Get a temporary document.
 */
export function getTempDocument(documentId: string): TempDocument | undefined {
    return tempDocuments.get(documentId);
}

/**
 * Remove a temporary document.
 */
export function removeTempDocument(documentId: string): void {
    tempDocuments.delete(documentId);
}

/**
 * Clear all temporary documents.
 */
export function clearTempDocuments(): void {
    tempDocuments.clear();
}

/**
 * Get all temporary document IDs.
 */
export function getTempDocumentIds(): string[] {
    return Array.from(tempDocuments.keys());
}
