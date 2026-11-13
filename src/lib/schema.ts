// Dados estruturados (schema.org) que ligam Dra. Larissa Pessoa à Hair Zenith.
import { site, equipe, registroValido } from './site';

const SITE = site.url;
export const ORG_ID = SITE + '/#hairzenith';
export const LARISSA_ID = SITE + '/equipe/larissa-pessoa/#larissa';
export const THAINA_ID = SITE + '/equipe/#thaina';
export const JULIA_ID = SITE + '/equipe/#julia';

type Unidade = (typeof site.unidades)[number];

function endereco(u: Unidade) {
  return { '@type': 'PostalAddress', streetAddress: u.rua, addressLocality: u.cidade, addressRegion: 'RJ', addressCountry: 'BR' };
}

export function schemaOrg() {
  return {
    '@type': 'MedicalClinic',
    '@id': ORG_ID,
    name: 'Hair Zenith',
    alternateName: ['Larissa Pessoa Tricologia Integrativa', 'Dra. Larissa Pessoa Tricologia', 'Clínica Larissa Pessoa'],
    description:
      'Clínica de tricologia especializada em queda de cabelo, calvície e perda de densidade capilar, fundada pela Dra. Larissa Pessoa. Nova clínica em construção, com inauguração prevista para março de 2027.',
    url: SITE + '/',
    logo: SITE + '/icone-512.png',
    image: SITE + '/assets/img/og-hairzenith.jpg',
    telephone: '+55-21-97278-0789',
    email: site.email,
    address: endereco(site.unidades[0]),
    areaServed: ['Rio de Janeiro', 'Cabo Frio', 'Região dos Lagos'],
    founder: { '@id': LARISSA_ID },
    employee: [{ '@id': LARISSA_ID }, { '@id': THAINA_ID }, { '@id': JULIA_ID }],
    knowsAbout: ['Tricologia', 'Queda de cabelo', 'Calvície feminina', 'Calvície masculina', 'Alopecia androgenética', 'Afinamento dos fios', 'Perda de densidade capilar', 'Tricoscopia'],
    sameAs: [site.instagram, site.siteAntigo],
    department: site.unidades.map((u) => ({
      '@type': 'MedicalClinic',
      name: `Hair Zenith ${u.nome}`,
      address: endereco(u),
      telephone: '+55-21-97278-0789',
      geo: { '@type': 'GeoCoordinates', latitude: u.lat, longitude: u.lon },
      hasMap: u.mapa,
    })),
  };
}

export function schemaLarissa() {
  return {
    '@type': 'Person',
    '@id': LARISSA_ID,
    name: 'Larissa Pessoa',
    alternateName: ['Dra. Larissa Pessoa', 'Larissa Mota Barros Pessoa'],
    jobTitle: 'Fundadora, CEO e tricologista',
    description: 'Tricologista especializada em queda de cabelo e calvície, fundadora e CEO da Hair Zenith.',
    worksFor: { '@id': ORG_ID },
    url: SITE + '/equipe/larissa-pessoa/',
    image: SITE + '/assets/img/larissa-blazer.jpg',
    knowsAbout: ['Tricologia', 'Alopecia androgenética', 'Queda de cabelo', 'Calvície'],
    sameAs: [site.instagram, site.siteAntigo],
  };
}

export function schemaArtigos() {
  return site.artigos.map((a) => ({
    '@type': 'ScholarlyArticle',
    headline: a.titulo,
    datePublished: a.data,
    sameAs: 'https://doi.org/' + a.doi,
    url: a.url,
    isPartOf: { '@type': 'Periodical', name: 'Brazilian Journal of Hair Health' },
    author: a.autores.map((n) =>
      n.includes('Larissa') ? { '@id': LARISSA_ID } : n.includes('Thaina') ? { '@id': THAINA_ID } : { '@type': 'Person', name: n },
    ),
  }));
}

export function schemaEquipe() {
  return equipe.map((p) => {
    const unidade = site.unidades.find((u) => u.id === p.unidade)!;
    return {
      '@type': 'Person',
      '@id': `${SITE}/equipe/#${p.id}`,
      name: p.nome,
      honorificPrefix: p.tratamento,
      jobTitle: 'Tricologista',
      description: p.texto,
      worksFor: { '@id': ORG_ID },
      workLocation: { '@type': 'Place', name: `Hair Zenith ${unidade.nome}`, address: endereco(unidade) },
      url: `${SITE}/equipe/#${p.id}`,
      ...(registroValido(p) && {
        hasCredential: { '@type': 'EducationalOccupationalCredential', credentialCategory: 'Registro profissional', name: `${p.conselho} ${p.registro}` },
      }),
    };
  });
}

export function migalhas(itens: [string, string][]) {
  return {
    '@type': 'BreadcrumbList',
    itemListElement: itens.map(([name, caminho], i) => ({ '@type': 'ListItem', position: i + 1, name, item: SITE + caminho })),
  };
}
