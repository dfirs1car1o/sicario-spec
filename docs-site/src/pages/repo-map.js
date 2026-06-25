import {useMemo, useState} from 'react';
import PropTypes from 'prop-types';
import Heading from '@theme/Heading';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import repoMap from '../generated/repo-map.json';
import styles from './repo-map.module.css';

const personaLabels = {
  all: 'All',
  contributor: 'Contributors',
  maintainer: 'Maintainers',
  reviewer: 'Reviewers',
  user: 'Users',
};

const mapNodeShape = PropTypes.shape({
  id: PropTypes.string.isRequired,
  kind: PropTypes.string.isRequired,
  path: PropTypes.string.isRequired,
  summary: PropTypes.string.isRequired,
  tags: PropTypes.arrayOf(PropTypes.string).isRequired,
  title: PropTypes.string.isRequired,
});

const mapGroupShape = PropTypes.shape({
  count: PropTypes.number.isRequired,
  nodes: PropTypes.arrayOf(mapNodeShape).isRequired,
  persona: PropTypes.string.isRequired,
  summary: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  tone: PropTypes.string.isRequired,
});

function githubUrl(path) {
  const name = path.split('/').pop() ?? path;
  const route = name.includes('.') ? 'blob' : 'tree';
  return `https://github.com/dfirs1car1o/sicario-spec/${route}/main/${path}`;
}

function normalize(value) {
  return value.toLowerCase();
}

function matchesQuery(group, node, query) {
  if (!query) {
    return true;
  }
  const haystack = [
    group.title,
    group.summary,
    group.persona,
    node.title,
    node.path,
    node.kind,
    node.summary,
    ...node.tags,
  ]
    .join(' ')
    .toLowerCase();
  return haystack.includes(query);
}

function matchesPersona(group, node, persona) {
  return (
    persona === 'all' ||
    group.persona === persona ||
    node.tags.includes(persona)
  );
}

function Branch({group, selectedId = null, onSelect}) {
  return (
    <section className={styles.branch} data-tone={group.tone}>
      <div className={styles.branchHeader}>
        <span>{group.persona}</span>
        <strong>{group.count}</strong>
      </div>
      <Heading as="h2">{group.title}</Heading>
      <p>{group.summary}</p>
      <div className={styles.leafList}>
        {group.nodes.map((node) => (
          <button
            aria-pressed={selectedId === node.id}
            className={styles.leaf}
            key={node.id}
            onClick={() => onSelect(node.id)}
            type="button"
          >
            <span>{node.kind}</span>
            <strong>{node.title}</strong>
            <small>{node.path}</small>
          </button>
        ))}
      </div>
    </section>
  );
}

Branch.propTypes = {
  group: mapGroupShape.isRequired,
  onSelect: PropTypes.func.isRequired,
  selectedId: PropTypes.string,
};

function DetailPanel({node = null}) {
  if (!node) {
    return (
      <aside className={styles.detailPanel}>
        <p className={styles.emptyState}>No matching map nodes.</p>
      </aside>
    );
  }

  return (
    <aside className={styles.detailPanel}>
      <span className={styles.detailKind}>{node.kind}</span>
      <Heading as="h2">{node.title}</Heading>
      <p>{node.summary}</p>
      <dl>
        <div>
          <dt>Path</dt>
          <dd>{node.path}</dd>
        </div>
        <div>
          <dt>Tags</dt>
          <dd>{node.tags.join(', ')}</dd>
        </div>
      </dl>
      <Link className={styles.sourceLink} to={githubUrl(node.path)}>
        Open source
      </Link>
    </aside>
  );
}

DetailPanel.propTypes = {
  node: mapNodeShape,
};

export default function RepoMap() {
  const [activePersona, setActivePersona] = useState('all');
  const [query, setQuery] = useState('');
  const [selectedId, setSelectedId] = useState(null);

  const normalizedQuery = normalize(query.trim());

  const filteredGroups = useMemo(
    () =>
      repoMap.groups
        .map((group) => ({
          ...group,
          nodes: group.nodes.filter(
            (node) =>
              matchesPersona(group, node, activePersona) &&
              matchesQuery(group, node, normalizedQuery),
          ),
        }))
        .filter((group) => group.nodes.length > 0),
    [activePersona, normalizedQuery],
  );

  const visibleNodes = filteredGroups.flatMap((group) => group.nodes);
  const selectedNode =
    visibleNodes.find((node) => node.id === selectedId) ?? visibleNodes[0] ?? null;

  return (
    <Layout
      title="Repo Map"
      description="Interactive SicarioSpec repository map generated from docs, presets, rules, control maps, examples, specs, and automation surfaces."
    >
      <main className={styles.page}>
        <section className={styles.headerBand}>
          <div className="container">
            <div className={styles.headerGrid}>
              <div>
                <p className={styles.kicker}>Repository intelligence</p>
                <Heading as="h1">Repo Map</Heading>
                <p className={styles.subtitle}>
                  A generated operating map for the SicarioSpec bundle. It connects
                  docs, presets, rule engine code, control maps, workflows, examples,
                  specs, and release surfaces around the way users actually enter the repo.
                </p>
              </div>
              <div className={styles.stats}>
                <div>
                  <strong>{repoMap.version}</strong>
                  <span>version</span>
                </div>
                <div>
                  <strong>{repoMap.summary.groups}</strong>
                  <span>branches</span>
                </div>
                <div>
                  <strong>{repoMap.summary.nodes}</strong>
                  <span>nodes</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className={styles.mapBand}>
          <div className="container">
            <div className={styles.controls}>
              <div className={styles.segmented} aria-label="Filter by audience">
                {repoMap.personas.map((persona) => (
                  <button
                    aria-pressed={activePersona === persona}
                    key={persona}
                    onClick={() => setActivePersona(persona)}
                    type="button"
                  >
                    {personaLabels[persona] ?? persona}
                  </button>
                ))}
              </div>
              <label className={styles.searchBox}>
                <span>Search</span>
                <input
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="rules, control maps, docs, release"
                  type="search"
                  value={query}
                />
              </label>
            </div>

            <div className={styles.mapLayout}>
              <div className={styles.rootNode}>
                <span>{repoMap.root.subtitle}</span>
                <strong>{repoMap.root.title}</strong>
                <small>{repoMap.root.path}</small>
              </div>

              <div className={styles.branchGrid}>
                {filteredGroups.map((group) => (
                  <Branch
                    group={group}
                    key={group.id}
                    onSelect={setSelectedId}
                    selectedId={selectedNode?.id}
                  />
                ))}
              </div>

              <DetailPanel node={selectedNode} />
            </div>

            <p className={styles.generatedBy}>
              Generated by <code>{repoMap.summary.generatedBy}</code>.
            </p>
          </div>
        </section>
      </main>
    </Layout>
  );
}
