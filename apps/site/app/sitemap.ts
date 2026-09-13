import type { MetadataRoute } from "next";
const routes = ["", "/demo", "/how-it-works", "/docs", "/docs/install", "/docs/security", "/docs/checkpoints", "/docs/integrations", "/changelog", "/privacy", "/terms", "/judges"];
export default function sitemap(): MetadataRoute.Sitemap { const base = process.env.NEXT_PUBLIC_SITE_URL ?? "https://dovet.site"; return routes.map((route) => ({ url: `${base}${route}`, changeFrequency: route === "" ? "weekly" : "monthly" })); }
