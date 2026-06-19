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
          { to: '/docs/presets', label: 'Docs', position: 'left' },
          { href: 'https://github.com/dfirs1car1o/sicario-spec', label: 'GitHub', position: 'right' },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              { label: 'Presets', to: '/docs/presets' },
              { label: 'Agent environments', to: '/docs/agent-environments' },
              { label: 'Release process', to: '/docs/release-process' },
            ],
          },
          {
            title: 'Project',
            items: [
              { label: 'GitHub', href: 'https://github.com/dfirs1car1o/sicario-spec' },
              { label: 'Issues', href: 'https://github.com/dfirs1car1o/sicario-spec/issues' },
              { label: 'Security', href: 'https://github.com/dfirs1car1o/sicario-spec/security/policy' },
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
