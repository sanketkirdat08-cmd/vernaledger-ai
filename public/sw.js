const CACHE_NAME = "vernaledger-shell-v9";
const APP_SHELL = [
    "/",
    "/index.html",
    "/style.css",
    "/app.js",
    "/manifest.webmanifest",
    "/icons/icon.svg",
    "/icons/icon-192.png",
    "/icons/icon-512.png",
    "/icons/apple-touch-icon.png"
];

self.addEventListener("install", (event) => {
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.map((key) => caches.delete(key)))
        )
    );
    self.clients.claim();
});

// Network-First strategy ensures desktop/laptop browsers always get the latest code
self.addEventListener("fetch", (event) => {
    if (event.request.method !== "GET" || new URL(event.request.url).origin !== self.location.origin) return;
    if (new URL(event.request.url).pathname.startsWith("/api/")) return;

    event.respondWith(
        fetch(event.request)
            .then((networkResponse) => {
                if (networkResponse && networkResponse.status === 200) {
                    const responseClone = networkResponse.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseClone));
                }
                return networkResponse;
            })
            .catch(() => caches.match(event.request).then((cached) => cached || caches.match("/")))
    );
});
