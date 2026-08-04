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
  'spec-authoring',
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

// The lesson path (maintainer feedback 2026-07-31; count set by curriculum
// analysis, not by fiat): six lessons. Lessons 5 and 6 are promoted because
// the product's own thesis (spec 004) is that the gate checks vocabulary and
// the HUMAN supplies substance — a path ending at "green in CI" trains
// people to trust exactly the signal the docs say not to trust alone.
// Everything else is task-shaped under "When you need it".
const LESSONS_LABEL = 'Start Here — Six Lessons';
const LESSONS = [
  { id: 'guides/start-here', label: 'Start here: six lessons' },
  { id: 'guides/getting-started', label: 'Lesson 1 · Install, reach a green gate' },
  { id: 'playbooks/initial-setup-selection', label: 'Lesson 2 · Choose your profile' },
  { id: 'playbooks/first-spec', label: 'Lesson 3 · Write your first spec' },
  { id: 'playbooks/wire-ci', label: 'Lesson 4 · Put the gate in CI' },
  { id: 'playbooks/spec-authoring', label: 'Lesson 5 · Write a spec worth reviewing' },
  { id: 'playbooks/read-evidence-as-reviewer', label: 'Lesson 6 · Review a gate you did not run' },
];
const lessonIds = new Set(LESSONS.map((l) => l.id));
const lessonItems = LESSONS.filter((l) =>
  [...guideItems, ...playbookItems].includes(l.id)
).map((l) => ({ type: 'doc', id: l.id, label: l.label }));

// Advanced Track (spec 008 FR-001/FR-002): an optional level ABOVE the six
// lessons, published as its own collapsed category between the lesson path
// and 'When You Need It' so the six-lesson path stays visually primary. The
// six-lesson path, its count, and its stated time budget are unchanged.
const ADVANCED_LABEL = 'Advanced Track — Graph & Loop Engineering';
const ADVANCED = [
  { id: 'guides/advanced-track', label: 'Advanced Track: start here' },
  { id: 'playbooks/graph-engineering', label: 'Advanced 1 · Graph engineering' },
  { id: 'playbooks/loop-engineering', label: 'Advanced 2 · Loop engineering' },
];
const advancedIds = new Set(ADVANCED.map((a) => a.id));
const advancedItems = ADVANCED.filter((a) =>
  [...guideItems, ...playbookItems].includes(a.id)
).map((a) => ({ type: 'doc', id: a.id, label: a.label }));

// FR-003 (the computed-complement trap): 'When You Need It' is the COMPLEMENT
// of the curated categories, so any id that is not excluded here appears
// twice in the sidebar. Both the lesson ids and the advanced-track ids must
// be subtracted; tests/test_advanced_track_docs.py asserts each of the three
// new ids appears exactly once across the whole structure.
const whenNeededItems = [...guideItems, ...playbookItems].filter(
  (id) => !lessonIds.has(id) && !advancedIds.has(id)
);

const learningSections = [
  ...(lessonItems.length ? [[LESSONS_LABEL, lessonItems]] : []),
  ...(advancedItems.length ? [[ADVANCED_LABEL, advancedItems]] : []),
  ...(whenNeededItems.length ? [['When You Need It', whenNeededItems]] : []),
];

const docSections = [
  [
    'Overview & Reference',
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

// Learning categories come FIRST (the old 'Start Here' reference category
// is now 'Overview & Reference') and stay expanded — they are the new-user path.
const allSections = [...learningSections, ...docSections];

const EXPANDED = new Set([LESSONS_LABEL, 'When You Need It']);

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
