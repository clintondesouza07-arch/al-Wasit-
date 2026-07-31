#!/usr/bin/env node
/**
 * Weekly news refresh for the Al Wasit Machinery homepage.
 *
 * Pulls headlines from a curated list of GCC construction / infrastructure /
 * heavy-equipment news feeds, filters them for relevance, keeps the best ~7,
 * and writes them to news-data.json at the repo root. The homepage fetches
 * that file client-side (see the news carousel script in alwasit-website.html).
 *
 * Runs automatically every week via .github/workflows/update-news.yml, or
 * manually with:  node scripts/update-news.js
 *
 * Design goals:
 *  - Never break the site. If every feed fails, or too few relevant items
 *    are found, we leave the existing news-data.json alone and exit quietly
 *    rather than overwrite it with something empty/broken.
 *  - Keep editorial relevance. We filter by keyword instead of just taking
 *    "whatever is newest" from a generic feed, since Al Wasit cares about
 *    construction/infrastructure/heavy-equipment news specifically.
 */

import Parser from 'rss-parser';
import { writeFile, readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUTPUT_PATH = path.join(__dirname, '..', 'news-data.json');
const MAX_ITEMS = 7;

// Curated feeds. Add/remove sources here as needed — each is tried
// independently, so one bad/renamed feed URL won't take down the others.
const FEEDS = [
  { url: 'https://www.constructionweekonline.com/feed', sourceName: 'Construction Week ME', category: 'GCC · Construction' },
  { url: 'https://www.tradearabia.com/rss/CONS.xml', sourceName: 'Trade Arabia', category: 'GCC · Construction' },
  { url: 'https://www.arabianbusiness.com/feed', sourceName: 'Arabian Business', category: 'GCC · Business' },
  { url: 'https://www.thenationalnews.com/rss', sourceName: 'The National', category: 'UAE · News' },
  { url: 'https://gulfnews.com/rss?feed=constructionandproperty', sourceName: 'Gulf News', category: 'UAE · Construction' },
  { url: 'https://news.google.com/rss/search?q=%22heavy%20equipment%22%20OR%20%22construction%20machinery%22%20UAE%20OR%20GCC%20when:14d&hl=en-AE&gl=AE&ceid=AE:en', sourceName: 'Google News', category: 'GCC · Equipment' },
  { url: 'https://news.google.com/rss/search?q=infrastructure%20project%20Saudi%20OR%20Qatar%20OR%20UAE%20OR%20Oman%20when:14d&hl=en-AE&gl=AE&ceid=AE:en', sourceName: 'Google News', category: 'GCC · Infrastructure' }
];

// Only keep stories that actually relate to Al Wasit's world — construction,
// infrastructure, heavy equipment, and the region it serves.
const KEYWORDS = [
  'construction', 'infrastructure', 'machinery', 'equipment', 'excavator', 'bulldozer',
  'crane', 'loader', 'grader', 'compactor', 'earthworks', 'contractor', 'contract awarded',
  'project', 'mega-project', 'giga-project', 'rail', 'metro', 'port', 'logistics', 'expo',
  'vision 2030', 'vision 2040', 'gcc', 'uae', 'dubai', 'abu dhabi', 'sharjah', 'saudi',
  'riyadh', 'neom', 'qatar', 'doha', 'oman', 'muscat', 'bahrain', 'kuwait'
];

// Fallback stock images by category, used only when a feed item has no
// usable image of its own (most RSS feeds don't reliably provide one).
const FALLBACK_IMAGES = {
  'GCC · Construction': 'https://images.unsplash.com/photo-1541888946425-d81bb19240f5?w=900&q=80&auto=format&fit=crop',
  'GCC · Business': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=900&q=80&auto=format&fit=crop',
  'UAE · News': 'https://images.unsplash.com/photo-1503708928676-1cb796a0891e?w=900&q=80&auto=format&fit=crop',
  'UAE · Construction': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=900&q=80&auto=format&fit=crop',
  'GCC · Equipment': 'https://images.unsplash.com/photo-1590496793929-36417d3117de?w=900&q=80&auto=format&fit=crop',
  'GCC · Infrastructure': 'https://images.unsplash.com/photo-1494412651409-8963ce7935a7?w=900&q=80&auto=format&fit=crop',
  default: 'https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=900&q=80&auto=format&fit=crop'
};

function isRelevant(text) {
  const t = text.toLowerCase();
  return KEYWORDS.some((k) => t.includes(k));
}

function extractImage(item) {
  if (item.enclosure && item.enclosure.url) return item.enclosure.url;
  if (item['media:content'] && item['media:content'].$ && item['media:content'].$.url) {
    return item['media:content'].$.url;
  }
  if (item['media:thumbnail'] && item['media:thumbnail'].$ && item['media:thumbnail'].$.url) {
    return item['media:thumbnail'].$.url;
  }
  if (item.image && typeof item.image === 'string') return item.image;
  const match = /<img[^>]+src="([^"]+)"/i.exec(item['content:encoded'] || item.content || item.summary || '');
  return match ? match[1] : null;
}

function formatDate(pubDate) {
  const d = pubDate ? new Date(pubDate) : new Date();
  if (isNaN(d.getTime())) return '2026';
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}

async function fetchFeed(parser, feed) {
  try {
    const parsed = await parser.parseURL(feed.url);
    return (parsed.items || []).map((item) => ({
      date: formatDate(item.pubDate || item.isoDate),
      pubDate: item.pubDate || item.isoDate || null,
      source: feed.sourceName,
      category: feed.category,
      title: (item.title || '').trim(),
      summary: (item.contentSnippet || item.summary || '').trim().slice(0, 220),
      url: item.link || feed.url,
      image: extractImage(item) || FALLBACK_IMAGES[feed.category] || FALLBACK_IMAGES.default
    }));
  } catch (err) {
    console.warn(`[update-news] Feed failed, skipping: ${feed.url} (${err.message})`);
    return [];
  }
}

function dedupe(items) {
  const seen = new Set();
  return items.filter((item) => {
    const key = (item.title || '').toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 60);
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

async function main() {
  const parser = new Parser({ timeout: 15000 });
  const results = await Promise.all(FEEDS.map((f) => fetchFeed(parser, f)));
  let items = results.flat();

  items = items.filter((it) => it.title && isRelevant(`${it.title} ${it.summary}`));
  items = dedupe(items);
  items.sort((a, b) => new Date(b.pubDate || 0) - new Date(a.pubDate || 0));
  items = items.slice(0, MAX_ITEMS);

  if (items.length < 3) {
    console.warn(`[update-news] Only found ${items.length} relevant items — leaving news-data.json unchanged to avoid publishing a thin/broken update.`);
    return;
  }

  // Strip the internal pubDate field before writing (keep the JSON clean).
  const cleanItems = items.map(({ pubDate, ...rest }) => rest);

  const now = new Date();
  const output = {
    updatedAt: now.toISOString(),
    updatedLabel: `Last updated: ${now.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })} · Refreshes weekly`,
    items: cleanItems
  };

  await writeFile(OUTPUT_PATH, JSON.stringify(output, null, 2) + '\n', 'utf-8');
  console.log(`[update-news] Wrote ${cleanItems.length} items to news-data.json`);
}

main().catch((err) => {
  console.error('[update-news] Unexpected failure, leaving news-data.json unchanged:', err);
  process.exitCode = 0; // don't fail the workflow — just skip this week's update
});
