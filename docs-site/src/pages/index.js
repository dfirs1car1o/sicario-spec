import clsx from 'clsx';
import Heading from '@theme/Heading';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import styles from './index.module.css';

const proofPoints = [
  {
    title: 'Deterministic, code-owned verdicts',
    body: 'Pass/fail comes from sicario verify — a stdlib-only gate with no model call and no AI import. The LLM is explanation-only, structurally barred from the decision path.',
  },
  {
    title: 'A mandatory governance contract',
    body: 'Specs, plans, and tasks must contain required governance sections. Missing classification, trust boundaries, abuse cases, or AI/fleet guardrails is a hard fail, not advice.',
  },
  {
    title: 'A halting gate plus control maps',
    body: 'sicario verify blocks merge/release on violation and is wired into CI. Starter evidence maps cover 10 frameworks: CSA CCM v4.1, SOX 404 / ICFR, NIST SSDF, NIST AI RMF, ISO/IEC 27001:2022, NIST SP 800-53 Rev 5, EU AI Act, GDPR (+ CPRA), PCI DSS v4.0, and the HIPAA Security Rule.',
  },
];

const environments = ['Claude Code', 'Codex / GPT', 'GitHub Copilot', 'Generic agents'];

export default function Home() {
  return (
    <Layout
      title="Secure-by-default Spec Kit governance"
      description="SicarioSpec turns GitHub Spec Kit into a security, governance, and evidence system for AI-era software delivery."
    >
      <main>
        <section className={styles.hero}>
          <div className={styles.heroInner}>
            <div className={styles.heroCopy}>
              <p className={styles.kicker}>Spec Kit governance for AI-era delivery</p>
              <Heading as="h1" className={styles.heroTitle}>
                SicarioSpec
              </Heading>
              <p className={styles.heroSubtitle}>
                Kill risk before it ships. Give AI agents and human reviewers one shared
                workflow for classification, controls, evidence, exceptions, and release gates.
              </p>
              <div className={styles.heroActions}>
                <Link className="button button--primary button--lg" to="/docs/presets">
                  Read the docs
                </Link>
                <Link className="button button--secondary button--lg" to="https://github.com/dfirs1car1o/sicario-spec">
                  View on GitHub
                </Link>
              </div>
            </div>
            <div className={styles.signalPanel} aria-label="SicarioSpec verification flow">
              <img src="img/sicario-spec-mark.svg" alt="SicarioSpec shield and crosshair mark" className={styles.mark} />
              <img
                src="img/verify-demo.gif"
                alt="sicario verify: a passing run (exit 0) and the same feature failing with SICARIO-MISSING-THREAT-MODEL (exit 1), decided by stdlib-only code with no LLM"
                style={{ width: '100%', borderRadius: '0.5rem', margin: '1rem 0' }}
              />
              <div className={styles.flow}>
                <span>spec idea</span>
                <span>classification</span>
                <span>threat model</span>
                <span>control map</span>
                <span>evidence</span>
                <span>human gate</span>
              </div>
            </div>
          </div>
        </section>

        <section className={styles.section}>
          <div className="container">
            <div className={styles.sectionHeader}>
              <p className={styles.kicker}>What it changes</p>
              <Heading as="h2">Risk becomes delivery work.</Heading>
            </div>
            <div className={styles.grid}>
              {proofPoints.map((item) => (
                <article className={styles.card} key={item.title}>
                  <Heading as="h3">{item.title}</Heading>
                  <p>{item.body}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className={styles.section}>
          <div className="container">
            <div className={styles.sectionHeader}>
              <p className={styles.kicker}>How it differs</p>
              <Heading as="h2">Enforces, not just advises.</Heading>
            </div>
            <p style={{ maxWidth: '52rem' }}>
              SicarioSpec is not the first or only security-governance preset for Spec Kit. Most
              presets in the ecosystem follow an advisory-append pattern: they enrich the spec and
              plan with secure-SDLC guidance and regulatory notes for an agent and reviewer to
              consider. SicarioSpec operates at a different layer — a mandatory governance contract
              whose pass/fail verdict is owned by deterministic, stdlib-only code with no LLM in the
              decision path, backed by a <strong>halting</strong> verify gate (non-zero exit blocks
              the merge) and selectable control maps across 10 frameworks. The two are
              complementary: keep the advice you like, then gate the result.
            </p>
          </div>
        </section>

        <section className={clsx(styles.section, styles.band)}>
          <div className="container">
            <div className={styles.split}>
              <div>
                <p className={styles.kicker}>One command</p>
                <Heading as="h2">Bootstrap a governed target repo.</Heading>
                <p>
                  SicarioSpec installs Spec Kit presets, governance docs, risk registers,
                  evidence paths, workflows, docs-site scaffolding, and agent instructions.
                </p>
              </div>
              <pre className={styles.command}>
                <code>{'sicario init my-project --integration all --profile public-core\ncd my-project\nsicario verify'}</code>
              </pre>
            </div>
          </div>
        </section>

        <section className={styles.section}>
          <div className="container">
            <div className={styles.sectionHeader}>
              <p className={styles.kicker}>Agent environments</p>
              <Heading as="h2">Built for mixed AI delivery teams.</Heading>
            </div>
            <div className={styles.pills}>
              {environments.map((environment) => (
                <Link key={environment} className={styles.pill} to="/docs/agent-environments">
                  {environment}
                </Link>
              ))}
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
