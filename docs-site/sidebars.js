// @ts-check

const fs = require('fs');
const path = require('path');

// Learning content (spec 007): docs/guides/ and docs/playbooks/ are a distinct
// learning category, separate from reference material (FR-021). The item lists
// are derived from the files actually present so the site build (which throws
// on unresolved sidebar ids) stays green while the guide set lands
// incrementally. Preferred order first; any additional pages follow
// alphabetically. Convention: pages keep filename-derived doc ids (no custom
// `id`/`slug` front matter).
const DOCS_ROOT = path.join(__dirname, '..', 'docs');

function presentDocs(subdir, preferredOrder) {
  const dir = path.join(DOCS_ROOT, subdir);
  if (!fs.existsSync(dir)) return [];
  const present = fs
    .readdirSync(dir)
    .filter((name) => name.endsWith('.md') || name.endsWith('.mdx'))
    .map((name) => name.replace(/\.mdx?$/, ''));
  const ordered = preferredOrder.filter((slug) => present.includes(slug));
  const rest = present.filter((slug) => !preferredOrder.includes(slug)).sort();
  return [...ordered, ...rest].map((slug) => `${subdir}/${slug}`);
}

// FR-010 playbook set, in the spec's enumeration order (slugs appear as the
// files land; absent ones are simply not listed yet).
const PLAYBOOK_ORDER = [
  'initial-setup-selection',
  'brownfield-adoption',
  'first-spec',
  'author-a-passing-spec',
  'custom-rule',
  'override-shipped-rule',
  'investigate-failing-gate',
  'select-frameworks',
  'wire-ci',
  'read-evidence-as-reviewer',
];

const GUIDE_ORDER = ['getting-started'];

const guideItems = presentDocs('guides', GUIDE_ORDER);
const playbookItems = presentDocs('playbooks', PLAYBOOK_ORDER);

const learningSections = [
  ...(guideItems.length ? [['Guides', guideItems]] : []),
  ...(playbookItems.length ? [['Playbooks', playbookItems]] : []),
];

const docSections = [
  [
    'Start Here',
    ['getting-started', 'bundle-walkthrough', 'architecture', 'profiles', 'presets', 'rule-engine'],
  ],
  [
    'Security Evidence Chain',
    [
      'security-model',
      'governance/data-classification',
      'governance/tagging-taxonomy',
      'security/threat-model',
      'security/abuse-cases',
      'control-maps',
      'compliance/evidence-index',
      'risk/risk-register',
      'risk/security-exceptions',
      'risk/accepted-risk-log',
    ],
  ],
  [
    'Delivery Workflows',
    [
      'agent-environments',
      'agent-fleet',
      'machine-user-pr-flow',
      'docs-and-diagrams',
      'docs-impact',
      'repository-settings',
    ],
  ],
  [
    'Assurance Profiles',
    [
      'cloud-iac',
      'openssf',
      'vendor-evaluation',
      'compliance/control-applicability',
      'completeness-matrix',
    ],
  ],
  [
    'Project Operations',
    [
      'extensions',
      'bundle-readiness',
      'catalog-submission',
      'release-process',
      'adoption-and-launch',
      'architecture/system-context',
    ],
  ],
];

// Learning categories sit right after Start Here, before the reference
// sections, and stay expanded — they are the new-user path.
const allSections = [docSections[0], ...learningSections, ...docSections.slice(1)];

const EXPANDED = new Set(['Start Here', 'Guides', 'Playbooks', 'Security Evidence Chain']);

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docs: allSections.map(([label, items]) => ({
    type: 'category',
    label,
    collapsed: !EXPANDED.has(label),
    items,
  })),
};

module.exports = sidebars;
