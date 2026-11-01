# Publish StockMind to GitHub

The project package is prepared locally but is not yet published to a GitHub account.

1. Sign in to GitHub and create a new empty repository named `StockMind`.
2. Do not initialize it with a README or license because this project already contains those files.
3. Open the StockMind folder in VS Code and open Terminal.
4. Run:

```powershell
git init
git add .
git status
```

5. Before committing, confirm that no `data/keys/*_private.pem` file is listed. The `.gitignore` excludes private keys.
6. Commit and connect to the repository URL shown by GitHub:

```powershell
git commit -m "Initial StockMind autonomous agent project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/StockMind.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. Do not paste a password or access token into source code. If Git asks for authentication, use GitHub's supported sign-in flow.

After pushing, copy the real repository URL into the assignment submission form. Do not submit the placeholder URL above.
