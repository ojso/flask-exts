const fs = require('fs').promises;
const fssync = require('fs');
const path = require('path');
const crypto = require('crypto');

// Root directory for vendored assets
const VENDOR_DIR = 'src/flask_exts/static/vendor';

// Cache file for hash results. Stored under node_modules/.cache so it is
// ignored by git and cleaned up together with node_modules.
const CACHE_FILE = path.join('node_modules', '.cache', 'vendor-hash.json');

// Configuration: target subdirectory -> { source file: destination filename }
const vendorConfig = {
  bootstrap5: {
    'node_modules/bootstrap/dist/css/bootstrap.min.css': 'bootstrap.min.css',
    'node_modules/bootstrap/dist/js/bootstrap.bundle.min.js': 'bootstrap.bundle.min.js',
  },
  clipboard: {
    'node_modules/clipboard/dist/clipboard.min.js': 'clipboard.min.js',
  },
  'tom-select': {
    'node_modules/tom-select/dist/css/tom-select.bootstrap5.min.css': 'tom-select.bootstrap5.min.css',
    'node_modules/tom-select/dist/js/tom-select.complete.min.js': 'tom-select.complete.min.js',
  },
  dayjs: {
    'node_modules/dayjs/dayjs.min.js': 'dayjs.min.js',
    'node_modules/dayjs/plugin/utc.js': 'utc.js',
    'node_modules/dayjs/plugin/timezone.js': 'timezone.js',
  },
  flatpickr: {
    'node_modules/flatpickr/dist/flatpickr.min.js': 'flatpickr.min.js',
    'node_modules/flatpickr/dist/flatpickr.min.css': 'flatpickr.min.css',
  },
};

// Statistics
let copiedCount = 0;
let skippedCount = 0;
let unchangedCount = 0;
let cacheHitCount = 0;
let cacheMissCount = 0;

// In-memory cache: absolute path -> { size, mtimeMs, hash }
let hashCache = {};

/**
 * Load the hash cache from disk. Missing or corrupted cache is treated as
 * empty; the script will simply recompute hashes for everything.
 */
async function loadCache() {
  try {
    const raw = await fs.readFile(CACHE_FILE, 'utf8');
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === 'object') {
      hashCache = parsed;
      console.log(`📦 Loaded hash cache: ${Object.keys(hashCache).length} entries`);
    }
  } catch {
    hashCache = {};
  }
}

/**
 * Persist the hash cache to disk.
 */
async function saveCache() {
  await fs.mkdir(path.dirname(CACHE_FILE), { recursive: true });
  await fs.writeFile(CACHE_FILE, JSON.stringify(hashCache), 'utf8');
}

/**
 * Compute SHA-256 hash of a file, using the cache when possible.
 *
 * Cache key is the absolute path. Cache entry stores size + mtimeMs so
 * that any change to the file (including touch, rename, reinstall) will
 * invalidate the entry and force a fresh hash. This is the standard
 * (path, size, mtime) strategy used by webpack, babel, eslint, etc.
 *
 * Why hashing with a cache is better than byte-by-byte comparison here:
 *   - A hash is a compact fingerprint that can be cached and reused
 *     across runs. Byte comparison cannot be cached; it must re-read
 *     both files every time.
 *   - Hash is independent of mtime/size semantics, so it is not fooled
 *     by same-size replacements or filesystem timestamp precision.
 *   - Hash can later be transmitted, stored in lockfiles, or compared
 *     against remote digests (ETag, npm integrity, CI artifacts) if
 *     the script ever needs that.
 */
async function hashFile(file) {
  const abs = path.resolve(file);

  let stat;
  try {
    stat = await fs.stat(abs);
  } catch {
    return null;
  }

  const cached = hashCache[abs];
  if (
    cached &&
    cached.size === stat.size &&
    cached.mtimeMs === stat.mtimeMs
  ) {
    cacheHitCount++;
    return cached.hash;
  }

  cacheMissCount++;
  const hash = await new Promise((resolve, reject) => {
    const h = crypto.createHash('sha256');
    const stream = fssync.createReadStream(abs);
    stream.on('data', chunk => h.update(chunk));
    stream.on('end', () => resolve(h.digest('hex')));
    stream.on('error', reject);
  });

  hashCache[abs] = { size: stat.size, mtimeMs: stat.mtimeMs, hash };
  return hash;
}

/**
 * Compare source and destination by SHA-256 hash.
 * Returns true if dest exists and both hashes match.
 */
async function isSameFile(src, dest) {
  const [srcHash, destHash] = await Promise.all([hashFile(src), hashFile(dest)]);
  if (srcHash === null || destHash === null) return false;
  return srcHash === destHash;
}

async function copyVendorFiles() {
  // Ensure node_modules exists
  try {
    await fs.access('node_modules');
  } catch {
    console.error('❌ node_modules not found. Please run `npm install` first.');
    process.exit(1);
  }

  await loadCache();

  for (const [subDir, files] of Object.entries(vendorConfig)) {
    const targetDir = path.join(VENDOR_DIR, subDir);
    await fs.mkdir(targetDir, { recursive: true });
    console.log(`📁 Ensured directory: ${targetDir}`);

    for (const [src, destName] of Object.entries(files)) {
      const dest = path.join(targetDir, destName);

      // Check source exists
      try {
        await fs.access(src);
      } catch {
        console.warn(`⚠️  Skipped (missing source): ${src}`);
        skippedCount++;
        continue;
      }

      // Skip copy if content hashes match
      if (await isSameFile(src, dest)) {
        console.log(`⏭️  Unchanged: ${dest}`);
        unchangedCount++;
        continue;
      }

      try {
        await fs.copyFile(src, dest);
        // Destination changed on disk, so drop its stale cache entry.
        // It will be recomputed lazily on the next run.
        delete hashCache[path.resolve(dest)];
        console.log(`✅ Copied: ${src} -> ${dest}`);
        copiedCount++;
      } catch (err) {
        console.error(`❌ Failed to copy ${src}:`, err.message);
        process.exitCode = 1;
      }
    }
  }

  await saveCache();

  console.log(
    `\n🎉 Done. Copied: ${copiedCount}, Unchanged: ${unchangedCount}, Skipped: ${skippedCount}`
  );
  console.log(
    `🧠 Hash cache: ${cacheHitCount} hits, ${cacheMissCount} misses`
  );
}

copyVendorFiles().catch(err => {
  console.error('Unexpected error:', err);
  process.exit(1);
});
