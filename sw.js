const CACHE_NAME = "vernaledger-shell-v3";
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
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
    );
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
        )
    );
    self.clients.claim();
});

self.addEventListener("fetch", (event) => {
    if (event.request.method !== "GET" || new URL(event.request.url).origin !== self.location.origin) return;
    if (new URL(event.request.url).pathname.startsWith("/api/")) return;
    event.respondWith(
        fetch(event.request).catch(() => caches.match(event.request).then((cached) => cached || caches.match("/")))
    );
});
