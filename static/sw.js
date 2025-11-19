const CACHE_NAME = 'morgobyte-v0.2';
const urlsToCache = [
  // Note: Not caching '/' because it has server-injected config that must stay fresh
  // Note: app.html is cached but uses network-first strategy to always get latest version
  '/static/app.html',
  '/static/setup-local.html',
  '/static/fonts/pixelfont.ttf',
  '/static/fonts/Comfortaa-Regular.ttf',
  '/static/images/logo1.png',
  '/static/images/logo_transparent_192.png',
  '/static/images/logo_transparent_512.png',
  '/static/images/favicon_64.png',
  '/static/manifest.json',
  '/static/css/fontawesome.min.css',
  '/static/css/solid.css',
  '/static/webfonts/fa-solid-900.woff2',
];

// Install service worker and cache all resources
self.addEventListener('install', event => {
  console.log('[SW] Service Worker installing...');
  self.clients.matchAll().then(clients => {
    clients.forEach(client => client.postMessage({type: 'SW_INSTALLING', version: CACHE_NAME}));
  });
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[SW] Opened cache, adding all URLs');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('[SW] All resources cached');
        return self.skipWaiting(); // Activate immediately
      })
      .catch(error => {
        console.error('[SW] Cache installation failed:', error);
      })
  );
});

// Cache and return requests
self.addEventListener('fetch', event => {
  // For navigation requests (loading the page), use network-first strategy
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Clone and cache the fresh response for offline use
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });
          console.log('[SW] Served from network and cached (navigate):', event.request.url);
          return response;
        })
        .catch(() => {
          // Network failed - try cache
          console.log('[SW] Network failed, trying cache for:', event.request.url);
          return caches.match(event.request).then(cachedResponse => {
            if (cachedResponse) {
              console.log('[SW] Serving from cache (offline):', event.request.url);
              return cachedResponse;
            }
            // No cache - return error page or static app.html
            console.log('[SW] No cache found, serving app.html');
            return caches.match('/static/app.html');
          });
        })
    );
    return;
  }

  // For app.html specifically, ALWAYS use network-first to get latest version
  if (event.request.url.includes('/static/app.html') || 
      event.request.url.includes('/static/setup-local.html') ||
      event.request.url.includes('/static/setup-server.html')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Cache the fresh version
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });
          console.log('[SW] Served fresh app.html from network');
          return response;
        })
        .catch(() => {
          // Network failed - use cached version
          console.log('[SW] Network failed for app.html, using cache');
          return caches.match(event.request);
        })
    );
    return;
  }

  // For all other requests, cache first, then network
  event.respondWith(
    (async () => {
      // Don't intercept API requests or AWS S3 audio files - let them pass through directly
      if (event.request.url.includes('/api/') || 
          event.request.url.includes('yoto-card-api-prod-media.s3.')) {
        console.log('[SW] Passing through request (bypassing cache):', event.request.url);
        return fetch(event.request);
      }

      // Check cache for non-API requests
      const cachedResponse = await caches.match(event.request);
      if (cachedResponse) {
        console.log('[SW] Cache hit for:', event.request.url);
        return cachedResponse;
      }

      // Not in cache - try to fetch
      console.log('[SW] Cache miss for:', event.request.url);
      
      // For cross-origin requests, use no-cors mode to allow caching
      const fetchOptions = event.request.url.startsWith(self.location.origin) 
        ? {} 
        : { mode: 'no-cors' };
      
      return fetch(event.request, fetchOptions).then(
          response => {
            // Check if valid response
            if (!response || response.status !== 200) {
              console.log('[SW] Invalid response for:', event.request.url, 'Status:', response?.status);
              return response;
            }

            // Cache images from CDNs (Yoto cover images and card content)
            const shouldCache = 
              event.request.url.includes('cdn.yoto.io') ||
              event.request.url.includes('card-content.yotoplay.com') ||
              event.request.destination === 'image' ||
              event.request.destination === 'font' ||
              event.request.destination === 'style' ||
              event.request.destination === 'script';

            if (shouldCache) {
              console.log('[SW] Should cache:', event.request.url, 'Type:', response.type);
              // Clone the response
              const responseToCache = response.clone();

              caches.open(CACHE_NAME)
                .then(cache => {
                  console.log('[SW] Caching resource:', event.request.url);
                  return cache.put(event.request, responseToCache);
                })
                .then(() => {
                  console.log('[SW] Successfully cached:', event.request.url);
                })
                .catch(error => {
                  console.error('[SW] Failed to cache:', event.request.url, error);
                });
            } else {
              console.log('[SW] Not caching:', event.request.url);
            }

            return response;
          }
        ).catch(error => {
          console.error('[SW] Fetch failed for:', event.request.url, error);
          // For images, return a placeholder
          if (event.request.destination === 'image') {
            return new Response('', { status: 404, statusText: 'Not Found' });
          }
          // For HTML requests, return cached app
          if (event.request.destination === 'document') {
            return caches.match('/static/app.html');
          }
          throw error;
        });
    })()
  );
});

// Update service worker
self.addEventListener('activate', event => {
  console.log('[SW] Service Worker activating...');
  self.clients.matchAll().then(clients => {
    clients.forEach(client => client.postMessage({type: 'SW_ACTIVATED', version: CACHE_NAME}));
  });
  
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            console.log('[SW] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('[SW] Service Worker activated');
      return self.clients.claim(); // Take control immediately
    })
  );
});

// Listen for messages from the app
self.addEventListener('message', event => {
  console.log('[SW] Received message:', event.data);
  if (event.data && event.data.type === 'SKIP_WAITING') {
    console.log('[SW] Skipping waiting...');
    self.skipWaiting();
  }
});
