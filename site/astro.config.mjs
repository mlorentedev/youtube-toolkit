import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://mlorentedev.github.io',
  base: '/youtube-toolkit',
  integrations: [
    starlight({
      title: 'YouTube Toolkit',
      description:
        'A Python CLI for multi-channel YouTube analytics, engagement metrics, and transcript extraction.',
      favicon: '/favicon.svg',
      logo: {
        src: './src/assets/logo.svg',
      },
      customCss: ['./src/styles/custom.css'],
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/mlorentedev/youtube-toolkit',
        },
      ],
      head: [
        {
          tag: 'meta',
          attrs: {
            property: 'og:image',
            content: 'https://mlorentedev.github.io/youtube-toolkit/favicon.svg',
          },
        },
        {
          tag: 'meta',
          attrs: { name: 'twitter:card', content: 'summary' },
        },
      ],
      sidebar: [
        {
          label: 'Guides',
          items: [{ label: 'Getting Started', slug: 'getting-started' }],
        },
      ],
    }),
  ],
});
