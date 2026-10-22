// Self-cleaning Service Worker: cleans up all legacy caches and unregisters
self.addEventListener("install", (event) => {
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) => Promise.all(keys.map((key) => caches.delete(key))))
            .then(() => self.registration.unregister())
            .then(() => self.clients.matchAll({ type: "window" }))
            .then((clients) => {
                for (const client of clients) {
                    client.navigate(client.url);
                }
            })
    );
    self.clients.claim();
});

self.addEventListener("fetch", (event) => {
    // Pure network pass-through, absolutely no caching
    event.respondWith(fetch(event.request));
});
