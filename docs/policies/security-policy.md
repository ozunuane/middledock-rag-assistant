# MiddleDock Information Security Policy

Effective: January 2026

## Password Requirements

- Minimum 14 characters
- Must include uppercase, lowercase, number, and special character
- Passwords expire every 90 days
- Cannot reuse last 12 passwords
- Multi-factor authentication (MFA) is mandatory for all accounts
- Hardware security keys (YubiKey) provided for engineering and finance teams

## Data Classification

### Public
- Marketing materials, blog posts, job listings
- No restrictions on sharing

### Internal
- Company-wide announcements, org charts, non-sensitive meeting notes
- May be shared with all employees, not externally

### Confidential
- Financial reports, customer data, employee records, source code
- Access restricted to authorized personnel
- Must be encrypted at rest and in transit
- Cannot be stored on personal devices

### Restricted
- Encryption keys, production credentials, PII of EU customers (GDPR)
- Access requires VP approval and audit logging
- Must never leave company-managed systems

## Incident Response

1. **Detect**: Report any suspected security incident to security@middledock.com within 1 hour
2. **Contain**: Security team isolates affected systems within 4 hours
3. **Investigate**: Root cause analysis within 48 hours
4. **Remediate**: Fix deployed and verified within 72 hours
5. **Report**: Incident report shared with leadership within 1 week
6. **Review**: Post-incident review meeting within 2 weeks

## Acceptable Use

- Company devices are for business use; limited personal use is acceptable
- No torrent clients, VPN bypass tools, or unauthorized software
- Browser extensions must be from approved list (maintained by IT)
- USB storage devices are disabled on all company laptops
- Personal cloud storage (Dropbox, personal Google Drive) must not be used for company data

## Vendor Security

- All vendors with access to company data must complete a security questionnaire
- SOC 2 Type II or ISO 27001 certification required for vendors handling confidential data
- Vendor access is reviewed quarterly
- Vendor contracts must include data processing agreements (DPA)

## Training

- All employees complete security awareness training within 30 days of hire
- Annual refresher training required (completion tracked in HR system)
- Engineering teams complete additional secure coding training
- Phishing simulation tests are conducted quarterly
