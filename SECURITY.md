# Security Policy

## Supported Versions

The following versions of `feu` are currently being supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.5.x   | :white_check_mark: |
| 0.4.x   | :white_check_mark: |
| < 0.4   | :x:                |

## Reporting a Vulnerability

We take the security of `feu` seriously. If you believe you have found a security vulnerability, please report it to us responsibly.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by emailing:

- **Email**: durand.tibo+gh@gmail.com

Please include the following information in your report:

1. A description of the vulnerability
2. Steps to reproduce the issue
3. Potential impact of the vulnerability
4. Any possible mitigations you've identified
5. Your contact information for follow-up questions

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours.
- **Communication**: We will keep you informed about our progress toward fixing the vulnerability.
- **Credit**: If you wish, we will publicly credit you for the responsible disclosure after the issue is resolved.
- **Timeline**: We aim to address critical vulnerabilities within 7 days and other vulnerabilities within 30 days.

## Security Best Practices

When using `feu`, we recommend following these best practices:

1. **Keep dependencies updated**: Regularly update `feu` and its dependencies to get the latest security patches.
   ```bash
   pip install --upgrade feu
   ```

2. **Use virtual environments**: Always use virtual environments to isolate your project dependencies.

3. **Review package sources**: When using `feu` to install packages, ensure you trust the package sources.

4. **Validate versions**: Use `feu`'s version checking features to ensure you're installing compatible and tested versions.

5. **Monitor advisories**: Subscribe to security advisories for packages in your dependency tree.

## Security Features in feu

`feu` includes several features that can help improve your security posture:

- **Version validation**: Ensures you're using tested and compatible package versions
- **Minimal dependencies**: Core functionality requires only the `packaging` library
- **No network access required**: Core features work offline (network features are optional)

## Disclosure Policy

When we receive a security report, we will:

1. Confirm the vulnerability and determine its impact
2. Develop a fix and test it thoroughly
3. Prepare a security advisory
4. Release a patched version
5. Publicly disclose the vulnerability details after users have had time to update

## Comments on This Policy

If you have suggestions on how this process could be improved, please submit a pull request or open an issue to discuss.

## Attribution

This security policy is adapted from best practices in the open-source community.
