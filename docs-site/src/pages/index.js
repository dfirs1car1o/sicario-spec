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
    body: 'sicario verify blocks merge/release on violation and is wired into CI. Starter evidence maps cover 11 frameworks: CSA CCM v4.1, SOX 404 / ICFR, NIST SSDF, NIST AI RMF, ISO/IEC 27001:2022, NIST SP 800-53 Rev 5, EU AI Act, GDPR (+ CPRA), PCI DSS v4.0, HIPAA Security Rule, and OWASP ASVS.',
  },
  {
    title: 'Security Evidence Chain',
    body: 'Risks and decisions trace to controls, tests, gates, evidence paths, owners, reviewers, and approval or accepted-risk states.',
  },
];

const environments = ['Claude Code', 'Codex / GPT', 'GitHub Copilot', 'Generic agents'];

const currentSurface = [
  {
    metric: '11',
    label: 'preset manifests',
    body: 'Composable Spec Kit profiles for core governance, docs, appsec, AI systems, agent fleets, cloud/IaC, security tooling, supply chain, compliance, SaaS, and enterprise-strict delivery.',
  },
  {
    metric: '16',
    label: 'shipped verify rules',
    body: 'Default `.rule.json` gates cover files, sections, keywords, forbidden patterns, required regexes, risk rows, classification, tagging, AI guardrails, and fleet guardrails.',
  },
  {
    metric: '11',
    label: 'control maps',
    body: 'Starter maps connect SicarioSpec evidence to CCM, SOX, SSDF, AI RMF, ISO 27001, NIST 800-53, EU AI Act, GDPR/CPRA, PCI DSS, HIPAA, and OWASP ASVS.',
  },
  {
    metric: '8',
    label: 'guard commands',
    body: 'Spec Kit extension commands cover init, assess, threat modeling, controls, evidence, verify, review, and apply-findings workflows.',
  },
];

const ruleFlow = [
  'load `.sicario/rules/*.rule.json`',
  'validate required fields and kind-specific params',
  'dispatch to fixed evaluator modules',
  'emit named findings with severity and path',
  'write gate evidence under `generated/sicario/`',
  'exit non-zero when required evidence is missing',
];

const maintainerTracks = [
  {
    title: 'Custom rule example',
    body: 'A contributor-owned issue is reserved for `examples/custom-rules/`, proving external teams can add rules without Python changes.',
    to: 'https://github.com/dfirs1car1o/sicario-spec/issues/32',
  },
  {
    title: 'Additional control map',
    body: 'A contributor-owned issue is reserved for SOC 2, FedRAMP, or BSI C5 coverage, expanding the standards evidence surface.',
    to: 'https://github.com/dfirs1car1o/sicario-spec/issues/31',
  },
];

const usePaths = [
  {
    label: 'Catalog path',
    title: 'Use the preset',
    body: 'Install sicario-core with Spec Kit when you want the smallest upstream-compatible governance layer.',
    command: 'specify preset add --dev /path/to/sicario-core',
    to: '/docs/getting-started#use-the-full-spec-kit-bundle',
  },
  {
    label: 'Full bundle',
    title: 'Bootstrap a repo',
    body: 'Use the SicarioSpec CLI when you want docs, risk registers, workflows, control maps, and verification.',
    command: 'sicario init my-project --integration all --profile public-core',
    to: '/docs/getting-started#use-the-full-sicariospec-cli',
  },
  {
    label: 'Review loop',
    title: 'Verify evidence',
    body: 'Run deterministic checks so missing security evidence is visible before release approval.',
    command: 'sicario verify',
    to: '/docs/getting-started#daily-operating-loop',
  },
];

export default function Home() {
  return (
    <Layout
      title="Evidence-first Spec Kit governance"
      description="SicarioSpec turns GitHub Spec Kit into an evidence-first security operations governance system for AI-era software delivery."
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
                workflow for classification, trust boundaries, controls, gates, evidence
                paths, owners, and release approval.
              </p>
              <div className={styles.heroActions}>
                <Link className="button button--primary button--lg" to="/docs/getting-started">
                  Start using it
                </Link>
                <Link className="button button--secondary button--lg" to="https://github.com/dfirs1car1o/sicario-spec">
                  View on GitHub
                </Link>
              </div>
            </div>
            <div className={styles.signalPanel} aria-label="SicarioSpec verification flow">
              <img src="img/sicario-spec-mark.svg" alt="SicarioSpec canteen mark" className={styles.mark} />
              <div className={styles.flow}>
                <span>feature intent</span>
                <span>classification</span>
                <span>trust boundary</span>
                <span>abuse case</span>
                <span>control gate</span>
                <span>evidence owner</span>
                <span>approval state</span>
              </div>
            </div>
          </div>
        </section>

        <section className={styles.section}>
          <div className="container">
            <div className={styles.sectionHeader}>
              <p className={styles.kicker}>How to use it</p>
              <Heading as="h2">Pick the operating mode first.</Heading>
            </div>
            <div className={styles.pathGrid}>
              {usePaths.map((item) => (
                <Link className={styles.pathCard} to={item.to} key={item.title}>
                  <span>{item.label}</span>
                  <Heading as="h3">{item.title}</Heading>
                  <p>{item.body}</p>
                  <code>{item.command}</code>
                </Link>
              ))}
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
              <p className={styles.kicker}>Current bundle surface</p>
              <Heading as="h2">Version 0.5.1 is more than a template pack.</Heading>
              <p className={styles.readableText}>
                The bundle now combines Spec Kit presets, a Python CLI, declarative verify
                rules, framework maps, release assets, Docusaurus documentation, GitHub
                workflows, and maintainer operations. The open contribution queue is intentionally
                small: two assigned issues that should arrive as reviewable PRs.
              </p>
            </div>
            <div className={styles.metricGrid}>
              {currentSurface.map((item) => (
                <article className={styles.metricCard} key={item.label}>
                  <strong>{item.metric}</strong>
                  <span>{item.label}</span>
                  <p>{item.body}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className={clsx(styles.section, styles.band)}>
          <div className="container">
            <div className={styles.split}>
              <div>
                <p className={styles.kicker}>Declarative verification</p>
                <Heading as="h2">Custom gates are JSON files, not Python forks.</Heading>
                <p>
                  SicarioSpec 0.5.1 loads `*.rule.json` files, validates their schema,
                  and runs fixed evaluator modules. A project can add, override, or disable
                  a governance gate in `.sicario/rules/` while keeping the same deterministic
                  pass/fail path in CI.
                </p>
                <Link className={styles.inlineLink} to="/docs/rule-engine">
                  Read the rule engine docs
                </Link>
              </div>
              <ol className={styles.flowList}>
                {ruleFlow.map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ol>
            </div>
          </div>
        </section>

        <section className={styles.section}>
          <div className="container">
            <div className={styles.sectionHeader}>
              <p className={styles.kicker}>How it differs</p>
              <Heading as="h2">Enforces, not just advises.</Heading>
            </div>
            <p className={styles.readableText}>
              SicarioSpec is not the first or only security-governance preset for Spec Kit. Most
              presets in the ecosystem follow an advisory-append pattern: they enrich the spec and
              plan with secure-SDLC guidance and regulatory notes for an agent and reviewer to
              consider. SicarioSpec operates at a different layer — a mandatory governance contract
              whose pass/fail verdict is owned by deterministic, stdlib-only code with no LLM in the
              decision path, backed by a <strong>halting</strong> verify gate (non-zero exit blocks
              the merge) and selectable control maps across 11 frameworks. The two are
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
                  Security Evidence Chain templates, workflows, docs-site scaffolding, and
                  agent instructions.
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

        <section className={styles.section}>
          <div className="container">
            <div className={styles.sectionHeader}>
              <p className={styles.kicker}>Maintainer queue</p>
              <Heading as="h2">Clean enough to wait for contributor PRs.</Heading>
              <p className={styles.readableText}>
                The repo should stay in a boring state: green checks, current docs, no stale
                triage labels, and only scoped community issues waiting for review. These two
                public tracks are the next bundle-expansion points.
              </p>
            </div>
            <div className={styles.pathGrid}>
              {maintainerTracks.map((item) => (
                <Link className={styles.pathCard} to={item.to} key={item.title}>
                  <span>Open contribution track</span>
                  <Heading as="h3">{item.title}</Heading>
                  <p>{item.body}</p>
                  <code>{item.to.replace('https://github.com/dfirs1car1o/sicario-spec/', '')}</code>
                </Link>
              ))}
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
