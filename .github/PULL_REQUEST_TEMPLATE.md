## Summary

Describe the change and the risk it addresses.

## Type

- [ ] Bug fix
- [ ] Feature
- [ ] Security hardening
- [ ] Control map / governance update
- [ ] Documentation
- [ ] Release / packaging

## SicarioSpec Checklist

- [ ] I ran `python3 -m unittest discover -s tests`
- [ ] I ran `python3 -m sicario_cli.cli verify .`
- [ ] I updated docs or recorded why docs were not impacted
- [ ] I updated data classification and tagging taxonomy when data, evidence, resources, or release assets changed
- [ ] I updated tests for behavior changes
- [ ] I updated `CHANGELOG.md` for release-visible changes
- [ ] I did not add secrets, customer data, private tenant data, or proprietary control text

## Security And Governance

- [ ] Threat model, abuse cases, or control mapping changed
- [ ] Data classification, retention, residency, sharing, or redaction changed
- [ ] Tagging taxonomy, resource tags, evidence tags, risk tags, or release tags changed
- [ ] Release/package metadata changed
- [ ] New generated artifacts or workflows were added
- [ ] No security/governance impact

## Evidence

Paste relevant command output, screenshots, or generated evidence paths.
