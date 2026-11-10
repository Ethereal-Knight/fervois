/** Public file URL, including the GitHub Pages project base when the site is built for Pages. */
export function assetUrl(path: string): string {
  const base = import.meta.env.BASE_URL
  const prefix = base.endsWith('/') ? base : `${base}/`
  const file = path.replace(/^\.?\//, '')
  return `${prefix}${file}`
}
