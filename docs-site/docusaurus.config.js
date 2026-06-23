// @ts-check

const lightCodeTheme = require('prism-react-renderer').themes.github;
const darkCodeTheme = require('prism-react-renderer').themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'SicarioSpec',
  tagline: 'Kill risk before it ships.',
  favicon: 'img/sicario-spec-mark.svg',
  url: 'https://dfirs1car1o.github.io',
  baseUrl: '/sicario-spec/',
  organizationName: 'dfirs1car1o',
  projectName: 'sicario-spec',
  onBrokenLinks: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },
  trailingSlash: false,

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          path: '../docs',
          routeBasePath: 'docs',
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/dfirs1car1o/sicario-spec/edit/main/docs/',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/sicario-spec-mark.svg',
      navbar: {
        title: 'SicarioSpec',
        logo: {
          alt: 'SicarioSpec mark',
          src: 'img/sicario-spec-mark.svg',
        },
        items: [
          { to: '/', label: 'Overview', position: 'left' },
          { to: '/docs/getting-started', label: 'Start Here', position: 'left' },
          { to: '/docs/presets', label: 'Presets', position: 'left' },
          { to: '/docs/security-model', label: 'Security Model', position: 'left' },
          { to: '/docs/control-maps', label: 'Control Maps', position: 'left' },
          { href: 'https://github.com/dfirs1car1o/sicario-spec', label: 'GitHub', position: 'right' },
        ],
      },
      colorMode: {
        defaultMode: 'dark',
        disableSwitch: false,
        respectPrefersColorScheme: false,
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              { label: 'Getting started', to: '/docs/getting-started' },
              { label: 'Presets', to: '/docs/presets' },
              { label: 'Security model', to: '/docs/security-model' },
              { label: 'Control maps', to: '/docs/control-maps' },
              { label: 'Release process', to: '/docs/release-process' },
            ],
          },
          {
            title: 'Profiles',
            items: [
              { label: 'Cloud / IaC', to: '/docs/cloud-iac' },
              { label: 'Agent environments', to: '/docs/agent-environments' },
              { label: 'Agent fleet', to: '/docs/agent-fleet' },
              { label: 'OpenSSF', to: '/docs/openssf' },
              { label: 'Completeness matrix', to: '/docs/completeness-matrix' },
            ],
          },
          {
            title: 'Project',
            items: [
              { label: 'GitHub', href: 'https://github.com/dfirs1car1o/sicario-spec' },
              { label: 'Issues', href: 'https://github.com/dfirs1car1o/sicario-spec/issues' },
              { label: 'Security', href: 'https://github.com/dfirs1car1o/sicario-spec/security/policy' },
              { label: 'Changelog', to: '/docs/release-process' },
            ],
          },
        ],
        copyright: `Copyright ${new Date().getFullYear()} SicarioSpec contributors.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
      },
    }),
};

module.exports = config;
