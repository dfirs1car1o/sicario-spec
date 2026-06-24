// @ts-check

const docSections = [
  ['Start Here', ['getting-started', 'architecture', 'profiles', 'presets', 'rule-engine']],
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

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docs: docSections.map(([label, items]) => ({
    type: 'category',
    label,
    collapsed: label !== 'Start Here' && label !== 'Security Evidence Chain',
    items,
  })),
};

module.exports = sidebars;
