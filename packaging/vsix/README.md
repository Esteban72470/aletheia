# VS Code Extension Packaging (VSIX)

This directory contains resources for packaging the Aletheia VS Code extension.

## Building the VSIX

```bash
cd extension/vscode
npm run package
```

The `.vsix` file will be generated in this directory.

## Publishing

1. Create a Personal Access Token (PAT) on Azure DevOps
2. Login to vsce: `vsce login <publisher>`
3. Publish: `vsce publish`

## Local Installation

```bash
code --install-extension aletheia-*.vsix
```

## Files

- `aletheia-<version>.vsix` - Built extension package (gitignored)
- Build artifacts are placed here during CI/CD
