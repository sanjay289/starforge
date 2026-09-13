# Launch Copy

## Short Post

I built Starforge, a zero-dependency CLI that audits a GitHub repo for the signals that make open source projects easier to trust, use, and star.

It checks README quality, install and usage docs, examples, tests, CI, license, contribution docs, security policy, issue templates, and package metadata.

Try it on your repo:

```bash
pipx install starforge
starforge /path/to/repo
```

Repo: https://github.com/sanjay289/starforge

## Longer Post

Most repos do not lose stars because the code is bad. They lose them because a visitor cannot quickly answer: what does this do, can I try it, is it maintained, and can I trust it?

Starforge turns those questions into a local CLI audit. It scores a repository and prints the highest-impact fixes for improving the GitHub project page.

I built it to be dependency-free, automation-friendly, and easy to run in CI with JSON output.

Repo: https://github.com/sanjay289/starforge
