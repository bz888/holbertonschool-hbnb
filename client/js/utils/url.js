export function getQueryParameter(name) {
    return new URLSearchParams(window.location.search).get(name);
}

export function getCurrentPageDestination() {
    const page = window.location.pathname.split('/').pop() || 'index.html';
    return `${page}${window.location.search}`;
}

export function getSafeLocalDestination(
    destination,
    fallback = 'index.html'
) {
    if (
        !destination
        || destination.startsWith('/')
        || destination.includes('..')
        || !/^[a-z0-9_-]+\.html(?:\?[^#]*)?(?:#.*)?$/i.test(destination)
    ) {
        return fallback;
    }

    return destination;
}
