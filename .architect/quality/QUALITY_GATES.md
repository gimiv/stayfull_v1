# 🚦 Quality Gates - Automated Enforcement

## 🔴 RED FLAGS (Stop Everything)
- [ ] Tests failing
- [ ] Coverage below 80%
- [ ] Security vulnerability found
- [ ] Performance regression >20%
- [ ] Build broken

## 🟡 YELLOW FLAGS (Need Attention)
- [ ] Coverage below 90%
- [ ] TODO count > 10
- [ ] Duplicate code detected
- [ ] Complex function (cyclomatic > 10)
- [ ] Missing documentation

## 🟢 GREEN FLAGS (Good to Go)
- [x] All tests passing
- [x] Coverage > 90%
- [x] Security scan clean
- [x] Performance acceptable
- [x] Documentation complete

## 📋 Pre-Commit Checklist
```bash
✓ Tests pass: npm test
✓ Lint clean: npm run lint
✓ Types valid: npm run type-check
✓ Coverage good: npm run coverage
✓ Security scan: npm audit
```

## 📋 Pre-Feature Checklist
- [ ] Specification written
- [ ] Tests written FIRST
- [ ] Implementation complete
- [ ] Documentation updated
- [ ] Code reviewed by Claude
- [ ] Performance tested

## 📋 Pre-Deployment Checklist
- [ ] All features tested
- [ ] Security audit passed
- [ ] Performance benchmarked
- [ ] Rollback plan ready
- [ ] Monitoring configured
- [ ] Documentation complete
