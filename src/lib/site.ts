// Dados e utilitários compartilhados por todas as páginas.
import site from '../data/site.json';
import problemas from '../data/problemas.json';
import listas from '../data/listas.json';
import equipe from '../data/equipe.json';
import manifesto from '../../public/assets/img/imagens.json';

export { site, problemas, listas, equipe };
export const ROMANOS = listas.romanos;

export type Imagem = { img: string; alt: string };
export type Problema = (typeof problemas)[number];
export type Profissional = (typeof equipe)[number];

// Registro de conselho provisório (só zeros) não aparece no site.
export function registroValido(p: Profissional) {
  return /[1-9]/.test(p.registro);
}

export function profissional(id: string) {
  const p = equipe.find((x) => x.id === id);
  if (!p) throw new Error(`Profissional ${id} não está em equipe.json`);
  return p;
}

export const manifestoImagens: Record<string, { g: number[]; p: number[] }> = manifesto;

export function wa(msg: string = site.msgPadrao) {
  return `https://wa.me/${site.whats}?text=${encodeURIComponent(msg)}`;
}

export function doi(codigo: string) {
  return `https://doi.org/${codigo}`;
}

export function dataPorExtenso(data: Date) {
  return data.toLocaleDateString('pt-BR', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' });
}
